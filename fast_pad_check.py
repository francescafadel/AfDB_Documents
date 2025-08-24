#!/usr/bin/env python3
import csv
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re

def check_for_pad_fast(url, project_id):
    """Faster version of PAD checking with better error handling"""
    print(f"Checking {project_id}: {url}")
    
    try:
        # Set up Chrome options for faster operation
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-images")  # Don't load images
        chrome_options.add_argument("--disable-javascript")  # Disable JS if possible
        chrome_options.add_argument("--window-size=800,600")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Navigate to the URL with shorter timeout
            driver.set_page_load_timeout(30)
            driver.get(url)
            
            # Wait less time for page to load
            time.sleep(2)
            
            # Get the page source
            page_source = driver.page_source
            
            # Quick check for PAD-related content
            pad_keywords = ["appraisal report", "project appraisal document"]
            
            found_pad = False
            pad_evidence = []
            
            for keyword in pad_keywords:
                if re.search(keyword, page_source, re.IGNORECASE):
                    found_pad = True
                    # Just count occurrences, don't extract context
                    matches = len(re.findall(keyword, page_source, re.IGNORECASE))
                    pad_evidence.append(f"Found '{keyword}' {matches} times")
                    break  # Found one, that's enough
            
            if found_pad:
                print(f"✅ PAD FOUND in {project_id}")
                return True, pad_evidence, []
            else:
                print(f"❌ No PAD found in {project_id}")
                return False, [], []
                
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Error checking {project_id}: {str(e)}")
        return False, [], []

def resume_analysis(start_index=400, batch_size=100):
    """Resume analysis from a specific point"""
    
    # Read URLs from CSV
    all_urls = []
    try:
        with open("afdb_full_extraction_with_keywords.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('project_url'):
                    project_id = row.get('Identifier', 'Unknown')
                    all_urls.append((project_id, row['project_url']))
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return
    
    print(f"Found {len(all_urls)} URLs in CSV file")
    print(f"Resuming from URL {start_index + 1}")
    
    # Get the batch of URLs to process
    end_index = min(start_index + batch_size, len(all_urls))
    urls_to_check = all_urls[start_index:end_index]
    
    print(f"Processing URLs {start_index+1} to {end_index} (batch size: {len(urls_to_check)})")
    print("=" * 80)
    
    results = []
    
    for i, (project_id, url) in enumerate(urls_to_check, start_index + 1):
        print(f"\n[{i}/{len(all_urls)}] ", end="")
        
        try:
            has_pad, evidence, document_links = check_for_pad_fast(url, project_id)
            
            results.append({
                'project_id': project_id,
                'url': url,
                'has_pad': has_pad,
                'evidence': evidence
            })
            
        except Exception as e:
            print(f"❌ Error processing {project_id}: {str(e)}")
            results.append({
                'project_id': project_id,
                'url': url,
                'has_pad': False,
                'evidence': [],
                'error': str(e)
            })
        
        # Shorter delay
        time.sleep(0.5)
        
        # Save progress every 25 URLs
        if i % 25 == 0:
            print(f"\n--- Progress saved at {i} URLs ---")
            with open(f'pad_results_fast_{i}.json', 'w') as f:
                json.dump(results, f, indent=2)
    
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
    batch_filename = f"pad_results_fast_batch_{start_index+1}_{end_index}.json"
    with open(batch_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBatch results saved to {batch_filename}")
    
    return results

def main():
    """Main function to run the fast analysis"""
    print("AfDB PAD Analysis - Fast Version")
    print("=" * 50)
    
    # Resume from where the slow version left off (around URL 400)
    start_index = 400
    batch_size = 100  # Process 100 URLs at a time
    
    print(f"Starting fast analysis from URL {start_index + 1}")
    print(f"Batch size: {batch_size}")
    
    # Run the analysis
    results = resume_analysis(start_index, batch_size)
    
    if results:
        print(f"\nFast analysis completed successfully!")
        print(f"Processed {len(results)} URLs in this batch")
    else:
        print("\nFast analysis failed or no URLs to process")

if __name__ == "__main__":
    main()

