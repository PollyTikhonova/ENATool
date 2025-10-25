"""
ENATool Command Line Interface

This module provides command-line access to ENATool functionality.
"""
import traceback
import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from . import fetch, __version__
from .safe_samples_downloader import get_download_summary


def print_banner():
    """Print ENATool banner."""
    banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║                        ENATool v{__version__}                            ║
║          European Nucleotide Archive Data Manager                ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def fetch_metadata_command(args):
    """
    Execute metadata fetch command.
    
    Args:
        args: Parsed command-line arguments
    """
    print(f"📊 Fetching metadata for project: {args.project_id}")
    
    # Determine output path
    output_path = args.path or args.project_id
    
    try:
        # Fetch metadata
        info = fetch(args.project_id, path=output_path, download=False, NO_PROGRESS_BAR=args.no_progress_bar)
        
        # Print summary
        print(f"\n✓ Successfully retrieved metadata")
        print(f"  • Total samples: {len(info)}")
        print(f"  • Output directory: {os.path.abspath(output_path)}")
        print(f"  • CSV file: {args.project_id}.csv")
        print(f"  • HTML file: {args.project_id}.html")
        
        # Show organism breakdown if available
        if 'scientific_name' in info.columns:
            print(f"\n  Organisms:")
            for organism, count in info['scientific_name'].value_counts().head(5).items():
                print(f"    • {organism}: {count} samples")
        
        # Show platform breakdown if available
        if 'instrument_platform' in info.columns:
            print(f"\n  Sequencing platforms:")
            for platform, count in info['instrument_platform'].value_counts().items():
                print(f"    • {platform}: {count} samples")
        
        print(f"\n✓ Metadata extraction complete!")
        return 0
        
    except Exception as e:
        print()
        print(traceback.format_exc())
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def download_command(args):
    """
    Execute download command (metadata + FASTQ files).
    
    Args:
        args: Parsed command-line arguments
    """
    print(f"📥 Fetching metadata and downloading FASTQ files for: {args.project_id}")
    
    # Determine output path
    output_path = args.path or args.project_id
    
    try:
        # Fetch metadata and download files
        info, downloads = fetch(args.project_id, path=output_path, download=True, keep_failed=args.keep_failed, NO_PROGRESS_BAR=args.no_progress_bar)
        
        # Print metadata summary
        print(f"\n✓ Metadata retrieved: {len(info)} samples")
        
        # Print download summary
        summary = get_download_summary(downloads)
        
        print(f"\n📥 Download Summary:")
        print(f"  • Total files: {summary['total']}")
        print(f"  • Successfully downloaded: {summary['successful']}")
        print(f"  • Already existed: {summary['already_existed']}")
        print(f"  • Failed: {summary['failed']}")
        
        if summary['failed'] > 0:
            print(f"\n⚠ Some downloads failed. Check the download table for details.")
            failed = downloads[downloads['download_status'] == 'Error']
            print(f"  Failed accessions: {', '.join(failed['accession'].tolist()[:5])}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")
        
        print(f"\n✓ Files saved to: {os.path.abspath(output_path)}/raw_reads/")
        print(f"✓ Download complete!")
        
        return 0
        
    except Exception as e:
        print()
        print(traceback.format_exc())
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def download_files_only_command(args):
    """
    Download FASTQ files for existing metadata.
    
    Args:
        args: Parsed command-line arguments
    """
    print(f"📥 Downloading FASTQ files for existing metadata")
    
    try:
        # Check if metadata exists
        csv_file = os.path.join(args.path, f"{args.project_id}.csv")
        if not os.path.exists(csv_file):
            print(f"\n✗ Error: Metadata file not found: {csv_file}")
            print(f"  Run 'enatool fetch {args.project_id}' first to get metadata")
            return 1
        
        # Load existing metadata
        import pandas as pd
        info = pd.read_csv(csv_file)
        
        # Set up ena accessor
        info.ena.id = args.project_id
        info.ena.path = args.path
        
        print(f"  • Found {len(info)} samples in metadata")
        print(f"  • Starting download...")
        
        # Download files
        downloads = info.ena.download(keep_failed=args.keep_failed, NO_PROGRESS_BAR=args.no_progress_bar)
        
        # Print summary
        summary = get_download_summary(downloads)
        
        print(f"\n📥 Download Summary:")
        print(f"  • Total files: {summary['total']}")
        print(f"  • Successfully downloaded: {summary['successful']}")
        print(f"  • Already existed: {summary['already_existed']}")
        print(f"  • Failed: {summary['failed']}")

        if summary['failed'] > 0:
            print(f"\n⚠ Some downloads failed. Check the download table for details.")
            failed = downloads[downloads['download_status'] == 'Error']
            print(f"  Failed accessions: {', '.join(failed['accession'].tolist()[:5])}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")
        
        print(f"\n✓ Files saved to: {os.path.abspath(args.path)}/raw_reads/")
        print(f"✓ Download complete!")
        
        return 0
        
    except Exception as e:
        print()
        print(traceback.format_exc())
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def info_command(args):
    """
    Show information about downloaded project.
    
    Args:
        args: Parsed command-line arguments
    """
    try:
        import pandas as pd
        
        # Check for metadata file
        csv_file = os.path.join(args.path, f"{args.project_id}.csv")
        if not os.path.exists(csv_file):
            print(f"\n✗ Error: Metadata file not found: {csv_file}")
            print(f"  Run 'enatool fetch {args.project_id}' first")
            return 1
        
        # Load metadata
        info = pd.read_csv(csv_file)
        
        print(f"\n📊 Project Information: {args.project_id}")
        print(f"{'='*60}")
        print(f"Total samples: {len(info)}")
        
        if 'scientific_name' in info.columns:
            print(f"\nOrganisms ({info['scientific_name'].nunique()}):")
            for organism, count in info['scientific_name'].value_counts().head(10).items():
                print(f"  • {organism}: {count}")
        
        if 'instrument_platform' in info.columns:
            print(f"\nSequencing Platforms:")
            for platform, count in info['instrument_platform'].value_counts().items():
                print(f"  • {platform}: {count}")
        
        if 'library_strategy' in info.columns:
            print(f"\nLibrary Strategies:")
            for strategy, count in info['library_strategy'].value_counts().head(5).items():
                print(f"  • {strategy}: {count}")
        
        if 'library_layout' in info.columns:
            print(f"\nLibrary Layout:")
            for layout, count in info['library_layout'].value_counts().items():
                print(f"  • {layout}: {count}")
        
        # Check for download info
        download_file = os.path.join(args.path, 'downoad_info_table.csv')
        if os.path.exists(download_file):
            downloads = pd.read_csv(download_file, sep='\t')
            if 'download_status' in downloads.columns:
                print(f"\nDownload Status:")
                for status, count in downloads['download_status'].value_counts().items():
                    print(f"  • {status}: {count}")
        
        return 0
        
    except Exception as e:
        print()
        print(traceback.format_exc())
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='enatool',
        description='ENATool - European Nucleotide Archive Data Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch metadata only
  enatool fetch PRJNA335681
  
  # Fetch metadata with custom output directory
  enatool fetch PRJNA335681 --path my_project
  
  # Fetch metadata and download FASTQ files
  enatool download PRJNA335681
  
  # Download files for existing metadata
  enatool download-files PRJNA335681 --path my_project
  
  # Show project information
  enatool info PRJNA335681 --path my_project

For more information: https://github.com/RCPCM-GCB/ENATool
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'ENATool {__version__}'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Suppress banner output'
    )

    parser.add_argument(
        '--no-progress-bar',
        action='store_true',
        help='Suppress progress bar'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Fetch command (metadata only)
    fetch_parser = subparsers.add_parser(
        'fetch',
        help='Fetch metadata for an ENA project',
        description='Download and save metadata for all samples in an ENA project'
    )
    fetch_parser.add_argument(
        'project_id',
        help='ENA project accession (e.g., PRJNA335681)'
    )
    fetch_parser.add_argument(
        '-p', '--path',
        help='Output directory (default: project_id)',
        metavar='DIR'
    )
    
    # Download command (metadata + files)
    download_parser = subparsers.add_parser(
        'download',
        help='Fetch metadata and download FASTQ files',
        description='Download metadata and all FASTQ files for an ENA project'
    )
    download_parser.add_argument(
        'project_id',
        help='ENA project accession (e.g., PRJNA335681)'
    )
    download_parser.add_argument(
        '-p', '--path',
        help='Output directory (default: project_id)',
        metavar='DIR'
    )
    download_parser.add_argument(
        '-k', '--keep-failed',
        action='store_true',
        help='Keep files that downloaded with md5 errors'
    )
    
    # Download-files command (files only for existing metadata)
    download_files_parser = subparsers.add_parser(
        'download-files',
        help='Download FASTQ files for existing metadata',
        description='Download FASTQ files using previously fetched metadata'
    )
    download_files_parser.add_argument(
        'project_id',
        help='ENA project accession (e.g., PRJNA335681)'
    )
    download_files_parser.add_argument(
        '-p', '--path',
        required=True,
        help='Path to directory containing metadata',
        metavar='DIR'
    )
    download_files_parser.add_argument(
        '-k', '--keep-failed',
        action='store_true',
        help='Keep files that downloaded with md5 errors'
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Show information about a project',
        description='Display summary information about downloaded project metadata'
    )
    info_parser.add_argument(
        'project_id',
        help='ENA project accession (e.g., PRJNA335681)'
    )
    info_parser.add_argument(
        '-p', '--path',
        required=True,
        help='Path to directory containing metadata',
        metavar='DIR'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show banner unless suppressed
    if not args.no_banner:
        print_banner()

    # Handle no command
    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    if args.command == 'fetch':
        return fetch_metadata_command(args)
    elif args.command == 'download':
        return download_command(args)
    elif args.command == 'download-files':
        return download_files_only_command(args)
    elif args.command == 'info':
        return info_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
