"""
ENATool - European Nucleotide Archive Data Management Tool

A comprehensive Python package for extracting metadata and downloading raw sequencing
files from the European Nucleotide Archive (ENA).

Features:
- Extract sample metadata from ENA projects
- Download FASTQ files with verification
- Generate interactive HTML reports
- Automatic fallback to NCBI BioSample
- Progress tracking for all operations

Example:
    >>> import ENATool
    >>> 
    >>> # Get sample information
    >>> info_table = ENATool.fetch('PRJNA335681', path='my_project')
    >>> 
    >>> # Download FASTQ files
    >>> download_table = info_table.ena.download()
"""

__version__ = "2.0.0"
__author__ = "P.Tikhonova"
__email__ = "tikhonova.polly@mail.ru"

from .extract_samples_info import get_samples_info_by_ena_prj_name
from .safe_samples_downloader import download_samples
from .api_urls import (
    get_ena_filereport_url,
    get_ena_sample_xml_url,
    get_ncbi_biosample_url
)

import pandas as pd
import os


@pd.api.extensions.register_dataframe_accessor("ena")
class ENATool:
    """
    Pandas DataFrame accessor for ENA operations.
    
    Adds `.ena` accessor to DataFrames for easy access to ENA-specific
    functionality like downloading FASTQ files.
    
    Attributes:
        id (str): Project accession ID
        path (str): Path to project directory
        table_type (str): Type of table ('raw' or 'ready')
    """
    
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self.table_type = None
        
        # Detect table type based on columns
        if all(column in self._obj.columns for column in 
               ['sample_accession', 'run_accession', 'fastq_ftp']):
            self.table_type = 'raw'
        if all(column in self._obj.columns for column in 
               ['sample_name', 'accession', 'filepath', 'number_of_files']):
            self.table_type = 'ready'
        
        self.id = None
        self.path = None
     
    def download(self, keep_failed, NO_PROGRESS_BAR):
        """
        Download FASTQ files for samples in the DataFrame.
        
        Returns:
            DataFrame with download status for each sample
            
        Raises:
            ValueError: If project ID is not set or table type is invalid
            
        Example:
            >>> info_table = ENATool.fetch('PRJNA335681')
            >>> download_table = info_table.ena.download()
        """
        if self.id is None:
            raise ValueError(
                'DataFrame.ena.id is None. Please set it:\n'
                '  table.ena.id = "PRJNA335681"\n'
                '  table.ena.path = "path/to/project"\n'
                'or reinitialize from existing table:\n'
                '  new_table.ena.reinit(old_table)'
            )
        
        if self.table_type == 'raw':
            report_table = download_samples(
                self.id,
                ena_sample_info_table=self._obj,
                destination_folder=self.path, 
                keep_failed=keep_failed,
                NO_PROGRESS_BAR=NO_PROGRESS_BAR
            )
            report_table.ena.id = self.id
            report_table.ena.path = self.path
            return report_table
        
        if self.table_type == 'ready':
            report_table = download_samples(
                self.id,
                downoad_info_table=self._obj,
                destination_folder=self.path,
                keep_failed=keep_failed,
                NO_PROGRESS_BAR=NO_PROGRESS_BAR
            )
            report_table.ena.id = self.id
            report_table.ena.path = self.path
            return report_table
        
        raise ValueError('Unable to detect table type. Check column names.')
            
    def reinit(self, obj):
        """
        Reinitialize ENA tool features from another DataFrame.
        
        Args:
            obj: DataFrame with existing ena.id and ena.path attributes
            
        Example:
            >>> filtered_table = original_table[original_table['organism'] == 'human']
            >>> filtered_table.ena.reinit(original_table)
        """
        self.id = obj.ena.id
        self.path = obj.ena.path


def fetch(project_id, path=None, download=False, keep_failed=False,  NO_PROGRESS_BAR=False):
    """
    Fetch all metadata from ENA for a project and optionally download raw files.
    
    This is the main entry point for ENATool. It retrieves comprehensive
    metadata for all samples in an ENA project and can automatically download
    the associated FASTQ files.
    
    Args:
        project_id (str): ENA project accession (e.g., 'PRJNA335681')
        path (str, optional): Directory for storing data. Defaults to project_id.
        download (bool, optional): If True, automatically download FASTQ files.
            Defaults to False.
        keep_failed (bool, optional): If True, does not remove the FASTQ files, 
            that downloaded with errors (failed md5 checksum).
            Defaults to False.
        NO_PROGRESS_BAR (bool, optional): If True, disables a progress bar. 
            Defaults to False.
    
    Returns:
        DataFrame or tuple: 
            - If download=False: Returns info_table DataFrame
            - If download=True: Returns (info_table, download_table) tuple
    
    Example:
        >>> # Just get metadata
        >>> info = ENATool.fetch('PRJNA335681')
        >>> print(f"Found {len(info)} samples")
        >>> 
        >>> # Get metadata and download files
        >>> info, downloads = ENATool.fetch('PRJNA335681', download=True)
        >>> print(downloads['download_status'].value_counts())
    """
    if path is None:
        path = project_id
    
    path = os.path.abspath(path)
    
    # Get sample information
    info_table = get_samples_info_by_ena_prj_name(project_id, path, NO_PROGRESS_BAR=NO_PROGRESS_BAR)
    info_table.ena.id = project_id
    info_table.ena.path = path
    
    if download:
        download_table = info_table.ena.download(keep_failed, NO_PROGRESS_BAR)
        return info_table, download_table
    
    return info_table


# Convenience exports
__all__ = [
    'fetch',
    'ENATool',
    'get_samples_info_by_ena_prj_name',
    'download_samples',
    'get_ena_filereport_url',
    'get_ena_sample_xml_url',
    'get_ncbi_biosample_url',
]
