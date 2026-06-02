from bs4 import BeautifulSoup

with open('upsc_html.txt', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

targets = [
    "Civil Services (Preliminary) Examination",
    "Combined Defence Services Examination",
    "National Defence Academy and Naval Academy Examination"
]

results = {target: [] for target in targets}

# Find all tables
tables = soup.find_all('table')

for table in tables:
    caption = table.find('caption')
    if not caption:
        continue
        
    exam_name = caption.text.strip()
    
    # Check if this table is for one of our targets
    for target in targets:
        if target.lower() in exam_name.lower():
            links = []
            for a in table.find_all('a', href=True):
                href = a['href']
                if href.lower().endswith('.pdf'):
                    links.append(href)
            
            if links:
                results[target].append({
                    "exam_full_name": exam_name,
                    "links": links
                })

# Print results
total_pyqs = 0
for target in targets:
    print(f"\n--- {target} ---")
    count = len(results[target])
    print(f"Found {count} exam blocks.")
    for res in results[target]:
        print(f"  - {res['exam_full_name']}: {len(res['links'])} PDFs")
        total_pyqs += len(res['links'])

print(f"\nTotal PDF links found for requested exams on this page: {total_pyqs}")

# Check for pagination
pager = soup.find('ul', class_='pager')
if pager:
    pages = [a['href'] for a in pager.find_all('a', href=True) if 'page=' in a['href']]
    print(f"\nPagination found! Links: {set(pages)}")
    
    last_page = soup.find('li', class_='pager-last')
    if last_page and last_page.find('a'):
        print(f"Last Page URL: {last_page.find('a')['href']}")
else:
    print("\nNo standard pagination ul.pager found.")
