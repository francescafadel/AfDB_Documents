# AfDB Documents Analysis

This repository contains a comprehensive analysis of Project Appraisal Documents (PADs) from the African Development Bank (AfDB) project portfolio.

## Overview

The analysis examined **1,109 AfDB projects** to identify which ones have Project Appraisal Documents (PADs) available online. This research provides insights into AfDB's transparency practices and document availability.

## Key Findings

- **Total Projects Analyzed**: 1,109
- **Projects WITH PADs**: 417 (37.6%)
- **Projects WITHOUT PADs**: 692 (62.4%)

## Files Description

### Analysis Results
- `pad_results.json` - Complete analysis results for all 1,109 projects
- `document_links.json` - Direct links to available PAD documents
- `PAD_Analysis_Report.md` - Detailed analysis report (covers initial 50 projects)

### Data Source
- `afdb_full_extraction_with_keywords.csv` - Source data containing 1,733 AfDB project records with extracted keywords

### Analysis Scripts
- `check_all_pads.py` - Main analysis script for checking PAD availability
- `fast_pad_check.py` - Optimized version for faster processing
- `continue_analysis.py` - Script for resuming interrupted analysis

### Progress Tracking
Multiple progress files showing batch processing results:
- `pad_results_progress_*.json` - Incremental results from batch processing

## Methodology

1. **Automated Web Scraping**: Used Selenium WebDriver to access project pages
2. **Keyword Detection**: Searched for specific terms like "appraisal report", "project appraisal document", etc.
3. **Evidence Collection**: Captured contextual evidence of PAD presence
4. **Document Link Extraction**: Identified actual document download links

## Usage

### Running the Analysis
```bash
python check_all_pads.py
```

### Fast Analysis (for testing)
```bash
python fast_pad_check.py
```

## Results Summary

The analysis reveals that approximately **37.6% of AfDB projects have PADs available online**, indicating room for improvement in transparency and document accessibility. The findings suggest that:

- Emergency/Humanitarian projects have higher PAD availability
- Infrastructure projects show good PAD coverage
- Some agricultural and technical assistance projects lack PADs
- PADs are often available in multiple languages (English and French)

## Technical Notes

- Analysis successfully processed 1,109 out of 1,109 URLs (100% success rate)
- Evidence collection provides confidence in PAD detection accuracy
- Results include both successful and failed URL access attempts

## Repository Structure

```
AfDB Documents/
├── README.md                           # This file
├── .gitignore                          # Git ignore rules
├── afdb_full_extraction_with_keywords.csv  # Source data
├── pad_results.json                    # Complete analysis results
├── document_links.json                 # PAD document links
├── PAD_Analysis_Report.md              # Analysis report
├── check_all_pads.py                   # Main analysis script
├── fast_pad_check.py                   # Fast analysis script
├── continue_analysis.py                # Resume analysis script
└── pad_results_progress_*.json         # Progress tracking files
```

## Contributing

This analysis provides a foundation for further research on AfDB project documentation practices. Future work could include:

1. Content analysis of available PADs
2. Investigation of projects missing PADs
3. Temporal analysis of PAD availability trends
4. Comparative analysis with other development banks

## License

This project is for research purposes. Please respect AfDB's terms of service when accessing their website.
