import requests
import urllib3

urllib3.disable_warnings()

url = "https://www.upsc.gov.in/examinations/previous-question-papers"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

print(f"Fetching {url}...")
response = requests.get(url, headers=headers, verify=False, timeout=15)

with open('upsc_html.txt', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Saved to upsc_html.txt")
