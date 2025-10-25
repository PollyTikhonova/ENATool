# ENATool 🧬

[![PyPI version](https://badge.fury.io/py/ENATool.svg)](https://badge.fury.io/py/ENATool)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python package for downloading and managing sequencing data from the European Nucleotide Archive (ENA) in terminal and through Python interface.

## ✨ Features

- 📊 **Extract Metadata** - Get comprehensive sample information from ENA projects
- 📥 **Download FASTQ Files** - Automated download with progress tracking
- 🔄 **Auto Fallback** - Automatically tries NCBI if ENA metadata unavailable
- 📈 **Progress Bars** - Real-time progress for downloads and metadata retrieval
- 📋 **Interactive Reports** - Generate searchable HTML tables with DataTables.js
- 💾 **Export to CSV** - Save metadata in standard formats
- 🔍 **Smart Verification** - Check fastq file integrity and skip existing files
- 💻 **Command line and Python interface**

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install ENATool
```

### Basic Usage in Terminal

```bash
# Custom output directory
enatool download PRJNA335681 --path data/my_project
```

### Basic Usage in Python

```python
import ENATool

# Fetch metadata AND download files in one command
info, downloads = ENATool.fetch('PRJNA335681', path='data/my_project', download=True)
```
## 📊 Example Output Files

ENATool creates organized output:

```
my_project/
├── PRJNA335681.csv              # Sample metadata
├── PRJNA335681.html             # Interactive table
├── downoad_info_table.csv       # Download tracking
└── raw_reads/                  # Downloaded FASTQ files
    ├── SRR123456/
    │   ├── SRR123456_1.fastq.gz
    │   └── SRR123456_2.fastq.gz
    └── SRR123457/
        └── SRR123457.fastq.gz
```

## 🔧 Requirements

- Python >= 3.7
- pandas >= 1.3.0
- numpy >= 1.20.0
- requests >= 2.25.0
- xmltodict >= 0.12.0
- tqdm >= 4.60.0
- lxml >= 4.6.0

## 📖 Documentation

- [Use ENATool in Terminal](#use-enatool-in-terminal)
   - [Fetching metadata](#fetching-metadata)
   - [Download reads and fetch metadata](#download-reads-and-fetch-metadata)
   - [Show project summary](#show-project-summary-stdout)
   - [Redownload corrupted files or download selected files only](#redownload-corrupted-files-or-download-only-selected-files)
   - [Leave files with incorrect md5 checksum](#leave-files-with-incorrect-md5-checksum)
   - [Process multiple projects](#process-multiple-projects)
   - [Hide banner](#hide-banner)
   - [Disable progress bar](#disable-progress-bar)
- [Use ENATool in Python](#use-enatool-in-python)
   - [Fetch Metadata](#fetch-metadata)
   - [Download FASTQ Files](#download-fastq-files)
   - [Download only a subset of samples](#download-only-a-subset-of-samples)
   - [Leave files with incorrect md5 checksum](#leave-files-with-incorrect-md5-checksum-1)
   - [Disable progress bar](#disable-progress-bar-1)
   - [Work with multiple datasets](#work-with-multiple-datasets)
   - [Python API Reference](#python-api-reference)
- [Citation](#-citation)

## Use ENATool in Terminal

### Fetching Metadata

Download metadata for all samples in an ENA project using `enatool fetch`.

**Syntax:**
```bash
enatool fetch PROJECT_ID [--path DIR]
```

**Arguments:**
- `PROJECT_ID` (required): ENA project accession (e.g., PRJNA335681)
- `--path DIR` or `-p DIR`: Output directory (default: PROJECT_ID)

**What it does:**
- Downloads sample metadata from ENA
- Tries NCBI BioSample as fallback if ENA fails
- Creates CSV file with all metadata
- Generates interactive HTML report
- Shows progress bars

**Output files:**
- `PROJECT_ID.csv` - Metadata in CSV format
- `PROJECT_ID.html` - Interactive HTML table

**Examples:**

```bash
# Basic usage - saves to PRJNA335681/
enatool fetch PRJNA335681

# Custom output directory
enatool fetch PRJNA335681 --path data/my_project
```

### Download Reads and Fetch Metadata
Download metadata for all samples in an ENA project and download sample files using using `enatool download`.

**Syntax:**
```bash
enatool download PROJECT_ID [--path DIR]
```

**Arguments:**
- `PROJECT_ID` (required): ENA project accession
- `--path DIR` or `-p DIR`: Output directory (default: PROJECT_ID)

**What it does:**
- Downloads metadata (same as `fetch`)
- Downloads all FASTQ files for all samples
- Uses enaDataGet tool
- Skips files that already exist
- Tracks download status

**Output files:**
- `PROJECT_ID.csv` - Metadata
- `PROJECT_ID.html` - Interactive table
- `downoad_info_table.csv` - Download tracking
- `raw_reads/` - Directory with FASTQ files
  - `SRR123456/` - One directory per run
    - `SRR123456_1.fastq.gz` - Forward reads
    - `SRR123456_2.fastq.gz` - Reverse reads (if paired-end)

**Examples:**

```bash
# Download everything
enatool download PRJNA335681

# Custom output directory
enatool download PRJNA335681 --path data/project1
```

### Show Project Summary [stdout]

Display summary information about a downloaded project using `enatool info`.

**Syntax:**
```bash
enatool info PROJECT_ID --path DIR
```

**Arguments:**
- `PROJECT_ID` (required): ENA project accession
- `--path DIR` or `-p DIR` (required): Directory containing metadata

**What it does:**
- Reads metadata from CSV file
- Shows summary statistics
- Displays organism breakdown
- Shows sequencing platforms
- Shows download status (if available)

**Examples:**

```bash
# Show info for custom directory
enatool info PRJNA335681 --path data/my_project
```

**Output:**
```
📊 Project Information: PRJNAXXXXXX
============================================================
Total samples: 50

Organisms (2):
  • Homo sapiens: 45
  • Mus musculus: 5

Sequencing Platforms:
  • ILLUMINA: 50

Library Strategies:
  • RNA-Seq: 30
  • WGS: 15
  • ChIP-Seq: 5

Library Layout:
  • PAIRED: 45
  • SINGLE: 5

Download Status:
  • OK: 48
  • Error: 2
```


### Redownload Corrupted Files or Download Only Selected Files

Download all FASTQ files using previously fetched metadata or based on the subsetted metadata table using `enatool download-files`. Also forces redownload of files which previously ended up with a error.

**Syntax:**
```bash
enatool download-files PROJECT_ID --path DIR
```

**Arguments:**
- `PROJECT_ID` (required): ENA project accession
- `--path DIR` or `-p DIR` (required): Directory containing metadata

**What it does:**
- Loads sample names from existing CSV file (`PROJECT_ID.csv`)
- Downloads FASTQ files
- Useful if you already have metadata and just want the files or for filtered metadata tables.

**Use cases:**
- You fetched metadata earlier with `enatool fetch`
- You filtered the CSV file manually
- You want to re-download after failures

**Examples:**

```bash
# First get metadata (fast)
enatool fetch PRJNA335681 --path my_project

# Later, download files 
enatool download-files PRJNA335681 --path my_project

# Or after filtering CSV file
enatool download-files PRJNA335681 --path my_project
```

### Leave files with incorrect md5 checksum

By default ENATool removes all the files which ended up being corrupted or md5 chesum did not match. However, you may use `--keep-failed` paramter to prevent the removal.

**Syntax:**
```bash
# with download command
enatool download PROJECT_ID --path DIR --keep-failed

# with download-files command
enatool download-files PROJECT_ID --path DIR --keep-failed
```

### Process multiple projects

For processing multiple projects:

```bash
# Simple loop
for project in PRJNA335681 PRJNA123456 PRJNA789012; do
    echo "Processing $project..."
    enatool fetch $project --path data/$project
done

# Or with download
for project in PRJNA335681 PRJNA123456; do
    echo "Downloading $project..."
    enatool download $project --path data/$project
done
```

### Hide banner
Use a global `enatool` option: `--no-banner`. Follows right after `enatool` and before the action command.

**Example:**
```bash
enatool --no-banner fetch PRJNA335681
```

### Disable progress bar
Use a global `enatool` option: `--no-progress-bar`. Follows right after `enatool` and before the action command.

**Example:**
```bash
enatool --no-progress-bar fetch PRJNA335681
```

__
## Use ENATool in Python
### Fetch Metadata

Use `fetch()` function to download metadata:

```python
import ENATool

# Basic usage - just get metadata
info_table = ENATool.fetch('PRJNA335681')

# Specify custom directory
info_table = ENATool.fetch('PRJNA335681', path='data/my_project')

# Get metadata AND download files
info_table, downloads = ENATool.fetch('PRJNA335681', download=True)

# Show some basic stats
print(f"Total samples: {len(info_table)}")
print(f"Organisms: {info_table['scientific_name'].unique()}")
print(f"Platforms: {info_table['instrument_platform'].value_counts()}")
```

**What you get:**
- Sample accessions and metadata
- Run accessions and sequencing details
- FASTQ file URLs and checksums
- Organism and experimental information
- Interactive HTML report

### Download FASTQ Files

```python
import ENATool

# Get metadata AND download files
info_table, downloads = ENATool.fetch('PRJNA335681', download=True)

# Check results
print(downloads['download_status'].value_counts())
```

**Download status values:**
- `OK` - Successfully downloaded
- `Exists` - File already exists (skipped)
- `Error` - Download failed

### Download only a subset of samples

```python
import ENATool

# Get metadata
info = ENATool.fetch('PRJNA335681')

# Filter samples
human_samples = info[info['scientific_name'] == 'Homo sapiens']

# ! Important ! 
# Re-initialize for filtered table
human_samples.ena.reinit(info)

# Download only filtered samples
downloads = human_samples.ena.download()

# Save to CSV
human_samples.to_csv('human_samples.csv', index=False)
```

### Leave files with incorrect md5 checksum
Prevent ENATool from automatic removal of the corrupted files.

```python
import ENATool

# Could be used in fetch method
info_table, downloads = ENATool.fetch('PRJNA335681', download=True, keep_failed=True)

# Could be used in download method
info = ENATool.fetch('PRJNA335681')
downloads = info.ena.download(keep_failed=True)
```

### Disable progress bar
```python
import ENATool

# Could be used in fetch method
info_table, downloads = ENATool.fetch('PRJNA335681', download=True, NO_PROGRESS_BAR=True)

# Could be used in download method
info = ENATool.fetch('PRJNA335681')
downloads = info.ena.download(NO_PROGRESS_BAR=True)
```

### Work with multiple datasets

```python
import ENATool

projects = ['PRJNA335681', 'PRJEB2961', 'PRJEB28350']

for project_id in projects:
    try:
        info = ENATool.fetch(project_id, path=f'data/{project_id}')
        print(f"✓ {project_id}: {len(info)} samples")
    except Exception as e:
        print(f"✗ {project_id}: {e}")
```

## Python API Reference

### Main Functions

#### `ENATool.fetch(project_id, path=None, download=False)`

Main entry point for fetching ENA data.

**Parameters:**
- `project_id` (str): ENA project accession (e.g., 'PRJNA335681')
- `path` (str, optional): Directory for outputs (defaults to project_id)
- `download` (bool, optional): Auto-download FASTQ files (default: False)

**Returns:**
- DataFrame (if download=False)
- Tuple of (info_table, download_table) (if download=True)

#### `DataFrame.ena.download()`

Download FASTQ files for samples in DataFrame.

**Returns:**
- DataFrame with download status


## 📝 Citation

If you use ENATool in your research, please cite:

```
Tikhonova, P. (2021). ENATool: European Nucleotide Archive Data Manager (v2.0.0). Zenodo. https://doi.org/10.5281/zenodo.17443004
```


## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI:** https://pypi.org/project/ENATool/
- **GitHub:** https://github.com/PollyTikhonova/ENATool
- **Documentation:** https://github.com/PollyTikhonova/ENATool#readme
- **Bug Reports:** https://github.com/PollyTikhonova/ENATool/issues
