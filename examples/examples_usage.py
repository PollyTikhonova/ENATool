"""
ENATool Usage Examples

This script demonstrates various ways to use ENATool for downloading
and managing ENA sequencing data.
"""

import ENATool


def example1_basic_metadata():
    """Example 1: Basic metadata extraction"""
    print("=" * 60)
    print("Example 1: Basic Metadata Extraction")
    print("=" * 60)
    
    # Fetch metadata for a project
    info = ENATool.fetch('PRJNA335681', path='example_project')
    
    print(f"\n✓ Retrieved metadata for {len(info)} samples")
    print(f"✓ Columns: {len(info.columns)}")
    print(f"\nFirst few columns: {info.columns[:5].tolist()}")
    
    # Show some statistics
    if 'scientific_name' in info.columns:
        print(f"\nOrganisms found:")
        for organism, count in info['scientific_name'].value_counts().head(3).items():
            print(f"  • {organism}: {count} samples")
    
    if 'instrument_platform' in info.columns:
        print(f"\nSequencing platforms:")
        for platform, count in info['instrument_platform'].value_counts().items():
            print(f"  • {platform}: {count} samples")


def example2_filtered_download():
    """Example 2: Download with filtering"""
    print("\n" + "=" * 60)
    print("Example 2: Filtered Download")
    print("=" * 60)
    
    # Get metadata
    info = ENATool.fetch('PRJNA335681', path='example_project')
    
    # Filter for specific organism (example)
    if 'scientific_name' in info.columns:
        organisms = info['scientific_name'].unique()
        if len(organisms) > 0:
            target_organism = organisms[0]
            filtered = info[info['scientific_name'] == target_organism]
            
            print(f"\n✓ Filtered to {len(filtered)} {target_organism} samples")
            
            # Reinitialize ena accessor
            filtered.ena.reinit(info)
            
            # Download (commented out to avoid actual download in example)
            # downloads = filtered.ena.download()
            # print(f"✓ Downloaded {(downloads['download_status'] == 'OK').sum()} files")
            
            print("✓ Ready to download (download command commented out)")


def example3_batch_processing():
    """Example 3: Process multiple projects"""
    print("\n" + "=" * 60)
    print("Example 3: Batch Processing Multiple Projects")
    print("=" * 60)
    
    # List of projects to process
    projects = ['PRJNA335681']  # Add more project IDs as needed
    
    results = {}
    for project_id in projects:
        try:
            info = ENATool.fetch(project_id, path=f'batch_data/{project_id}')
            results[project_id] = {
                'status': 'success',
                'samples': len(info),
                'organisms': info['scientific_name'].nunique() if 'scientific_name' in info.columns else 0
            }
            print(f"✓ {project_id}: {len(info)} samples")
        except Exception as e:
            results[project_id] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"✗ {project_id}: {e}")
    
    # Summary
    print(f"\nProcessed {len(projects)} projects:")
    successful = sum(1 for r in results.values() if r['status'] == 'success')
    print(f"  Successful: {successful}/{len(projects)}")


def example4_api_details():
    """Example 4: Using low-level API"""
    print("\n" + "=" * 60)
    print("Example 4: Low-Level API Access")
    print("=" * 60)
    
    from ENATool import get_samples_info_by_ena_prj_name, download_samples
    
    # Get metadata using low-level function
    info = get_samples_info_by_ena_prj_name(
        'PRJNA335681',
        folder='advanced_example',
        save_table=True,
        return_table=True
    )
    
    print(f"\n✓ Retrieved {len(info)} samples using low-level API")
    print(f"✓ Files saved to: advanced_example/")
    
    # Download using low-level function (commented out)
    # downloads = download_samples(
    #     'PRJNA335681',
    #     ena_sample_info_table=info,
    #     destination_folder='advanced_example'
    # )


def example5_data_analysis():
    """Example 5: Metadata analysis"""
    print("\n" + "=" * 60)
    print("Example 5: Metadata Analysis")
    print("=" * 60)
    
    # Get metadata
    info = ENATool.fetch('PRJNA335681', path='analysis_example')
    
    print(f"\nDataset Overview:")
    print(f"  Total samples: {len(info)}")
    print(f"  Total columns: {len(info.columns)}")
    
    # Analyze by platform
    if 'instrument_platform' in info.columns:
        print(f"\nBy Platform:")
        for platform, count in info['instrument_platform'].value_counts().items():
            print(f"  {platform}: {count} ({count/len(info)*100:.1f}%)")
    
    # Analyze by library strategy
    if 'library_strategy' in info.columns:
        print(f"\nBy Library Strategy:")
        for strategy, count in info['library_strategy'].value_counts().head(5).items():
            print(f"  {strategy}: {count}")
    
    # Check for paired-end
    if 'library_layout' in info.columns:
        print(f"\nLibrary Layout:")
        for layout, count in info['library_layout'].value_counts().items():
            print(f"  {layout}: {count}")


def example6_export_data():
    """Example 6: Export and save data"""
    print("\n" + "=" * 60)
    print("Example 6: Export Data")
    print("=" * 60)
    
    # Get metadata
    info = ENATool.fetch('PRJNA335681', path='export_example')
    
    # Export to CSV
    csv_file = 'export_example/samples.csv'
    info.to_csv(csv_file, index=False)
    print(f"✓ Exported to CSV: {csv_file}")
    
    # Export specific columns
    if 'sample_accession' in info.columns and 'scientific_name' in info.columns:
        subset = info[['sample_accession', 'scientific_name', 'library_strategy']]
        subset_file = 'export_example/samples_subset.csv'
        subset.to_csv(subset_file, index=False)
        print(f"✓ Exported subset to: {subset_file}")
    
    print(f"✓ Interactive HTML available at: export_example/PRJNA335681.html")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("ENATool Examples")
    print("=" * 60)
    print("\nThese examples demonstrate ENATool functionality.")
    print("Note: Downloads are commented out to avoid large data transfers.\n")
    
    try:
        example1_basic_metadata()
        example2_filtered_download()
        example3_batch_processing()
        example4_api_details()
        example5_data_analysis()
        example6_export_data()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        print("\nCheck the generated directories for output files:")
        print("  • example_project/")
        print("  • batch_data/")
        print("  • advanced_example/")
        print("  • analysis_example/")
        print("  • export_example/")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Note: Some examples require internet connection to ENA servers.")


if __name__ == "__main__":
    main()
