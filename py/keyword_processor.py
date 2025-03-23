import os
import re
import time
import random
import logging
from bs4 import BeautifulSoup
import html
from fake_useragent import UserAgent
import keyboard
from threading import Event, Lock
from typing import List
import requests

# Configure logging like scraper.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keyword_processor.log'),
        logging.StreamHandler()
    ]
)

class KeywordProcessor:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.last_request_time = time.time()
        self.request_delay = (1, 3)  # Shorter delay like scraper.py
        self.max_retries = 3
        self.stop_event = Event()
        self.keyboard_lock = Lock()
        self.results = []
        self.input_file = None

    def _get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }

    def _respect_rate_limit(self):
        """Add random delay between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay[0]:
            sleep_time = random.uniform(*self.request_delay)
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def extract_keywords(self, url: str) -> List[str]:
        """Extract keywords with retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                self._respect_rate_limit()
                
                response = self.session.get(
                    url, 
                    headers=self._get_headers(),
                    timeout=10,
                    cookies=self.session.cookies
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    keywords = set()  # Use set to avoid duplicates
                    
                    # Method 1: Advanced meta tag extraction
                    meta_tags = [
                        ('name', 'keywords'),
                        ('property', 'article:tag'),
                        ('property', 'og:keywords'),
                        ('name', 'news_keywords'),
                        ('name', 'sailthru.tags'),
                        ('name', 'article:tag'),
                        ('property', 'article:section'),
                        ('name', 'twitter:label1'),
                        ('name', 'twitter:label2'),
                        ('name', 'parsely-tags'),
                        ('property', 'video:tag')
                    ]
                    
                    for attr, value in meta_tags:
                        meta = soup.find('meta', {attr: value})
                        if meta and meta.get('content'):
                            keywords.update(k.strip().lower() for k in meta['content'].split(',') if k.strip())
                    
                    # Method 2: Expanded tag/category elements
                    tag_classes = ['tag', 'tags', 'category', 'categories', 'topic', 'topics',
                                'label', 'labels', 'keyword', 'keywords', 'genre', 'genres',
                                'subject', 'subjects', 'article-tag', 'post-tag']
                    tag_selectors = [f'.{cls}' for cls in tag_classes] + ['[data-tag]', '[data-tags]']
                    
                    for selector in tag_selectors:
                        for element in soup.select(selector):
                            if element.string and element.string.strip():
                                keywords.add(element.string.strip().lower())
                            if element.get('data-tag'):
                                keywords.add(element['data-tag'].strip().lower())
                    
                    # Method 3: Extract from schema.org metadata
                    for script in soup.find_all('script', type='application/ld+json'):
                        try:
                            import json
                            data = json.loads(script.string)
                            if isinstance(data, dict):
                                for key in ['keywords', 'genre', 'about', 'articleSection']:
                                    if key in data:
                                        if isinstance(data[key], list):
                                            keywords.update(k.strip().lower() for k in data[key] if k.strip())
                                        elif isinstance(data[key], str):
                                            keywords.update(k.strip().lower() for k in data[key].split(',') if k.strip())
                        except:
                            continue
                    
                    # Method 4: Breadcrumb navigation
                    for crumb in soup.find_all(['a', 'span'], class_=['breadcrumb', 'breadcrumbs', 'crumb']):
                        if crumb.string and crumb.string.strip():
                            keywords.add(crumb.string.strip().lower())
                    
                    # Method 5: Extract from URL path
                    from urllib.parse import urlparse, unquote
                    path = urlparse(url).path
                    path_keywords = [k for k in path.split('/') if len(k) > 3 and k.isalnum()]
                    keywords.update(unquote(k.lower()) for k in path_keywords)
                    
                    # Process and filter keywords
                    processed_keywords = []
                    stopwords = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
                    
                    for kw in keywords:
                        # Split multi-word keywords if too long
                        if len(kw.split()) > 3:
                            parts = kw.split()
                            processed_keywords.extend(p for p in parts if len(p) > 3 and p not in stopwords)
                        else:
                            if len(kw) > 3 and not any(w in stopwords for w in kw.split()):
                                processed_keywords.append(kw)
                    
                    # Sort by relevance (frequency in page)
                    keyword_freq = {}
                    page_text = soup.get_text().lower()
                    for kw in processed_keywords:
                        keyword_freq[kw] = page_text.count(kw)
                    
                    final_keywords = sorted(list(set(processed_keywords)), 
                                        key=lambda x: keyword_freq[x], 
                                        reverse=True)[:7]
                    
                    # Fallback to title terms if no keywords found
                    if not final_keywords and soup.title:
                        title_words = [w.strip().lower() for w in soup.title.string.split() 
                                    if len(w.strip()) > 3 and w.strip().lower() not in stopwords]
                        final_keywords = title_words[:5]
                    
                    return final_keywords

            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                time.sleep(random.uniform(1, 3))
                continue
        return []

    def _setup_keyboard_handler(self):
        """Setup keyboard event handler"""
        def on_press(event):
            if event.name == 'q':
                with self.keyboard_lock:
                    if not self.stop_event.is_set():
                        print("\nStopping and saving progress...")
                        self.stop_event.set()

        keyboard.on_press(on_press)

    def _show_progress(self, current: int, total: int, url: str):
        """Show progress bar"""
        width = 50
        progress = int(width * current / total)
        print(f"\r[{'=' * progress}{' ' * (width - progress)}] {current}/{total} - {url[:50]}...", end='')

    def process_html_file(self, input_file: str, output_file: str = None):
        """Process HTML file and add keywords"""
        if not output_file:
            output_file = input_file
            
        self.input_file = input_file
        print("\nPress 'Q' at any time to stop and save progress\n")
        self._setup_keyboard_handler()

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            videos = soup.find_all('div', class_='video')
            total = len(videos)

            for idx, video in enumerate(videos, 1):
                if self.stop_event.is_set():
                    print("\nStopping as requested...")
                    break

                link = video.find('a')
                if not link or not link.get('href'):
                    continue

                url = link['href']
                self._show_progress(idx, total, url)

                if not video.find('div', class_='keywords'):
                    keywords = self.extract_keywords(url)
                    if keywords:
                        keywords_div = soup.new_tag('div', attrs={'class': 'keywords'})
                        for keyword in keywords:
                            span = soup.new_tag('span', attrs={'class': 'keyword'})
                            span.string = html.escape(keyword)
                            keywords_div.append(span)
                        video.append(keywords_div)

            # Save the modified HTML
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"\nDone! Saved to {output_file}")

        except Exception as e:
            logging.error(f"Error processing file: {e}")
        finally:
            keyboard.unhook_all()

    def __del__(self):
        """Clean up resources"""
        keyboard.unhook_all()

def main():
    processor = KeywordProcessor()
    
    print("\nKeyword Processor")
    print("================")
    
    while True:
        input_file = input("\nEnter path to HTML file: ").strip()
        if not os.path.exists(input_file):
            print("File not found. Please try again.")
            continue
            
        output_file = input("Enter output file path (or press Enter to overwrite): ").strip()
        if not output_file:
            output_file = input_file
            
        processor.process_html_file(input_file, output_file)
        
        if input("\nProcess another file? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main()
