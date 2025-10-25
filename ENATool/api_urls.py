"""
API URL Templates for ENA and NCBI

This module contains all URL templates and API endpoints used for accessing
ENA (European Nucleotide Archive) and NCBI resources.
"""

# ENA API Base URLs
ENA_PORTAL_API_BASE = "https://www.ebi.ac.uk/ena/portal/api"
ENA_BROWSER_API_BASE = "https://www.ebi.ac.uk/ena/browser/api"

# NCBI Base URLs
NCBI_BIOSAMPLE_BASE = "https://www.ncbi.nlm.nih.gov/biosample"


# ENA File Report Fields
ENA_FILEREPORT_FIELDS = [
    "study_accession",
    "secondary_study_accession",
    "sample_accession",
    "secondary_sample_accession",
    "experiment_accession",
    "run_accession",
    "submission_accession",
    "tax_id",
    "scientific_name",
    "instrument_platform",
    "instrument_model",
    "library_name",
    "nominal_length",
    "library_layout",
    "library_strategy",
    "library_source",
    "library_selection",
    "read_count",
    "base_count",
    "center_name",
    "first_public",
    "last_updated",
    "experiment_title",
    "study_title",
    "study_alias",
    "experiment_alias",
    "run_alias",
    "fastq_bytes",
    "fastq_md5",
    "fastq_ftp",
    "fastq_aspera",
    "fastq_galaxy",
    "submitted_bytes",
    "submitted_md5",
    "submitted_ftp",
    "submitted_aspera",
    "submitted_galaxy",
    "submitted_format",
    "sra_bytes",
    "sra_md5",
    "sra_ftp",
    "sra_aspera",
    "sra_galaxy",
    "sample_alias",
    "broker_name",
    "sample_title",
    "nominal_sdev",
    "first_created"
]


def get_ena_filereport_url(project_accession: str) -> str:
    """
    Generate URL for ENA file report API.
    
    Args:
        project_accession: ENA project accession (e.g., 'PRJNA335681')
        
    Returns:
        Complete URL for the file report API
        
    Example:
        >>> get_ena_filereport_url('PRJNA335681')
        'https://www.ebi.ac.uk/ena/portal/api/filereport?accession=...'
    """
    fields_str = ",".join(ENA_FILEREPORT_FIELDS)
    
    return (
        f"{ENA_PORTAL_API_BASE}/filereport?"
        f"accession={project_accession}&"
        f"result=read_run&"
        f"fields={fields_str}&"
        f"format=tsv&"
        f"download=true"
    )


def get_ena_sample_xml_url(sample_accession: str) -> str:
    """
    Generate URL for ENA sample XML API.
    
    Args:
        sample_accession: Sample accession number
        
    Returns:
        URL to download sample XML
        
    Example:
        >>> get_ena_sample_xml_url('SAMN12345678')
        'https://www.ebi.ac.uk/ena/browser/api/xml/SAMN12345678?download=true'
    """
    return f"{ENA_BROWSER_API_BASE}/xml/{sample_accession}?download=true"


def get_ncbi_biosample_url(sample_accession: str) -> str:
    """
    Generate URL for NCBI BioSample page.
    
    Args:
        sample_accession: Sample accession number
        
    Returns:
        URL to NCBI BioSample page
        
    Example:
        >>> get_ncbi_biosample_url('SAMN12345678')
        'https://www.ncbi.nlm.nih.gov/biosample/SAMN12345678'
    """
    return f"{NCBI_BIOSAMPLE_BASE}/{sample_accession}"
