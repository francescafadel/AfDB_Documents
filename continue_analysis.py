#!/usr/bin/env python3
"""
Script to continue PAD analysis with remaining URLs from the CSV file.
This can be run to process the remaining URLs beyond the first 50.
"""

import csv
import json
import time
from check_all_pads import check_for_pad, read_csv_urls

def continue_pad_analysis(start_index=50, batch_size=50):
    """
    Continue PAD analysis from a specific index
    
    Args:
        start_index (int): Starting index in the URL list
        batch_size (int): Number of URLs to process in this batch
    """
    
    # Read all URLs from CSV
    all_urls = read_csv_urls("afdb_full_extraction_with_keywords.csv")
    
    if start_index >= len(all_urls):
        print(f"Start index {start_index} is beyond the total number of URLs ({len(all_urls)})")
        return
    
    # Get the batch of URLs to process
    end_index = min(start_index + batch_size, len(all_urls))
    urls_to_check = all_urls[start_index:end_index]
    
    print(f"Processing URLs {start_index+1} to {end_index} (batch size: {len(urls_to_check)})")
    print(f"Total URLs in CSV: {len(all_urls)}")
    print("=" * 80)
    
    results = []
    
    for i, (project_id, url) in enumerate(urls_to_check, start_index + 1):
        print(f"\n[{i}/{len(all_urls)}] ", end="")
        has_pad, evidence, document_links = check_for_pad(url, project_id)
        
        results.append({
            'project_id': project_id,
            'url': url,
            'has_pad': has_pad,
            'evidence': evidence
        })
        
        # Add a small delay to be respectful to the server
        time.sleep(1)
    
    # Summary for this batch
    projects_with_pad = [r for r in results if r['has_pad']]
    projects_without_pad = [r for r in results if not r['has_pad']]
    
    print("\n" + "=" * 80)
    print(f"BATCH SUMMARY (URLs {start_index+1}-{end_index}):")
    print("=" * 80)
    print(f"Projects WITH PADs: {len(projects_with_pad)}")
    print(f"Projects WITHOUT PADs: {len(projects_without_pad)}")
    print(f"Success rate: {len(projects_with_pad)/len(results)*100:.1f}%")
    
    # Save batch results
    batch_filename = f"pad_results_batch_{start_index+1}_{end_index}.json"
    with open(batch_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBatch results saved to {batch_filename}")
    
    return results

def main():
    """Main function to run the analysis"""
    print("AfDB PAD Analysis - Continue Script")
    print("=" * 50)
    
    # You can modify these parameters as needed
    start_index = 50  # Start from URL 51 (after the first 50)
    batch_size = 50   # Process 50 URLs at a time
    
    print(f"Starting analysis from URL {start_index + 1}")
    print(f"Batch size: {batch_size}")
    
    # Run the analysis
    results = continue_pad_analysis(start_index, batch_size)
    
    if results:
        print(f"\nAnalysis completed successfully!")
        print(f"Processed {len(results)} URLs in this batch")
    else:
        print("\nAnalysis failed or no URLs to process")

if __name__ == "__main__":
    main()

