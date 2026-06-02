import os
import requests
from bs4 import BeautifulSoup
import re
from config import JEE_URL, NEET_URL, ROOT_OUTPUT_PATH, HEADERS
from utils import get_logger, clean_filename, extract_gdrive_id

logger = get_logger("scraper")

class BaseScraper:
    def __init__(self, name, url, output_dir):
        self.name = name
        self.url = url
        self.output_dir = os.path.join(ROOT_OUTPUT_PATH, output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.tasks = []

    def fetch_page(self):
        logger.info(f"Fetching {self.name} URL: {self.url}")
        resp = requests.get(self.url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, 'html.parser')

    def run(self):
        raise NotImplementedError

class MathongoScraper(BaseScraper):
    def __init__(self):
        super().__init__("Mathongo (JEE)", JEE_URL, "JEE")

    def run(self):
        soup = self.fetch_page()
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href', '')
            if 'links.mathongo.com' in href:
                # The text is inside tr > td, so parent.parent gets the row text typically
                # or we can extract the text and regex it.
                row_text = link.parent.parent.text.strip()
                
                # e.g., "1JEE Main 2025 (22 Jan Shift 1) Previous Year PaperDownload PDF"
                # Remove leading digits
                name = re.sub(r'^\d+', '', row_text)
                # Remove trailing texts
                name = name.replace("Previous Year PaperDownload PDF", "").strip()
                name = name.replace("Download PDF", "").strip()
                
                # Fallback name if extraction is weird
                if not name or len(name) > 100:
                    name = f"JEE Main {len(self.tasks)+1}"
                
                filename = clean_filename(name) + ".pdf"
                
                # Create sub-directory for the year if possible (e.g., JEE Main 2025 -> JEE/JEE Main 2025/)
                match_year = re.search(r'(20\d{2})', name)
                year = match_year.group(1) if match_year else "Unknown Year"
                year_dir = os.path.join(self.output_dir, f"JEE Main {year}")
                os.makedirs(year_dir, exist_ok=True)
                
                destination = os.path.join(year_dir, filename)
                
                self.tasks.append({
                    "name": name,
                    "url": href, # Needs resolving in downloader
                    "destination": destination,
                    "type": "mathongo_shortlink"
                })
        
        logger.info(f"MathongoScraper found {len(self.tasks)} papers.")
        return self.tasks

class NeetScraper(BaseScraper):
    def __init__(self):
        super().__init__("Mystudycart (NEET)", NEET_URL, "NEET")

    def run(self):
        soup = self.fetch_page()
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href', '')
            if 'drive.google.com' in href:
                parent_text = link.parent.text.strip()
                
                # e.g., "NEET 2025 Question Paper : Download PDF"
                name = parent_text.split(':')[0].strip()
                name = name.replace("Download PDF", "").strip()
                
                if not name or len(name) > 100 or 'AIPMT' not in name.upper() and 'NEET' not in name.upper():
                    # Check if text inside anchor is better
                    anchor_text = link.text.strip()
                    if anchor_text and ('NEET' in anchor_text.upper() or 'AIPMT' in anchor_text.upper()):
                        name = anchor_text
                    else:
                        continue # Probably not a paper
                
                filename = clean_filename(name) + ".pdf"
                
                # Create sub-directory for the year
                match_year = re.search(r'(20\d{2}|19\d{2})', name)
                year = match_year.group(1) if match_year else "Unknown Year"
                year_dir = os.path.join(self.output_dir, f"NEET {year}")
                os.makedirs(year_dir, exist_ok=True)
                
                destination = os.path.join(year_dir, filename)
                
                # Extract Google Drive ID right away
                file_id = extract_gdrive_id(href)
                if not file_id:
                    continue
                
                self.tasks.append({
                    "name": name,
                    "file_id": file_id,
                    "destination": destination,
                    "type": "gdrive"
                })
                
        logger.info(f"NeetScraper found {len(self.tasks)} papers.")
        return self.tasks
