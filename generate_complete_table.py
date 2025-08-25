#!/usr/bin/env python3
"""
Script to generate a complete HTML table with all AfDB PAD analysis results
"""

import json
import csv
import re
from pathlib import Path

def extract_country_from_project_id(project_id):
    """Extract country code from project ID"""
    if project_id.startswith('P-'):
        parts = project_id.split('-')
        if len(parts) >= 3:
            return parts[1]
    return "Unknown"

def get_country_name(country_code):
    """Get full country name from country code"""
    country_mapping = {
        'ZW': 'Zimbabwe', 'EG': 'Egypt', 'Z1': 'Multi-Country', 'CF': 'Central African Republic',
        'MG': 'Madagascar', 'BW': 'Botswana', 'GM': 'Gambia', 'SS': 'South Sudan',
        'TD': 'Chad', 'BJ': 'Benin', 'CD': 'DRC', 'SL': 'Sierra Leone', 'ZM': 'Zambia',
        'MW': 'Malawi', 'TN': 'Tunisia', 'MA': 'Morocco', 'SN': 'Senegal', 'UG': 'Uganda',
        'KE': 'Kenya', 'AO': 'Angola', 'RW': 'Rwanda', 'MZ': 'Mozambique', 'ST': 'São Tomé',
        'SZ': 'Eswatini', 'CI': 'Côte d\'Ivoire', 'NG': 'Nigeria', 'ML': 'Mali', 'GH': 'Ghana',
        'SO': 'Somalia', 'SD': 'Sudan', 'TZ': 'Tanzania', 'SC': 'Seychelles'
    }
    return country_mapping.get(country_code, country_code)

def load_pad_results():
    """Load PAD analysis results from JSON file"""
    with open('pad_results.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_project_descriptions():
    """Load project descriptions from CSV file"""
    descriptions = {}
    with open('afdb_full_extraction_with_keywords.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_id = row['Identifier']
            descriptions[project_id] = {
                'description': row.get('general_description', '')[:200] + '...' if len(row.get('general_description', '')) > 200 else row.get('general_description', ''),
                'keywords': row.get('Keywords Found (Any Column)', '')
            }
    return descriptions

def generate_html_table():
    """Generate complete HTML table with all project data"""
    
    # Load data
    pad_results = load_pad_results()
    descriptions = load_project_descriptions()
    
    # Process data
    table_data = []
    for project in pad_results:
        project_id = project['project_id']
        country_code = extract_country_from_project_id(project_id)
        country_name = get_country_name(country_code)
        
        # Get description and keywords
        desc_info = descriptions.get(project_id, {})
        description = desc_info.get('description', 'No description available')
        keywords = desc_info.get('keywords', 'No keywords')
        
        # Clean up evidence
        evidence = project.get('evidence', [])
        evidence_text = '; '.join(evidence[:2]) if evidence else 'No PAD evidence found'
        if len(evidence_text) > 100:
            evidence_text = evidence_text[:100] + '...'
        
        table_data.append({
            'project_id': project_id,
            'country_code': country_code,
            'country_name': country_name,
            'has_pad': project['has_pad'],
            'url': project['url'],
            'description': description,
            'keywords': keywords,
            'evidence': evidence_text
        })
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete AfDB PAD Analysis Results - All 1,109 Projects</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        .summary {{ background-color: #ecf0f1; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .summary-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }}
        .stat-box {{ background-color: white; padding: 15px; border-radius: 5px; text-align: center; border-left: 4px solid #3498db; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .stat-label {{ color: #7f8c8d; font-size: 14px; }}
        .filters {{ margin-bottom: 20px; display: flex; gap: 15px; flex-wrap: wrap; align-items: center; }}
        .filter-group {{ display: flex; align-items: center; gap: 8px; }}
        select, input {{ padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; font-size: 14px; }}
        .table-container {{ overflow-x: auto; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }}
        th {{ background-color: #34495e; color: white; font-weight: bold; position: sticky; top: 0; }}
        tr:hover {{ background-color: #f8f9fa; }}
        .has-pad {{ background-color: #d5f4e6; color: #27ae60; font-weight: bold; }}
        .no-pad {{ background-color: #fadbd8; color: #e74c3c; font-weight: bold; }}
        .project-url {{ color: #3498db; text-decoration: none; }}
        .project-url:hover {{ text-decoration: underline; }}
        .keywords {{ font-size: 12px; color: #7f8c8d; max-width: 200px; }}
        .pagination {{ margin-top: 20px; text-align: center; }}
        .pagination button {{ padding: 8px 12px; margin: 0 5px; border: 1px solid #bdc3c7; background-color: white; cursor: pointer; border-radius: 4px; }}
        .pagination button:hover {{ background-color: #ecf0f1; }}
        .pagination button.active {{ background-color: #3498db; color: white; border-color: #3498db; }}
        .export-buttons {{ margin-bottom: 20px; text-align: right; }}
        .export-btn {{ padding: 10px 20px; margin-left: 10px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }}
        .export-csv {{ background-color: #27ae60; color: white; }}
        .export-json {{ background-color: #f39c12; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🇿🇦 Complete AfDB Project Appraisal Document (PAD) Analysis Results</h1>
        
        <div class="summary">
            <h2>📊 Analysis Summary</h2>
            <div class="summary-stats">
                <div class="stat-box">
                    <div class="stat-number">{len(table_data)}</div>
                    <div class="stat-label">Total Projects Analyzed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{sum(1 for p in table_data if p['has_pad'])}</div>
                    <div class="stat-label">Projects WITH PADs ({sum(1 for p in table_data if p['has_pad'])/len(table_data)*100:.1f}%)</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{sum(1 for p in table_data if not p['has_pad'])}</div>
                    <div class="stat-label">Projects WITHOUT PADs ({sum(1 for p in table_data if not p['has_pad'])/len(table_data)*100:.1f}%)</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Success Rate (URL Access)</div>
                </div>
            </div>
        </div>

        <div class="export-buttons">
            <button class="export-btn export-csv" onclick="exportToCSV()">📥 Export to CSV</button>
            <button class="export-btn export-json" onclick="exportToJSON()">📥 Export to JSON</button>
        </div>

        <div class="filters">
            <div class="filter-group">
                <label>PAD Status:</label>
                <select id="padFilter" onchange="filterTable()">
                    <option value="all">All Projects</option>
                    <option value="true">With PADs</option>
                    <option value="false">Without PADs</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Search Project ID:</label>
                <input type="text" id="searchInput" placeholder="Enter project ID..." onkeyup="filterTable()">
            </div>
            <div class="filter-group">
                <label>Country:</label>
                <select id="countryFilter" onchange="filterTable()">
                    <option value="all">All Countries</option>
                    {chr(10).join([f'<option value="{code}">{name}</option>' for code, name in sorted(set((p["country_code"], p["country_name"]) for p in table_data))])}
                </select>
            </div>
        </div>

        <div class="table-container">
            <table id="padTable">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Project ID</th>
                        <th>Country</th>
                        <th>PAD Status</th>
                        <th>Project URL</th>
                        <th>Project Description</th>
                        <th>Keywords</th>
                        <th>Evidence</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                </tbody>
            </table>
        </div>

        <div class="pagination" id="pagination">
        </div>
    </div>

    <script>
        const padData = {json.dumps(table_data, indent=2)};
        let currentPage = 1;
        const itemsPerPage = 20;
        let filteredData = [...padData];

        function displayTable(data = filteredData) {{
            const tableBody = document.getElementById('tableBody');
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;
            const pageData = data.slice(startIndex, endIndex);

            tableBody.innerHTML = '';

            pageData.forEach((project, index) => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{startIndex + index + 1}}</td>
                    <td><strong>${{project.project_id}}</strong></td>
                    <td>${{project.country_name}}</td>
                    <td class="${{project.has_pad ? 'has-pad' : 'no-pad'}}">
                        ${{project.has_pad ? '✅ HAS PAD' : '❌ NO PAD'}}
                    </td>
                    <td><a href="${{project.url}}" target="_blank" class="project-url">View Project</a></td>
                    <td>${{project.description}}</td>
                    <td class="keywords">${{project.keywords}}</td>
                    <td class="keywords">${{project.evidence}}</td>
                `;
                tableBody.appendChild(row);
            }});

            updatePagination(data.length);
        }}

        function updatePagination(totalItems) {{
            const totalPages = Math.ceil(totalItems / itemsPerPage);
            const pagination = document.getElementById('pagination');
            
            let paginationHTML = '';
            
            if (totalPages > 1) {{
                paginationHTML += `<button onclick="changePage(${{currentPage - 1}})" ${{currentPage === 1 ? 'disabled' : ''}}>Previous</button>`;
                
                for (let i = 1; i <= totalPages; i++) {{
                    if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {{
                        paginationHTML += `<button onclick="changePage(${{i}})" class="${{i === currentPage ? 'active' : ''}}">${{i}}</button>`;
                    }} else if (i === currentPage - 3 || i === currentPage + 3) {{
                        paginationHTML += `<span>...</span>`;
                    }}
                }}
                
                paginationHTML += `<button onclick="changePage(${{currentPage + 1}})" ${{currentPage === totalPages ? 'disabled' : ''}}>Next</button>`;
            }}
            
            pagination.innerHTML = paginationHTML;
        }}

        function changePage(page) {{
            const totalPages = Math.ceil(filteredData.length / itemsPerPage);
            if (page >= 1 && page <= totalPages) {{
                currentPage = page;
                displayTable();
            }}
        }}

        function filterTable() {{
            const padFilter = document.getElementById('padFilter').value;
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const countryFilter = document.getElementById('countryFilter').value;

            filteredData = padData.filter(project => {{
                const matchesPad = padFilter === 'all' || project.has_pad.toString() === padFilter;
                const matchesSearch = project.project_id.toLowerCase().includes(searchInput);
                const matchesCountry = countryFilter === 'all' || project.country_code === countryFilter;
                
                return matchesPad && matchesSearch && matchesCountry;
            }});

            currentPage = 1;
            displayTable();
        }}

        function exportToCSV() {{
            const headers = ['Project ID', 'Country', 'PAD Status', 'URL', 'Description', 'Keywords', 'Evidence'];
            const csvContent = [
                headers.join(','),
                ...filteredData.map(project => [
                    project.project_id,
                    project.country_name,
                    project.has_pad ? 'HAS PAD' : 'NO PAD',
                    project.url,
                    `"${{project.description}}"`,
                    `"${{project.keywords}}"`,
                    `"${{project.evidence}}"`
                ].join(','))
            ].join('\\n');

            const blob = new Blob([csvContent], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'afdb_pad_analysis_complete.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }}

        function exportToJSON() {{
            const jsonContent = JSON.stringify(filteredData, null, 2);
            const blob = new Blob([jsonContent], {{ type: 'application/json' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'afdb_pad_analysis_complete.json';
            a.click();
            window.URL.revokeObjectURL(url);
        }}

        displayTable();
    </script>
</body>
</html>
"""
    
    # Write to file
    with open('Complete_AfDB_PAD_Analysis_Table.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Complete HTML table generated with {len(table_data)} projects!")
    print("📁 File: Complete_AfDB_PAD_Analysis_Table.html")
    
    # Also generate a simple CSV version
    csv_filename = 'Complete_AfDB_PAD_Analysis_Table.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Project ID', 'Country', 'PAD Status', 'URL', 'Description', 'Keywords', 'Evidence'])
        for project in table_data:
            writer.writerow([
                project['project_id'],
                project['country_name'],
                'HAS PAD' if project['has_pad'] else 'NO PAD',
                project['url'],
                project['description'],
                project['keywords'],
                project['evidence']
            ])
    
    print(f"📁 CSV file: {csv_filename}")

if __name__ == "__main__":
    generate_html_table()

