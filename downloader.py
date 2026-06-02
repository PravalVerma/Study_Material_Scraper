import os
import time
import requests
import re
import zipfile
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from config import REQUEST_TIMEOUT, MAX_RETRIES, RATE_LIMIT_SECONDS, ENABLE_PARALLEL_DOWNLOADS, MAX_WORKERS, HEADERS
from utils import get_logger, proxy_rotator

logger = get_logger("downloader")

class Downloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.downloaded = 0
        self.failed = []

    def get_confirm_token(self, response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        if 'confirm=' in response.text:
            match = re.search(r'confirm=([0-9A-Za-z_]+)', response.text)
            if match:
                return match.group(1)
        return None

    def resolve_redirects(self, url):
        """Resolves any redirects (like Mathongo shortlinks) to get the final URL."""
        try:
            resp = self.session.head(url, allow_redirects=True, timeout=REQUEST_TIMEOUT, proxies=proxy_rotator.get_proxy())
            return resp.url
        except Exception as e:
            logger.error(f"Failed to resolve URL {url}: {e}")
            return url

    def download_google_drive(self, file_id, destination):
        URL = "https://drive.google.com/uc?export=download"
        
        for attempt in range(MAX_RETRIES):
            try:
                proxies = proxy_rotator.get_proxy()
                response = self.session.get(URL, params={'id': file_id}, stream=True, timeout=REQUEST_TIMEOUT, proxies=proxies)
                
                # Check for rate limits
                if response.status_code in [403, 429]:
                    logger.warning(f"Rate limited on {file_id}. Status: {response.status_code}. Attempt {attempt+1}/{MAX_RETRIES}")
                    time.sleep((attempt + 1) * 2) # Exponential backoff
                    continue

                response.raise_for_status()

                token = self.get_confirm_token(response)
                if token:
                    params = {'id': file_id, 'confirm': token}
                    response = self.session.get(URL, params=params, stream=True, timeout=REQUEST_TIMEOUT, proxies=proxies)
                    response.raise_for_status()

                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    # Google Drive might show an HTML error page (e.g. quota exceeded)
                    logger.error(f"HTML received instead of PDF for {file_id} (Quota Exceeded?)")
                    return False

                with open(destination, "wb") as f:
                    for chunk in response.iter_content(32768):
                        if chunk:
                            f.write(chunk)
                return True
            except requests.RequestException as e:
                logger.error(f"Download error on attempt {attempt+1} for {file_id}: {e}")
                time.sleep((attempt + 1) * 2)

        return False

    def download_standard(self, url, destination):
        """Downloads standard files like NCERT ZIPs with extended timeout for large files."""
        for attempt in range(MAX_RETRIES):
            try:
                proxies = proxy_rotator.get_proxy()
                response = self.session.get(
                    url, stream=True, timeout=120, proxies=proxies, verify=False
                )
                
                if response.status_code == 404:
                    logger.warning(f"404 Not Found: {url} - skipping permanently.")
                    return False
                
                if response.status_code in [403, 429]:
                    time.sleep((attempt + 1) * 3)
                    continue
                    
                response.raise_for_status()
                
                with open(destination, "wb") as f:
                    for chunk in response.iter_content(32768):
                        if chunk:
                            f.write(chunk)
                return True
            except Exception as e:
                logger.error(f"Download error on attempt {attempt+1} for {url}: {e}")
                if os.path.exists(destination):
                    os.remove(destination)
                time.sleep((attempt + 1) * 3)
        return False

    def process_file(self, task):
        destination = task['destination']
        name = task['name']
        
        # Resolve shortlink if needed
        file_id = task.get('file_id')
        if task.get('type') == 'mathongo_shortlink':
            url = task['url']
            final_url = self.resolve_redirects(url)
            from utils import extract_gdrive_id
            file_id = extract_gdrive_id(final_url)
            if not file_id:
                logger.error(f"Could not extract Google Drive ID from {final_url}")
                return False

        if task.get('type') == 'ncert_zip':
            extract_dir = task['extract_dir']
            final_dir = task.get('final_dir', extract_dir)
            book_title = task.get('book_title', name)
            final_pdf_path = os.path.join(final_dir, f"{book_title}.pdf")
            
            # Skip if merged PDF already exists
            if os.path.exists(final_pdf_path) and os.path.getsize(final_pdf_path) > 1024:
                logger.info(f"Skipping {name}, merged PDF already exists.")
                return True
                
            logger.info(f"Downloading NCERT Zip {name}...")
            if not ENABLE_PARALLEL_DOWNLOADS:
                time.sleep(RATE_LIMIT_SECONDS)
                
            success = self.download_standard(task['url'], destination)
            if success and os.path.exists(destination):
                # Extract zip
                try:
                    with zipfile.ZipFile(destination, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    os.remove(destination) # clean up zip
                    
                    # Merge extracted PDFs
                    try:
                        import fitz  # PyMuPDF
                        pdf_files = [f for f in os.listdir(extract_dir) if f.lower().endswith('.pdf')]
                        if pdf_files:
                            # Natural sort the files to ensure chapter 10 comes after chapter 9
                            import re
                            def natural_sort_key(s):
                                return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
                            
                            pdf_files.sort(key=natural_sort_key)
                            
                            merged_pdf = fitz.open()
                            for pdf_file in pdf_files:
                                pdf_path = os.path.join(extract_dir, pdf_file)
                                try:
                                    doc = fitz.open(pdf_path)
                                    merged_pdf.insert_pdf(doc)
                                    doc.close()
                                except Exception as e:
                                    logger.error(f"Error reading {pdf_path} for merging: {e}")
                                    
                            book_title = task.get('book_title', name)
                            temp_pdf_path = os.path.join(extract_dir, f"temp_merged_{book_title}.pdf")
                            merged_pdf.save(temp_pdf_path)
                            merged_pdf.close()
                            
                            # Clean up individual chapter PDFs
                            for pdf_file in pdf_files:
                                os.remove(os.path.join(extract_dir, pdf_file))
                                
                            # Rename temp to final name
                            if os.path.exists(final_pdf_path):
                                os.remove(final_pdf_path) # remove if exists from a previous failed run
                            os.rename(temp_pdf_path, final_pdf_path)
                                
                            # Remove the temporary extraction directory
                            try:
                                os.rmdir(extract_dir)
                            except OSError as e:
                                logger.warning(f"Could not remove temp dir {extract_dir}: {e}")
                                
                            logger.info(f"[SUCCESS] Downloaded, Extracted & Merged: {name}")
                        else:
                            logger.info(f"[SUCCESS] Downloaded & Extracted (No PDFs found to merge): {name}")
                    except ImportError:
                        logger.warning(f"PyMuPDF (fitz) not installed. Skipping merge for {name}.")
                        logger.info(f"[SUCCESS] Downloaded & Extracted: {name}")
                    except Exception as e:
                        logger.error(f"[ERROR] Failed to merge PDFs for {name}: {e}")
                        
                    return True
                except Exception as e:
                    logger.error(f"[ERROR] Failed to extract zip {name}: {e}")
                    if os.path.exists(destination):
                        os.remove(destination)
                    return False
            else:
                logger.error(f"[ERROR] Failed download: {name}")
                return False

        # Regular File Logic
        # Skip if already downloaded correctly
        if os.path.exists(destination) and os.path.getsize(destination) > 1024: # >1KB
            logger.info(f"Skipping {name}, already exists.")
            return True

        logger.info(f"Downloading {name}...")
        
        # Add rate limiting sleep if parallel is disabled
        if not ENABLE_PARALLEL_DOWNLOADS:
            time.sleep(RATE_LIMIT_SECONDS)

        if not file_id:
            logger.error(f"No file_id for {name}")
            return False

        success = self.download_google_drive(file_id, destination)
        
        if success:
            # Check size again to be sure
            if os.path.getsize(destination) > 1024:
                logger.info(f"[SUCCESS] Saved file: {name}")
                return True
            else:
                logger.error(f"[ERROR] Downloaded file is too small or empty: {name}")
                os.remove(destination)
                return False
        else:
            logger.error(f"[ERROR] Failed download: {name}")
            return False

    def download_all(self, tasks):
        logger.info(f"Starting download of {len(tasks)} files...")
        
        if ENABLE_PARALLEL_DOWNLOADS:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_task = {executor.submit(self.process_file, task): task for task in tasks}
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        success = future.result()
                        if success:
                            self.downloaded += 1
                        else:
                            self.failed.append(task['name'])
                    except Exception as exc:
                        logger.error(f"{task['name']} generated an exception: {exc}")
                        self.failed.append(task['name'])
        else:
            for task in tasks:
                success = self.process_file(task)
                if success:
                    self.downloaded += 1
                else:
                    self.failed.append(task['name'])

        return {
            "total_found": len(tasks),
            "downloaded": self.downloaded,
            "failed_files": self.failed
        }
