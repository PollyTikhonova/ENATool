"""
ENA Sample Information Extractor

This module provides tools to extract and parse sample information from the
European Nucleotide Archive (ENA) by project name. It downloads metadata,
parses XML files, and generates interactive HTML tables.

Example usage:
    folder = 'xml_files'
    samples_table = get_samples_info_by_ena_prj_name('PRJNA335681', folder=folder)
"""

import os
import shutil
import pandas as pd
import numpy as np
import requests
import xmltodict
from typing import List, Union, Tuple, Optional

# Handle tqdm for both notebook and regular environments
try:
    _in_ipython_session = __IPYTHON__
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm

from .html_templates import generate_html_report
from .api_urls import (
    get_ena_filereport_url,
    get_ena_sample_xml_url,
    get_ncbi_biosample_url
)


def download_samples_file(prj_name: str, folder: str = '') -> pd.DataFrame:
    """
    Download sample information file from ENA for a given project.
    
    Args:
        prj_name: ENA project accession (e.g., 'PRJNA335681')
        folder: Directory to save the downloaded file
        
    Returns:
        DataFrame containing sample information
    """
    url = get_ena_filereport_url(prj_name)
    return pd.read_csv(url, sep='\t')


def download_file(url: str, filename: Optional[str] = None, folder: str = '') -> str:
    """
    Download a file from a URL and save it locally.
    
    Args:
        url: URL to download from
        filename: Optional custom filename
        folder: Directory to save the file
        
    Returns:
        Path to the downloaded file
    """
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    
    if filename is None:
        filename = url.split('/')[-1].replace('?download=true', '') + '.xml'
    
    # Construct filepath
    if folder:
        filepath = os.path.join(folder, 'xml_files', filename)
    else:
        filepath = os.path.join('xml_files', filename)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'wb') as f:
        f.write(response.content)
    
    return filepath


def cleanup_xml_files(folder: str = '') -> bool:
    """
    Remove the xml_files directory and all its contents.
    
    Args:
        folder: Parent directory containing xml_files folder
        
    Returns:
        True if cleanup was successful, False otherwise
    """
    if folder:
        xml_folder = os.path.join(folder, 'xml_files')
    else:
        xml_folder = 'xml_files'
    
    try:
        if os.path.exists(xml_folder) and os.path.isdir(xml_folder):
            shutil.rmtree(xml_folder)
            print(f"Successfully removed {xml_folder}")
            return True
        else:
            print(f"Directory {xml_folder} does not exist")
            return False
    except Exception as e:
        print(f"Error removing {xml_folder}: {e}")
        return False


def parse_values(parent_key: str, values: Union[dict, str]) -> dict:
    """
    Parse nested values from XML structure into flat dictionary.
    
    Args:
        parent_key: Parent key for nested structure
        values: Dictionary or string value to parse
        
    Returns:
        Flattened dictionary with composite keys
    """
    result = {}
    
    if isinstance(values, dict):
        for key, value in values.items():
            key = key.replace('@', '').replace('#', '')
            result[f'{parent_key}__{key}'] = value
    else:
        result[parent_key] = values
    
    return result


def parse_ena_sample_table(filename: str) -> pd.DataFrame:
    """
    Parse ENA sample XML file into a DataFrame.
    
    Args:
        filename: Path to XML file
        
    Returns:
        DataFrame with parsed sample metadata
    """
    with open(filename, 'r') as f:
        metadata_dict = xmltodict.parse(f.read())
    
    metadata_dict = metadata_dict['SAMPLE_SET']['SAMPLE']
    metadata_df = {}
    
    # Parse identifiers and sample name
    for root_key in ['IDENTIFIERS', 'SAMPLE_NAME']:
        if root_key in metadata_dict:
            for key, values in metadata_dict[root_key].items():
                metadata_df.update(parse_values(f'{root_key}__{key}', values))
    
    # Parse title and description
    for root_key in ['TITLE', 'DESCRIPTION']:
        if root_key in metadata_dict:
            metadata_df[root_key] = metadata_dict[root_key]
    
    # Parse sample attributes
    if 'SAMPLE_ATTRIBUTES' in metadata_dict:
        sample_attrs = metadata_dict['SAMPLE_ATTRIBUTES']['SAMPLE_ATTRIBUTE']
        for attribute in sample_attrs:
            key = '_'.join(attribute['TAG'].split())
            metadata_df[key] = attribute['VALUE']
    
    return pd.DataFrame(metadata_df, index=[0])


def retrieve_ena_metadata(samples: List[str], folder: str, NO_PROGRESS_BAR: bool) -> Optional[pd.DataFrame]:
    """
    Retrieve metadata for multiple ENA samples.
    
    Args:
        samples: List of sample accessions
        folder: Directory to save downloaded XML files
        NO_PROGRESS_BAR: disables progress bar, if True
        
    Returns:
        DataFrame with combined metadata, or None if failed
    """
    try:
        filenames = [
            download_file(
                get_ena_sample_xml_url(sample),
                folder=folder
            )
            for sample in tqdm(
                samples,
                desc='Getting ENA Metadata',
                disable=NO_PROGRESS_BAR
            )
        ]
        
        metadata_dfs = [parse_ena_sample_table(filename) for filename in filenames]
        metadata_df = pd.concat(metadata_dfs, ignore_index=True)
        metadata_df.index = metadata_df['IDENTIFIERS__PRIMARY_ID'].values
        
        return metadata_df
    except Exception as e:
        print(f"Failed to retrieve ENA metadata: {e}")
        return None


def correct_duplicate_columns(table: pd.DataFrame) -> pd.DataFrame:
    """
    Rename duplicate column names by appending numbers.
    
    Args:
        table: DataFrame with potentially duplicate column names
        
    Returns:
        DataFrame with unique column names
    """
    unique_cols, counts = np.unique(table.columns.values, return_counts=True)
    duplicated_columns = unique_cols[counts > 1]
    
    def increment_generator(column: str):
        """Generator that yields column names with incrementing suffixes."""
        iter_num = 1
        while True:
            if iter_num == 1:
                yield column
            else:
                yield f'{column}_{iter_num}'
            iter_num += 1
    
    # Create generators for duplicated columns
    generators = {
        col: increment_generator(col)
        for col in table.columns.values
        if col in duplicated_columns
    }
    
    # Apply unique names
    table.columns = [
        next(generators[col]) if col in generators else col
        for col in table.columns.values
    ]

    columns_to_remove = []
    columns_to_rename = {}
    for column in generators.keys():
        final_increment = next(generators[column])
        final_increment = int(final_increment.split('_')[-1])
        duplicated_columns = [f'{column}_{iter_num}' 
                              for iter_num in range(2, final_increment)]
        for dup_column in duplicated_columns:
            if not all(table[column].values == table[dup_column].values):
                duplicated_columns.remove(dup_column)
        if len(duplicated_columns) > 0:
            columns_to_rename[f'{column}_1'] = column

    table = table.drop(columns_to_remove, axis=1)
    table = table.rename(columns=columns_to_rename)
    return table


def get_ncbi_info(sample_accessions: List[str], NO_PROGRESS_BAR: bool) -> pd.DataFrame:
    """
    Retrieve sample information from NCBI BioSample.
    
    Args:
        sample_accessions: List of sample accession numbers
        NO_PROGRESS_BAR: Disables progress bar if True
        
    Returns:
        DataFrame with combined NCBI sample information
    """
    sample_info_tables = []
    
    for sample_accession in tqdm(
        sample_accessions,
        desc='Getting NCBI Info',
        disable=NO_PROGRESS_BAR
    ):
        url = get_ncbi_biosample_url(sample_accession)
        sample_info = pd.read_html(url, index_col=0)[0].transpose()
        sample_info.index = [sample_accession]
        sample_info_tables.append(correct_duplicate_columns(sample_info))
    
    return pd.concat(sample_info_tables, ignore_index=True)


def get_samples_info_by_ena_prj_name(
    prj_name: str,
    folder: str = '',
    save_table: bool = True,
    return_table: bool = True,
    return_html: bool = False,
    return_path: bool = False,
    cleanup_xml: bool = True,
    NO_PROGRESS_BAR: bool = False,
) -> Union[pd.DataFrame, str, Tuple]:
    """
    Main function to extract and compile sample information from ENA project.
    
    Args:
        prj_name: ENA project accession (e.g., 'PRJNA335681')
        folder: Directory to save output files
        save_table: Whether to save CSV and HTML outputs
        return_table: Whether to return the DataFrame
        return_html: Whether to return HTML string
        return_path: Whether to return path to HTML file
        cleanup_xml: Whether to automatically remove xml_files folder after extraction (default: True)
        
    Returns:
        Depending on flags: DataFrame, HTML string, file path, or tuple of these
        
    Example:
        >>> samples = get_samples_info_by_ena_prj_name('PRJNA335681', folder='output')
        >>> # Keep XML files:
        >>> samples = get_samples_info_by_ena_prj_name('PRJNA335681', folder='output', cleanup_xml=False)
    """
    # Create directory if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    try:
        # Download basic sample information
        samples_info = download_samples_file(prj_name, folder=folder)
        samples_info = correct_duplicate_columns(samples_info)
        samples_info.index = samples_info['sample_accession'].values
        
        # Try to get detailed metadata from ENA, fall back to NCBI if needed
        samples_table = retrieve_ena_metadata(samples_info['sample_accession'].values, folder, NO_PROGRESS_BAR)
        samples_table = correct_duplicate_columns(samples_table)
        
        if samples_table is None:
            print("ENA metadata retrieval failed, falling back to NCBI...")
            samples_table = get_ncbi_info(samples_info['sample_accession'].values, NO_PROGRESS_BAR)
        
        # Combine basic info with detailed metadata
        samples_table = pd.concat([samples_info, samples_table], axis=1)
        samples_table = correct_duplicate_columns(samples_table)

        # Save outputs if requested
        filepath = os.path.join(folder, prj_name)
        if save_table:
            os.makedirs(folder, exist_ok=True)
            samples_table.to_csv(f'{filepath}.csv', index=False)
            
            with open(f'{filepath}.html', 'w') as f:
                f.write(generate_html_report(samples_table))
        
        # Prepare return values based on flags
        return_values = []
        if return_table:
            return_values.append(samples_table)
        if return_html:
            return_values.append(generate_html_report(samples_table))
        if return_path:
            return_values.append(f'{filepath}.html')
        
        # Return single value or tuple
        if len(return_values) == 1:
            return return_values[0]
        elif len(return_values) > 1:
            return tuple(return_values)
        else:
            return None
        
    finally:
        # Clean up XML files if requested (runs even if there's an error)
        if cleanup_xml:
            cleanup_xml_files(folder)
