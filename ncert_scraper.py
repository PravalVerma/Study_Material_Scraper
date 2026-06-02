import os
import re
import urllib.request
import ssl
from scraper import BaseScraper
from config import NCERT_URL, ROOT_OUTPUT_PATH
from utils import get_logger, clean_filename

logger = get_logger("ncert_scraper")

# Languages to EXCLUDE — everything except English and Hindi
EXCLUDED_LANGUAGES = [
    'urdu', 'marathi', 'sindhi', 'punjabi', 'gujarati', 'gujrati',
    'malayalam', 'konkani', 'assamese', 'maithili', 'maithli', 'bodo',
    'sanskrit', 'oriya', 'odia', 'bengali', 'santhali', 'manipuri',
    'nepali', 'telugu', 'kannada', 'tamil', 'dogri', 'kashmiri',
    'marathi', 'santhali', 'sindhi',
]

# Subjects to skip entirely — not needed by the user
EXCLUDED_SUBJECTS = [
    'physical education and well being',
    'physical education',
    'health and physical education',
    'arts',
    'graphics design',
    'graphic design',
    'new age graphics design',
    'sangeet',
    'vocational education',
    'vocational',
    'heritage crafts',
    'fine art',
    'creative writing and translation',
    'creative writing & translation',
    'knowledge traditions practices of india',
    'computers and communication technology',
]

def _is_excluded(title: str, subject: str) -> bool:
    """Returns True if the book/subject should be excluded."""
    title_lower = title.lower()
    subject_lower = subject.lower()
    
    # Skip unwanted subjects entirely
    if subject_lower in EXCLUDED_SUBJECTS:
        return True
    
    # Skip if the subject itself is an excluded language (e.g., Subject = "Urdu")
    if subject_lower in EXCLUDED_LANGUAGES:
        return True
    
    # Skip if the title contains a language name in parentheses
    # This catches both regional languages AND Hindi/English editions of other subjects
    # e.g., "Ganita Prakash (Hindi)", "Bansuri - I (Hindi)", "Joyful-Mathematics (English)"
    # Note: Actual Hindi textbooks don't have "(Hindi)" in their title — they have names
    # like "Sarangi", "Veena", "Aroh", "Vasant" etc.
    paren_match = re.search(r'\(([^)]+)\)', title)
    if paren_match:
        lang_in_paren = paren_match.group(1).strip().lower()
        if lang_in_paren in EXCLUDED_LANGUAGES or lang_in_paren == 'hindi' or lang_in_paren == 'english':
            return True
    
    # Also check for Urdu-specific title patterns  
    urdu_patterns = ['riyazi', 'iftedai', 'ibtedai', 'tajassus', 'sitaar', 
                     'shahnai', 'hamari hairat', 'riyazi mela',
                     'jismani taleem', 'muashre', 'khayal',
                     'tabiyaat', 'hayatiyaat', 'keemiya', 'takhleequi',
                     'nai aawaz', 'gulistan', 'khaiban', 'nawai',
                     'muwaslati', 'computer aur muwaslati',
                     'nafsiyaat', 'karobari', 'khatadari', 'insani ',
                     'siyasi', 'jamhuri', 'samajiyaat', 'mutala',
                     'mashiyat', 'hindustan mein', 'hindustan aur',
                     'hindustani aain', 'tareekh', 'gugrophiya',
                     'shum', 'aasri', 'door pass', 'door - pass',
                     'sab rang', 'apani juban', 'aapni zaban',
                     'hamare mazi', 'hamara mahol', 'wasail',
                     'jaan pahechan', 'gulzare', 'hisab',
                     'azadi ke bad', 'computer science - urdu',
                     'hindustan me dastkari']
    for pattern in urdu_patterns:
        if pattern in title_lower:
            return True
    
    return False


class NcertScraper(BaseScraper):
    def __init__(self):
        super().__init__("NCERT", NCERT_URL, "NCERT")

    def fetch_page_urllib(self):
        """Bypass standard requests fingerprinting using urllib and unverified SSL"""
        logger.info(f"Fetching {self.name} URL via urllib: {self.url}")
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            self.url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
                with open("ncert_html.txt", "w", encoding="utf-8") as f:
                    f.write(html)
                return html
        except Exception as e:
            logger.warning(f"Failed to fetch dynamically: {e}. Attempting to use local cache...")
            if os.path.exists("ncert_html.txt"):
                with open("ncert_html.txt", "r", encoding="utf-8") as f:
                    return f.read()
            raise e

    def run(self):
        html = self.fetch_page_urllib()
        
        # Extract only the active (non-commented) JavaScript
        # First, strip JS block comments /* ... */
        html_no_block_comments = re.sub(r'/\*.*?\*/', '', html, flags=re.DOTALL)
        # Strip single-line JS comments (lines starting with //)
        html_clean = re.sub(r'//[^\n]*', '', html_no_block_comments)
        
        # Now parse only the active code
        # Split by class+subject if-blocks
        blocks = re.split(r'if\s*\(\s*\(document\.test\.tclass\.value==', html_clean)
        
        for block in blocks[1:]:
            # Extract class and subject
            header_match = re.search(
                r'(\d+)\)\s*&&\s*\(document\.test\.tsubject\.options\[sind\]\.text=="([^"]+)"\)\)',
                block
            )
            if not header_match:
                continue
                
            class_val = header_match.group(1)
            subject = header_match.group(2).strip()
            
            # Only Classes 1–12
            try:
                class_num = int(class_val)
                if class_num < 1 or class_num > 12:
                    continue
            except ValueError:
                continue
                
            class_name = f"Class {class_num}"
            
            # Skip entire block if the subject is an excluded language
            if subject.lower() in EXCLUDED_LANGUAGES:
                continue
            
            # Extract book options: text and value pairs
            texts = dict(re.findall(
                r'document\.test\.tbook\.options\[(\d+)\]\.text="([^"]+)"', block
            ))
            # Extract values: idx -> book_code
            raw_values = re.findall(
                r'document\.test\.tbook\.options\[(\d+)\]\.value="textbook\.php\?([^=]+)=[^"]+"', block
            )
            values = {idx: code for idx, code in raw_values}
            
            for idx, title in texts.items():
                if idx not in values:
                    continue
                if title.startswith("..Select"):
                    continue
                    
                book_code = values[idx]
                    
                # Apply the language filter
                if _is_excluded(title, subject):
                    continue
                    
                clean_title = clean_filename(title)
                clean_subject = clean_filename(subject)
                
                # Build the ZIP URL
                zip_url = f"https://ncert.nic.in/textbook/pdf/{book_code}dd.zip"
                
                # Target folder: NCERT/Class X/Subject/
                dest_dir = os.path.join(self.output_dir, class_name, clean_subject)
                os.makedirs(dest_dir, exist_ok=True)
                
                # Temporary directory for zip extraction
                extract_dir = os.path.join(dest_dir, f"temp_{clean_title}")
                os.makedirs(extract_dir, exist_ok=True)
                
                zip_dest = os.path.join(extract_dir, f"{book_code}.zip")
                
                self.tasks.append({
                    "name": f"{class_name} - {subject} - {title}",
                    "url": zip_url,
                    "destination": zip_dest,
                    "extract_dir": extract_dir,
                    "final_dir": dest_dir,
                    "type": "ncert_zip",
                    "book_title": clean_title
                })
                    
        logger.info(f"NcertScraper found {len(self.tasks)} books (English & Hindi only).")
        return self.tasks
