import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

url = "https://www.upsc.gov.in/examinations/previous-question-papers?field_exam_name_value=Civil+Services"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, verify=False, timeout=15)
soup = BeautifulSoup(response.text, 'html.parser')

tables = soup.find_all('table')
print(f"Found {len(tables)} tables after searching.")

count = 0
for table in tables:
    caption = table.find('caption')
    if caption:
        print(f"  - {caption.text.strip()}")
        count += 1
        
print(f"Total exams matched: {count}")
