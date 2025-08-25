import pandas as pd
import json

def merge_pad_results():
    """
    Merge the original CSV file with PAD analysis results and add a new column
    indicating whether each project has PAD documents available.
    """
    
    # Load the original CSV file
    print("Loading original CSV file...")
    df_original = pd.read_csv('afdb_full_extraction_with_keywords.csv')
    print(f"Original CSV has {len(df_original)} rows")
    
    # Load the PAD analysis results
    print("Loading PAD analysis results...")
    with open('pad_results.json', 'r', encoding='utf-8') as f:
        pad_results = json.load(f)
    
    # Create a dictionary mapping project_id to has_pad status
    pad_status = {}
    for result in pad_results:
        project_id = result['project_id']
        has_pad = result['has_pad']
        pad_status[project_id] = has_pad
    
    print(f"PAD analysis results cover {len(pad_status)} projects")
    
    # Add the PAD status column to the original dataframe
    print("Adding PAD status column...")
    df_original['Has_PAD_Documents'] = df_original['Identifier'].map(pad_status)
    
    # Fill NaN values with "Unknown" for projects not in the PAD analysis
    df_original['Has_PAD_Documents'] = df_original['Has_PAD_Documents'].fillna('Unknown')
    
    # Convert boolean values to more readable format
    df_original['Has_PAD_Documents'] = df_original['Has_PAD_Documents'].map({
        True: 'Yes',
        False: 'No',
        'Unknown': 'Unknown'
    })
    
    # Save the merged dataset
    output_filename = 'afdb_projects_with_pad_status.csv'
    df_original.to_csv(output_filename, index=False)
    
    # Print summary statistics
    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)
    
    pad_counts = df_original['Has_PAD_Documents'].value_counts()
    print(f"Total projects in original CSV: {len(df_original)}")
    print(f"Projects with PAD analysis: {len(pad_status)}")
    print(f"Projects without PAD analysis: {len(df_original) - len(pad_status)}")
    print("\nPAD Status Distribution:")
    for status, count in pad_counts.items():
        percentage = (count / len(df_original)) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    # Calculate statistics for projects that were analyzed
    analyzed_projects = df_original[df_original['Has_PAD_Documents'] != 'Unknown']
    if len(analyzed_projects) > 0:
        analyzed_pad_counts = analyzed_projects['Has_PAD_Documents'].value_counts()
        print(f"\nAnalyzed Projects Only ({len(analyzed_projects)} projects):")
        for status, count in analyzed_pad_counts.items():
            percentage = (count / len(analyzed_projects)) * 100
            print(f"  {status}: {count} ({percentage:.1f}%)")
    
    print(f"\nMerged dataset saved to: {output_filename}")
    
    return df_original

if __name__ == "__main__":
    merged_df = merge_pad_results()
