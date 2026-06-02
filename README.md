# PYQ and NCERT Scraper

A Production-Grade Python Agent to automatically scrape and download Previous Year Question Papers (PYQs) for JEE Main and NEET, as well as official NCERT Textbooks for Classes I-XII.

## Features
- **Concurrent Downloading**: Uses `ThreadPoolExecutor` for fast downloads.
- **Proxy Rotation**: Built-in support to rotate proxies to bypass rate limits.
- **Google Drive Integration**: Custom logic to bypass Google Drive's "Large File" warning and download PDFs directly.
- **Resiliency**: Exponential backoff retries, duplicate detection, and content validation.
- **Reporting**: Generates a detailed JSON report upon completion.

## Folder Structure
```
PYQs/
├── JEE/
│   ├── JEE Main 2025/
│   ├── JEE Main 2024/
│   └── ...
├── NEET/
│   ├── NEET 2025/
│   ├── NEET 2024/
│   └── ...
NCERT/
├── Class 1/
│   ├── English/
│   │   ├── Mridang/
│   │   │   ├── Chapter 1.pdf
│   │   │   └── ...
│   └── Mathematics/
└── ...
```

## Setup & Installation

1. Install Python 3.11+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
Edit `config.py` to customize the behavior:
- `ROOT_OUTPUT_PATH`: Where to save the PDFs.
- `MAX_WORKERS`: Number of concurrent threads for downloading.
- `ENABLE_NCERT_DOWNLOADS`: Boolean to enable/disable NCERT.
- `PROXIES_LIST`: Add your HTTP/HTTPS proxies if you hit Google Drive rate limits. Example: `['http://user:pass@1.1.1.1:8080']`

## Usage
Run the main script with specific flags depending on what you want to download:

```bash
# Download NCERT Textbooks only
python main.py --ncert

# Download JEE Main PYQs only
python main.py --jee

# Download NEET PYQs only
python main.py --neet

# Download Everything
python main.py --all
```

The script will:
1. Parse Mathongo for JEE Main papers, Mystudycart for NEET, or the official NCERT portal depending on your flags.
2. Bypass TLS bot protections automatically.
3. Download all PDFs/ZIPs concurrently and extract them automatically.
4. Save logs to `logs/scraper.log`.
5. Generate a detailed `download_report.json`.
