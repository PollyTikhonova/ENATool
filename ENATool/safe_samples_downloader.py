"""
FASTQ File Downloader for ENA

This module handles the download and verification of FASTQ files from ENA.
Downloads FASTQ files directly from ENA FTP servers using HTTP
"""

import os
import pandas as pd
import requests
from time import sleep
import hashlib
# import gzip

# Handle tqdm for both notebook and regular environments
try:
    _in_ipython_session = __IPYTHON__
    from tqdm import tqdm_notebook as tq
except NameError:
    from tqdm import tqdm as tq

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """Exception raised for errors in the input."""
    def __init__(self, message):
        self.message = message


class InfoError(Error):
    """Exception raised for errors in the input."""
    def __init__(self, message):
        self.message = message


def verify_md5(filepath, expected_md5):
    """Verify MD5 checksum of downloaded file."""
    if expected_md5 is None or pd.isna(expected_md5):
        return True
    
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    
    calculated_md5 = md5_hash.hexdigest()
    return calculated_md5 == expected_md5


def download_file_from_url(url, destination_path, md5sum=None, max_retries=3, keep_failed=False):
    """
    Download a file from URL with progress bar and MD5 verification.
    
    Args:
        url: FTP or HTTP URL to download from
        destination_path: Local path to save file
        md5sum: Expected MD5 checksum (optional)
        max_retries: Number of download attempts
        keep_failed (bool, optional): If True, does not remove the FASTQ files, 
            that downloaded with errors (failed md5 checksum).
            Defaults to False.
    
    Returns:
        str: 'OK', 'Error', or 'Exists'
    """
    # Check if file already exists and is valid
    if os.path.exists(destination_path):
        if md5sum and not pd.isna(md5sum):
            if verify_md5(destination_path, md5sum):
                return 'Exists'
            elif keep_failed:
                print(f"Existing file has incorrect MD5: {os.path.basename(destination_path)}")
                return 'Error'
            else:
                print(f"Existing file has incorrect MD5, re-downloading: {os.path.basename(destination_path)}")
        else:
            return 'Exists'
    
    # Create directory if needed
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    
    # Convert FTP to HTTP (ENA supports both)
    if url.startswith('ftp://'):
        url = url.replace('ftp://', 'https://')
    if url.startswith('http://'):
        url = url.replace('http://', 'https://')
    if 'https://' not in url:
        url = 'https://'+url
    
    # Try downloading with retries
    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                        size = f.write(chunk)
            
            # Verify MD5 if provided
            if md5sum and not pd.isna(md5sum):
                if verify_md5(destination_path, md5sum):
                    return 'OK'
                else:
                    if keep_failed:
                        print(f"MD5 mismatch for {os.path.basename(destination_path)}")
                        return 'Error'
                    else:
                        print(f"MD5 mismatch for {os.path.basename(destination_path)}, retrying...")
                        os.remove(destination_path)
                        if attempt < max_retries - 1:
                            sleep(2)
                            continue
                        else:
                            return 'Error'
            
            return 'OK'
            
        except requests.exceptions.RequestException as e:
            print(f"Download attempt {attempt + 1}/{max_retries} failed: {e}")
            if os.path.exists(destination_path):
                os.remove(destination_path)
            
            if attempt < max_retries - 1:
                sleep(5)
            else:
                return 'Error'
        
        except Exception as e:
            print(f"Unexpected error downloading {url}: {e}")
            if os.path.exists(destination_path):
                os.remove(destination_path)
            return 'Error'
    
    return 'Error'


def download_and_check_data(project_id, accession, destination_paths, 
                            ftp_urls=None, md5sums=None, keep_failed=False):
    """
    Download files directly from ENA FTP servers.
    
    Args:
        project_id: Project identifier
        accession: Run accession (e.g., SRR3997915)
        destination_paths: Single path (str) or list of destination file paths
        ftp_urls: Single URL (str) or semicolon-separated URLs or list
        md5sums: Single checksum (str) or semicolon-separated checksums or list
        keep_failed (bool, optional): If True, does not remove the FASTQ files, 
            that downloaded with errors (failed md5 checksum).
            Defaults to False.
    
    Returns:
        str or list: Download status for each file (str if 1 file, list if 2+ files)
    """
    if ftp_urls is None or pd.isna(ftp_urls):
        return None
    
    # Convert strings to lists of length one if needed
    if isinstance(ftp_urls, str):
        if ';' in ftp_urls:
            ftp_urls = ftp_urls.split(';')
        else:
            ftp_urls = [ftp_urls]
            destination_paths = [destination_paths] if isinstance(destination_paths, str) else destination_paths
            md5sums = [md5sums] if isinstance(md5sums, str) else [None]
    
    # Ensure destination_paths is a list
    if not isinstance(destination_paths, list):
        destination_paths = [destination_paths]
    
    # Parse MD5 checksums
    if md5sums and not pd.isna(md5sums):
        if isinstance(md5sums, str):
            md5sums = md5sums.split(';')
    else:
        md5sums = [None] * len(ftp_urls)
    
    # Download each file
    statuses = []
    for dest_path, ftp_url, md5sum in zip(destination_paths, ftp_urls, md5sums):
        status = download_file_from_url(ftp_url, dest_path, md5sum, keep_failed=keep_failed)
        statuses.append(status)
    
    # Return single status if 1 file, list if 2+ files
    if len(statuses) == 1:
        return statuses[0]
    else:
        return statuses


def download_samples(project_id, ena_sample_info_table=None, downoad_info_table=None, 
                     destination_folder=None, keep_failed=False, NO_PROGRESS_BAR=False):
    """
    Download samples using direct FTP URLs.
    
    Args:
        project_id: ENA project accession (e.g., PRJNA335681)
        ena_sample_info_table: DataFrame from get_samples_info_by_ena_prj_name
                              Must have: 'sample_accession', 'run_accession', 'fastq_ftp', 'fastq_md5'
        downoad_info_table: Pre-formatted download table (overrides ena_sample_info_table)
        destination_folder: Where to save files (default: ./{project_id}/raw_reads)
        keep_failed (bool, optional): If True, does not remove the FASTQ files, 
            that downloaded with errors (failed md5 checksum).
            Defaults to False.
        NO_PROGRESS_BAR (bool, optional): If True, disables a progress bar. 
            Defaults to False.
    
    Returns:
        DataFrame: Download status table with columns:
                  ['sample_name', 'accession', 'filepath', 'ftp_urls', 'md5sums', 'download_status']
    """
    if destination_folder is None:
        destination_folder = f"{os.getcwd()}/{project_id}/raw_reads"
    else:
        destination_folder = f'{destination_folder}/raw_reads'
    
    if (downoad_info_table is None) and (ena_sample_info_table is not None):
        # Build download table from ENA sample info
        downoad_info_table = pd.DataFrame(
            columns=['sample_name', 'accession', 'filepath', 'ftp_urls', 'md5sums', 'n']
        )
        
        required_cols = ['sample_accession', 'run_accession', 'fastq_ftp']
        if not all(col in ena_sample_info_table.columns for col in required_cols):
            raise InputError(f"ena_sample_info_table must contain columns: {required_cols}")
        
        # Check for MD5 column
        md5_col = 'fastq_md5' if 'fastq_md5' in ena_sample_info_table.columns else None
        
        for idx, row in ena_sample_info_table.iterrows():
            name = row['sample_accession']
            accession = row['run_accession']
            fastq_ftp = row['fastq_ftp']
            fastq_md5 = row[md5_col] if md5_col else None
            
            if pd.isna(fastq_ftp):
                destination_file = None
                ftp_urls = None
                md5sums = None
            else:
                # Check if multiple files (paired-end)
                if ';' in fastq_ftp:
                    # Multiple files - keep as list
                    links = fastq_ftp.split(';')
                    destination_file = [
                        f'{destination_folder}/{accession}/{link.split("/")[-1]}' 
                        for link in links
                    ]
                    n = 2
                else:
                    # Single file - keep as string
                    destination_file = f'{destination_folder}/{accession}/{fastq_ftp.split("/")[-1]}'
                    n = 1

                ftp_urls = fastq_ftp
                md5sums = fastq_md5
            
            downoad_info_table.loc[len(downoad_info_table)] = [
                name, accession, destination_file, ftp_urls, md5sums, n
            ]
        
        # Save download info table
        os.makedirs(os.path.dirname(destination_folder), exist_ok=True)
        downoad_info_table.to_csv(
            f'{os.path.dirname(destination_folder)}/download_info_table.csv',
            index=False, sep='\t'
        )
    
    elif (downoad_info_table is None) and (ena_sample_info_table is None):
        raise InputError('You must provide either ena_sample_info_table or downoad_info_table')
    
    # Download all files
    download_status = []
    
    for idx, row in tq(downoad_info_table.iterrows(),
                      desc='Downloading FASTQ files',
                      total=len(downoad_info_table),
                      disable=NO_PROGRESS_BAR):
        accession = row['accession']
        destination_path = row['filepath']
        ftp_urls = row.get('ftp_urls', None)
        md5sums = row.get('md5sums', None)
        
        if len(destination_path) == 0:
            status = None
        else:
            # Pass data as-is (string for single file, list for multiple)
            status = download_and_check_data(
                project_id, accession, destination_path, ftp_urls, md5sums, keep_failed
            )
        
        download_status.append(status)
    
    downoad_info_table['download_status'] = download_status
    
    # Save final status
    downoad_info_table.to_csv(
        f'{os.path.dirname(destination_folder)}/download_info_table.csv',
        index=False, sep='\t'
    )
    
    return downoad_info_table


def get_download_summary(download_table: pd.DataFrame) -> dict:
    """
    Get summary statistics for download results.
    
    Args:
        download_table: DataFrame with download_status column
    
    Returns:
        Dictionary with download statistics
    
    Example:
        >>> summary = get_download_summary(download_table)
        >>> print(f"Success: {summary['successful']}/{summary['total']}")
    """
    if 'download_status' not in download_table.columns:
        return {'error': 'No download_status column found'}
    
    counts_table = []
    for value in download_table['download_status'].values:
        if type(value) == list:
            counts_table.extend(value)
        elif type(value) == str:
            counts_table.extend([value])
    counts_table = pd.DataFrame({'download_status':counts_table})
    
    status_counts = counts_table['download_status'].value_counts()

    return {
        'total': download_table['n'].sum(),
        'successful': status_counts.get('OK', 0),
        'already_existed': status_counts.get('Exists', 0),
        'failed': status_counts.get('Error', 0),
        'not_attempted': download_table['download_status'].isna().sum()
    }

