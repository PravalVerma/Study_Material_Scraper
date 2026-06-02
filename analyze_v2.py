import requests
from bs4 import BeautifulSoup
import json

urls = {
    "JEE": "https://www.mathongo.com/iit-jee/jee-main-previous-year-question-paper",
    "NEET": "https://mystudycart.com/aipmt-past-year-papers-free-download"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

results = {}

for name, url in urls.items():
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.content, 'html.parser')
        links = soup.find_all('a')
        pdf_links = [link.get('href') for link in links if link.get('href') and ('.pdf' in link.get('href').lower() or 'drive.google.com' in link.get('href').lower())]
        
        sample_links = []
        for link in links:
            href = link.get('href')
            text = link.text.strip()
            if href and ('2023' in text or '2022' in text or '2021' in text or 'pdf' in href.lower() or 'download' in text.lower()):
                sample_links.append(f"[{text}] -> {href}")
                if len(sample_links) >= 15:
                    break
                    
        results[name] = {
            "status_code": resp.status_code,
            "total_links": len(links),
            "pdf_links_count": len(pdf_links),
            "sample_links": sample_links
        }
    except Exception as e:
        results[name] = {"error": str(e)}

with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)
