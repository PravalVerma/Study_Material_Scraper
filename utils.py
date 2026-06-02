import os
import re
import logging
from urllib.parse import urlparse, parse_qs
from config import PROXIES_LIST

def get_logger(name="scraper"):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # File handler
        fh = logging.FileHandler('logs/scraper.log', encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger

def clean_filename(filename: str) -> str:
    """Removes invalid characters from a filename."""
    # Remove invalid characters: \ / : * ? " < > |
    cleaned = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Remove extra spaces
    cleaned = " ".join(cleaned.split())
    return cleaned

class ProxyRotator:
    def __init__(self, proxies: list):
        self.proxies = proxies
        self.index = 0
        
    def get_proxy(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.index]
        self.index = (self.index + 1) % len(self.proxies)
        return {"http": proxy, "https": proxy}

proxy_rotator = ProxyRotator(PROXIES_LIST)

def extract_gdrive_id(url: str) -> str:
    """Extracts Google Drive File ID from a URL."""
    # Pattern for /file/d/ID/view or /open?id=ID or /uc?id=ID
    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
        
    match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
        
    return None
