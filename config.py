import os

# Root directory to save the downloaded PDFs
ROOT_OUTPUT_PATH = os.getenv("PYQ_OUTPUT_PATH", "./PYQs")

# Target URLs
JEE_URL = "https://www.mathongo.com/iit-jee/jee-main-previous-year-question-paper"
NEET_URL = "https://mystudycart.com/aipmt-past-year-papers-free-download"
NCERT_URL = "https://ncert.nic.in/textbook.php?ln=en"

# Scraping settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RATE_LIMIT_SECONDS = 1  # Delay between requests

# Parallel downloading
ENABLE_PARALLEL_DOWNLOADS = True
ENABLE_NCERT_DOWNLOADS = True
MAX_WORKERS = 4

# Common headers to avoid basic bot detection
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Proxy settings
# If rate limits are hit, populate this list with proxy URLs like:
# 'http://user:pass@192.168.1.1:8080'
PROXIES_LIST = []
