import requests
from bs4 import BeautifulSoup
import json

url = "https://ncert.nic.in/textbook.php?ln=en"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print(f"Fetching {url}")
try:
    resp = requests.get(url, headers=headers, verify=False, timeout=15) # ncert sometimes has weird SSL
    print(f"Status Code: {resp.status_code}")
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    # Let's find form elements
    forms = soup.find_all('form')
    print(f"Forms found: {len(forms)}")
    for form in forms:
        print(f"Form Action: {form.get('action')}, Method: {form.get('method')}")
        
    # Let's look for Select dropdowns
    selects = soup.find_all('select')
    print(f"\nSelect elements found: {len(selects)}")
    for select in selects:
        print(f"Select Name: {select.get('name')}, ID: {select.get('id')}")
        options = select.find_all('option')
        print(f"  Options count: {len(options)}")
        for opt in options[:5]: # print first 5 options
            print(f"    - {opt.get('value')}: {opt.text.strip()}")
            
    # Let's find script tags to see if there's ajax
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and ('ajax' in script.string.lower() or 'fetch' in script.string.lower() or 'jquery' in script.string.lower()):
            print("\nFound possible AJAX script block.")
            # print snippet of script
            print(script.string[:500])
            
except Exception as e:
    print(f"Error: {e}")
