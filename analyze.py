import requests
from bs4 import BeautifulSoup

urls = {
    "JEE": "https://www.mathongo.com/iit-jee/jee-main-previous-year-question-paper",
    "NEET": "https://mystudycart.com/aipmt-past-year-papers-free-download"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

for name, url in urls.items():
    print(f"\n=====================================")
    print(f"--- Analyzing {name} ---")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {resp.status_code}")
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        links = soup.find_all('a')
        print(f"Total anchor tags: {len(links)}")
        
        pdf_links = [link.get('href') for link in links if link.get('href') and ('.pdf' in link.get('href').lower())]
        print(f"Direct PDF links found: {len(pdf_links)}")
        
        # Sample links
        print("Sample links:")
        count = 0
        for link in links:
            href = link.get('href')
            text = link.text.strip()
            if href and ('2023' in text or '2022' in text or '2021' in text or 'pdf' in href.lower() or 'download' in text.lower()):
                print(f"  [{text}] -> {href}")
                count += 1
                if count >= 10:
                    break
        
    except Exception as e:
        print(f"Error analyzing {name}: {e}")
