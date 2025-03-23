import os
import re
import time
import random
import logging
import requests
import validators
import signal
from typing import List, Dict, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import webbrowser
import sys
from threading import Event, Lock

# Configure logging with path relative to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(script_dir, 'scraper.log')),
        logging.StreamHandler()
    ]
)

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.min_image_size = 5000
        self.domain_blacklist = ['google-analytics.com', 'facebook.com']
        self.last_request_time = 0
        self.request_delay = (1, 3)
        self.selenium_driver = None
        self.selenium_initialized = False
        self.stop_event = Event()
        self.results = []
        self.input_file = None  # Add this line to track input file name
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\nStopping and saving progress...")
        self.stop_event.set()

    def _init_selenium(self):
        """Initialize headless Chrome browser"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.ua.random}")
            
            service = Service(ChromeDriverManager().install())
            self.selenium_driver = webdriver.Chrome(service=service, options=chrome_options)
            self.selenium_initialized = True
            logging.info("Selenium driver initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Selenium: {e}")
            self.selenium_initialized = False

    def _get_headers(self):
        return {'User-Agent': self.ua.random}

    def _respect_ratelimit(self):
        current_time = time.time()
        time_passed = current_time - self.last_request_time
        if time_passed < self.request_delay[0]:
            time.sleep(random.uniform(*self.request_delay))
        self.last_request_time = time.time()

    def get_user_input(self) -> List[str]:
        """Get and validate user input"""
        print("\nWeb Scraper")
        print("===========")
        
        while True:
            input_type = input("\nEnter '1' for single URL or '2' for file: ")
            
            if input_type == '1':
                url = input("Enter URL: ").strip()
                return self._process_urls([url])
                
            elif input_type == '2':
                file_path = input("Enter file path: ").strip()
                try:
                    with open(file_path, 'r') as f:
                        urls = [line.strip() for line in f if line.strip()]
                    if not urls:
                        print("File is empty. Try again.")
                        continue
                    self.input_file = file_path  # Store the input file path
                    return self._process_urls(urls)
                except Exception as e:
                    print(f"Error reading file: {e}")
            else:
                print("Invalid choice. Enter 1 or 2.")

    def _process_urls(self, urls: List[str]) -> List[str]:
        processed = []
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            if validators.url(url):
                processed.append(url)
            else:
                logging.warning(f"Invalid URL: {url}")
        return processed

    def _selenium_fetch(self, url: str) -> Optional[str]:
        try:
            self._init_selenium()
            self.selenium_driver.get(url)
            WebDriverWait(self.selenium_driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return self.selenium_driver.page_source
        except Exception as e:
            logging.error(f"Selenium error for {url}: {str(e)}")
            return None

    def fetch_page(self, url: str) -> Optional[str]:
        self._respect_ratelimit()
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logging.warning(f"Requests failed for {url}, trying Selenium: {str(e)}")
        
        return self._selenium_fetch(url)

    def extract_metadata(self, url: str, html_content: str) -> Optional[Dict]:
        """Extract title, image, and keywords from page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Title extraction
            og_title = soup.find('meta', property='og:title')
            title = og_title['content'].strip()[:200] if og_title else None
            if not title and soup.title and soup.title.string:
                title = soup.title.string.strip()[:200]
            title = title or "Untitled"

            # Image extraction
            image_url = None
            meta_sources = [
                ('property', 'og:image'),
                ('name', 'twitter:image:src'),
                ('itemprop', 'image')
            ]
            for attr, value in meta_sources:
                meta = soup.find('meta', {attr: value})
                if meta and meta.get('content'):
                    image_url = urljoin(url, meta['content'])
                    break

            if not image_url:
                for img in soup.find_all('img', src=True):
                    src = urljoin(url, img['src'])
                    if self._is_valid_image(src):
                        image_url = src
                        break

            image_url = image_url or "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

            # Keywords extraction
            keywords = []
            meta_keywords = soup.find('meta', {'name': 'keywords'}) or soup.find('meta', {'property': 'article:tag'})
            if meta_keywords and meta_keywords.get('content'):
                keywords = [k.strip() for k in meta_keywords['content'].split(',') if k.strip()]
            
            # If no keywords found in meta tags, try to extract from tags or categories
            if not keywords:
                # Try to find tags/categories from common blog platforms
                for tag in soup.find_all(['a'], class_=['tag', 'category', 'tags', 'categories']):
                    if tag.string and tag.string.strip():
                        keywords.append(tag.string.strip())
            
            # Limit to first 5 keywords
            keywords = keywords[:5]

            return {
                'title': title,
                'image': image_url,
                'url': url,
                'domain': urlparse(url).netloc,
                'keywords': keywords
            }
        except Exception as e:
            logging.error(f"Error extracting metadata from {url}: {str(e)}")
            return None

    def _find_largest_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        largest_image = None
        max_size = 0

        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                img_url = urljoin(base_url, src)
                try:
                    response = self.session.head(img_url, headers=self._get_headers())
                    size = int(response.headers.get('content-length', 0))
                    if size > max_size and size > self.min_image_size:
                        max_size = size
                        largest_image = img_url
                except:
                    continue

        return largest_image

    def _show_progress(self, current: int, total: int, url: str):
        """Show progress bar"""
        width = 50
        progress = int(width * current / total)
        print(f"\r[{'=' * progress}{' ' * (width - progress)}] {current}/{total} - {url[:50]}", end='', flush=True)

    def scrape_urls(self, urls: List[str]) -> List[Dict]:
        self.results = []  # Reset results
        total = len(urls)
        
        print("\nPress Ctrl+C at any time to stop and save progress\n")
        
        try:
            for idx, url in enumerate(urls, 1):
                if self.stop_event.is_set():
                    print("\nStopping as requested...")
                    break
                
                self._show_progress(idx, total, url)
                content = self.fetch_page(url)
                if content:
                    metadata = self.extract_metadata(url, content)
                    if metadata:
                        self.results.append(metadata)
                        
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
        finally:
            if self.results and self.stop_event.is_set():
                temp_file = "temp_scrape_results.html"
                self.generate_html(self.results, temp_file)
                print(f"\nPartial results saved to {temp_file}")
                webbrowser.open(f'file://{os.path.abspath(temp_file)}')
            return self.results

    def generate_html(self, data: List[Dict], filename: str = 'output.html') -> str:
        """Generate HTML with video-style layout"""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Scraped Content</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .container {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .video {
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .video:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                .video img {
                    width: 100%;
                    height: 200px;
                    object-fit: cover;
                }
                .video-title {
                    padding: 15px;
                    margin: 0;
                    font-size: 16px;
                    color: #333;
                }
                .keywords {
                    padding: 0 15px 15px;
                    margin: 0;
                    font-size: 14px;
                    color: #666;
                }
                .keyword {
                    display: inline-block;
                    background: #f0f0f0;
                    padding: 3px 8px;
                    border-radius: 12px;
                    margin: 2px;
                }
            </style>
        </head>
        <body>
            <div class="container">
        """

        for item in data:
            keywords_html = ""
            if item.get('keywords'):
                keywords_html = '<div class="keywords">' + ''.join(
                    f'<span class="keyword">{html.escape(k)}</span>'
                    for k in item['keywords']
                ) + '</div>'

            html_content += f"""
            <div class="video">
                <a href="{html.escape(item['url'])}" target="_blank">
                    <img loading="lazy" src="{html.escape(item['image'])}" alt="{html.escape(item['title'])}">
                </a>
                <h2 class="video-title">{html.escape(item['title'])}</h2>
                {keywords_html}
            </div>
            """

        html_content += """
            </div>
        </body>
        </html>
        """

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filename

    def get_default_output_name(self) -> str:
        """Generate default output filename from input file"""
        if self.input_file:
            # Replace extension with .html or use the base name
            return os.path.splitext(self.input_file)[0] + '.html'
        return 'output.html'

    def __del__(self):
        if self.selenium_driver:
            self.selenium_driver.quit()

def main():
    scraper = WebScraper()
    urls = scraper.get_user_input()
    
    if not urls:
        logging.error("No valid URLs to process")
        return

    try:
        results = scraper.scrape_urls(urls)
        
        if results and not scraper.stop_event.is_set():
            default_name = scraper.get_default_output_name()
            output_file = input(f"\nOutput filename (default: {default_name}): ").strip() or default_name
            saved_file = scraper.generate_html(results, output_file)
            print(f"\nSuccess! Saved {len(results)} items to {saved_file}")
            webbrowser.open(f'file://{os.path.abspath(saved_file)}')
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
