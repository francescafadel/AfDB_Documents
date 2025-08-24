#!/usr/bin/env python3
import csv
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json

def extract_document_links(driver, project_id):
    """Extract actual document links from the project page"""
    try:
        # Look for document links in the page
        document_links = []
        
        # Find all links that might be documents
        links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                if href and any(keyword in text.lower() for keyword in ['appraisal', 'report', 'document', 'pad']):
                    document_links.append({
                        'text': text,
                        'url': href,
                        'project_id': project_id
                    })
            except:
                continue
        
        return document_links
    except Exception as e:
        print(f"Error extracting document links for {project_id}: {str(e)}")
        return []

def check_for_pad(url, project_id):
    """Check if a project page contains Project Appraisal Document references"""
    print(f"Checking {project_id}: {url}")
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Navigate to the URL
            driver.get(url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Get the page source
            page_source = driver.page_source
            
            # Check for PAD-related content
            pad_keywords = [
                "project appraisal document",
                "appraisal document", 
                "Project Appraisal",
                "appraisal report",
                "project document",
                "appraisal study"
            ]
            
            found_pad = False
            pad_evidence = []
            
            for keyword in pad_keywords:
                if re.search(keyword, page_source, re.IGNORECASE):
                    found_pad = True
                    # Find the context around the keyword
                    matches = re.finditer(keyword, page_source, re.IGNORECASE)
                    for match in matches:
                        start = max(0, match.start() - 100)
                        end = min(len(page_source), match.end() + 100)
                        context = page_source[start:end].replace('\n', ' ').strip()
                        # Filter out CSS/HTML noise
                        if not any(css_noise in context.lower() for css_noise in ['padding', 'margin', 'border', 'background', 'color', 'font']):
                            pad_evidence.append(f"Found '{keyword}' in context: ...{context}...")
            
            # Extract document links
            document_links = extract_document_links(driver, project_id)
            
            if found_pad:
                print(f"✅ PAD FOUND in {project_id}")
                for evidence in pad_evidence[:2]:  # Show first 2 pieces of evidence
                    print(f"   {evidence}")
                if document_links:
                    print(f"   📄 Found {len(document_links)} potential document links")
                return True, pad_evidence, document_links
            else:
                print(f"❌ No PAD found in {project_id}")
                return False, [], document_links
                
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Error checking {project_id}: {str(e)}")
        return False, [], []

def read_csv_urls(filename):
    """Read URLs from the CSV file"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('project_url'):
                    project_id = row.get('Identifier', 'Unknown')
                    urls.append((project_id, row['project_url']))
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
    return urls

def main():
    # Read URLs from CSV
    csv_filename = "afdb_full_extraction_with_keywords.csv"
    all_urls = read_csv_urls(csv_filename)
    
    print(f"Found {len(all_urls)} URLs in CSV file")
    
    # Process all URLs in the CSV file
    urls_to_check = all_urls
    
    print(f"Checking all {len(urls_to_check)} AfDB project URLs for Project Appraisal Documents...")
    print("=" * 80)
    
    results = []
    document_links_all = []
    errors = []
    
    for i, (project_id, url) in enumerate(urls_to_check, 1):
        print(f"\n[{i}/{len(urls_to_check)}] ", end="")
        
        try:
            has_pad, evidence, document_links = check_for_pad(url, project_id)
            
            results.append({
                'project_id': project_id,
                'url': url,
                'has_pad': has_pad,
                'evidence': evidence
            })
            
            if document_links:
                document_links_all.extend(document_links)
                
        except Exception as e:
            print(f"❌ Error processing {project_id}: {str(e)}")
            errors.append({
                'project_id': project_id,
                'url': url,
                'error': str(e)
            })
            results.append({
                'project_id': project_id,
                'url': url,
                'has_pad': False,
                'evidence': [],
                'error': str(e)
            })
        
        # Add a small delay to be respectful to the server
        time.sleep(1)
        
        # Save progress every 50 URLs
        if i % 50 == 0:
            print(f"\n--- Progress saved at {i} URLs ---")
            with open(f'pad_results_progress_{i}.json', 'w') as f:
                json.dump(results, f, indent=2)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY OF RESULTS:")
    print("=" * 80)
    
    projects_with_pad = [r for r in results if r['has_pad']]
    projects_without_pad = [r for r in results if not r['has_pad']]
    
    print(f"Projects WITH Project Appraisal Documents: {len(projects_with_pad)}")
    for project in projects_with_pad:
        print(f"  ✅ {project['project_id']}")
    
    print(f"\nProjects WITHOUT Project Appraisal Documents: {len(projects_without_pad)}")
    for project in projects_without_pad:
        print(f"  ❌ {project['project_id']}")
    
    print(f"\nTotal projects checked: {len(results)}")
    print(f"Success rate: {len(projects_with_pad)/len(results)*100:.1f}%")
    
    # Save results to files
    with open('pad_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    with open('document_links.json', 'w') as f:
        json.dump(document_links_all, f, indent=2)
    
    print(f"\nResults saved to pad_results.json and document_links.json")
    
    # Save errors if any
    if errors:
        with open('pad_errors.json', 'w') as f:
            json.dump(errors, f, indent=2)
        print(f"Errors saved to pad_errors.json ({len(errors)} errors)")
    
    # Show some document links
    if document_links_all:
        print(f"\nSample document links found:")
        for link in document_links_all[:10]:
            print(f"  📄 {link['project_id']}: {link['text']} -> {link['url']}")
    
    print(f"\nTotal document links found: {len(document_links_all)}")

if __name__ == "__main__":
    main()
