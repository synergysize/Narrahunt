#!/usr/bin/env python3
"""
Main controller for Narrahunt Phase 2 recursive crawler.
Manages the crawl queue, fetches pages, and extracts Ethereum artifacts.
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime
from urllib.parse import urlparse

# Import crawler components
from modules.url_queue import URLQueue
from modules.fetch import fetch_page
from modules.crawl import extract_links
from modules.enhanced_artifact_detector import EnhancedArtifactDetector
from modules.utils import is_allowed_domain, is_allowed_by_robots

# Set up logging
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f'{base_dir}/results/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{base_dir}/results/logs/full_crawl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('narrahunt.main')

def load_config(config_path=f"{base_dir}/config/config.json"):
    """Load crawler configuration from file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        # Default configuration
        return {
            "crawl_delay": 2,
            "max_pages": 100,
            "max_depth": 3,
            "follow_redirects": True,
            "respect_robots": True
        }

def load_source_profiles(profiles_path=f"{base_dir}/source_profiles.json"):
    """Load source domain profiles."""
    try:
        with open(profiles_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading source profiles: {e}")
        # Default simple profile
        return {
            "ethereum.org": {
                "allowed": True,
                "seed_urls": ["https://ethereum.org/en/"]
            }
        }

def run_crawler(test_mode=False):
    """
    Main function to run the crawler.
    
    Args:
        test_mode: If True, run in test mode with fewer pages
    """
    # Load configuration
    config = load_config()
    source_profiles = load_source_profiles()
    
    # Initialize URL queue
    queue = URLQueue()
    
    # Initialize artifact detector
    detector = EnhancedArtifactDetector()
    
    # Add seed URLs to queue
    for domain, profile in source_profiles.items():
        if profile.get("allowed", False):
            for url in profile.get("seed_urls", []):
                queue.add_url(url, 0)
    
    # Start crawling
    max_pages = config.get("max_pages", 100)
    if test_mode:
        max_pages = min(max_pages, 10)
    
    logger.info(f"Starting crawl with max_pages={max_pages}")
    
    # Statistics tracking
    stats = {
        "pages_fetched": 0,
        "pages_failed": 0,
        "artifacts_found": 0,
        "start_time": datetime.now(),
        "end_time": None
    }
    
    # Create results directory
    results_dir = f"{base_dir}/results/artifacts"
    os.makedirs(results_dir, exist_ok=True)
    
    try:
        while not queue.is_empty() and stats["pages_fetched"] < max_pages:
            # Get next URL from queue
            url, depth = queue.next_url()
            
            if not url:
                logger.warning("Got empty URL from queue")
                continue
            
            # Log progress
            logger.info(f"Processing {url} (depth {depth})")
            
            # Check robots.txt
            if config.get("respect_robots", True) and not is_allowed_by_robots(url):
                logger.info(f"Skipping {url} - disallowed by robots.txt")
                continue
            
            # Fetch page
            try:
                html_content, fetch_info = fetch_page(url)
                stats["pages_fetched"] += 1
                
                if not html_content:
                    logger.warning(f"No content fetched from {url}")
                    continue
                
                # Extract artifacts
                artifacts = detector.extract_artifacts(html_content, url)
                
                if artifacts:
                    logger.info(f"Found {len(artifacts)} artifacts on {url}")
                    stats["artifacts_found"] += len(artifacts)
                    
                    # Save artifacts
                    domain = urlparse(url).netloc
                    filename = f"{results_dir}/{domain}_{stats['pages_fetched']}.json"
                    with open(filename, 'w') as f:
                        json.dump({
                            "url": url,
                            "fetch_time": fetch_info.get("date"),
                            "artifacts": artifacts
                        }, f, indent=2)
                
                # Extract links and add to queue if depth allows
                if depth < config.get("max_depth", 3):
                    links = extract_links(url, html_content)
                    
                    added_count = 0
                    for link in links:
                        # Check if domain is allowed
                        if is_allowed_domain(link, allowed_domains=list(source_profiles.keys())):
                            if queue.add_url(link, depth + 1):
                                added_count += 1
                    
                    logger.info(f"Added {added_count} new URLs to queue from {url}")
                
                # Respect crawl delay
                time.sleep(config.get("crawl_delay", 2))
                
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                stats["pages_failed"] += 1
                continue
            
            # Save queue state periodically
            if stats["pages_fetched"] % 10 == 0:
                queue.save_state()
                logger.info(f"Queue state saved: {queue.pending_count()} pending, {queue.visited_count()} visited")
    
    except KeyboardInterrupt:
        logger.info("Crawl interrupted by user")
    
    # Update stats
    stats["end_time"] = datetime.now()
    elapsed_seconds = (stats["end_time"] - stats["start_time"]).total_seconds()
    stats["elapsed_seconds"] = elapsed_seconds
    stats["pages_per_second"] = stats["pages_fetched"] / elapsed_seconds if elapsed_seconds > 0 else 0
    
    # Save queue state
    queue.save_state()
    
    # Save stats
    with open(f"{base_dir}/results/crawl_stats.json", 'w') as f:
        # Convert datetime objects to strings
        stats_copy = stats.copy()
        stats_copy["start_time"] = stats_copy["start_time"].isoformat()
        stats_copy["end_time"] = stats_copy["end_time"].isoformat()
        json.dump(stats_copy, f, indent=2)
    
    logger.info(f"Crawl completed. Processed {stats['pages_fetched']} pages, found {stats['artifacts_found']} artifacts")
    
    return stats

def main():
    """Entry point for the crawler."""
    parser = argparse.ArgumentParser(description='Narrahunt Phase 2 Crawler')
    parser.add_argument('--test', action='store_true', help='Run in test mode with fewer pages')
    args = parser.parse_args()
    
    run_crawler(test_mode=args.test)

if __name__ == "__main__":
    main()