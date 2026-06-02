import json
import os
import argparse
from scraper import MathongoScraper, NeetScraper
from ncert_scraper import NcertScraper
from downloader import Downloader
from utils import get_logger

logger = get_logger("main")

def main():
    parser = argparse.ArgumentParser(description="PYQ and NCERT Scraper Agent")
    parser.add_argument("--jee", action="store_true", help="Download JEE Main PYQs")
    parser.add_argument("--neet", action="store_true", help="Download NEET PYQs")
    parser.add_argument("--ncert", action="store_true", help="Download NCERT Textbooks")
    parser.add_argument("--all", action="store_true", help="Download Everything")
    args = parser.parse_args()

    logger.info("Starting PYQ & NCERT Scraper Agent...")
    
    scrapers = []
    if args.all or args.jee:
        scrapers.append(MathongoScraper())
    if args.all or args.neet:
        scrapers.append(NeetScraper())
    if args.all or args.ncert:
        scrapers.append(NcertScraper())
        
    if not scrapers:
        logger.error("No target selected. Use --jee, --neet, --ncert, or --all.")
        return
        
    all_tasks = []
    
    for scraper in scrapers:
        try:
            tasks = scraper.run()
            all_tasks.extend(tasks)
        except Exception as e:
            logger.error(f"Error running scraper {scraper.name}: {e}")
            
    if not all_tasks:
        logger.warning("No files found to download. Exiting.")
        return

    # Categorize tasks
    jee_tasks = [t for t in all_tasks if "mathongo" in t.get("type", "")]
    neet_tasks = [t for t in all_tasks if "gdrive" in t.get("type", "")]
    ncert_tasks = [t for t in all_tasks if "ncert" in t.get("type", "")]
    
    logger.info(f"Total JEE tasks: {len(jee_tasks)}")
    logger.info(f"Total NEET tasks: {len(neet_tasks)}")
    logger.info(f"Total NCERT tasks: {len(ncert_tasks)}")

    downloader = Downloader()
    
    report = downloader.download_all(all_tasks)
    
    # We need to manually calculate downloads per category since downloader groups them
    # But for a quick summary, we can just dump the tasks sizes
    report['jee_total_found'] = len(jee_tasks)
    report['neet_total_found'] = len(neet_tasks)
    report['ncert_total_found'] = len(ncert_tasks)
    
    report_path = "download_report.json"
    
    # Try to load existing report and append
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                old_report = json.load(f)
                old_report.update(report)
                report = old_report
        except Exception:
            pass

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    logger.info(f"Scraping complete. Downloaded {report['downloaded']} files.")
    logger.info(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
