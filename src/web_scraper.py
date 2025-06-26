"""
Web Scraper for Islamic AI Fine-tuning Project
Scrapes website content and saves to text files
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
from pathlib import Path
import re
from utils import print_success, print_error, print_info, print_warning

class WebScraper:
    def __init__(self):
        """Initialize the web scraper"""
        self.project_root = Path(__file__).parent
        self.scraped_dir = self.project_root / "scraped_content"
        self.scraped_dir.mkdir(exist_ok=True)
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Session for connection reuse
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def clean_text(self, text):
        """Clean and normalize scraped text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common unwanted patterns
        text = re.sub(r'Cookie Policy|Privacy Policy|Terms of Service', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Subscribe|Newsletter|Advertisement', '', text, flags=re.IGNORECASE)
        
        return text

    def extract_content(self, soup, url):
        """Extract meaningful content from BeautifulSoup object"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
            element.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#content',
            '#main'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return ""
        
        # Extract text content
        content_parts = []
        
        # Get title
        title = soup.find('title')
        if title:
            content_parts.append(f"Title: {self.clean_text(title.get_text())}")
        
        # Get headings and paragraphs
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span']):
            text = self.clean_text(element.get_text())
            if text and len(text) > 20:  # Only include substantial text
                content_parts.append(text)
        
        # Join content with proper spacing
        full_content = '\n\n'.join(content_parts)
        
        # Add metadata
        metadata = f"""
URL: {url}
Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Content Length: {len(full_content)} characters

---

{full_content}
"""
        
        return metadata

    def scrape_url(self, url, max_pages=1):
        """Scrape content from a single URL or multiple pages"""
        try:
            print_info(f"🌐 Starting to scrape: {url}")
            
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    'success': False,
                    'message': 'Invalid URL format',
                    'content': ''
                }
            
            all_content = []
            urls_to_scrape = [url]
            scraped_urls = set()
            
            for current_url in urls_to_scrape[:max_pages]:
                if current_url in scraped_urls:
                    continue
                
                try:
                    print_info(f"📄 Scraping page: {current_url}")
                    
                    # Make request with timeout
                    response = self.session.get(current_url, timeout=10)
                    response.raise_for_status()
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    if 'text/html' not in content_type:
                        print_warning(f"⚠️ Skipping non-HTML content: {content_type}")
                        continue
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract content
                    content = self.extract_content(soup, current_url)
                    if content:
                        all_content.append(content)
                        scraped_urls.add(current_url)
                    
                    # Find additional pages if max_pages > 1
                    if len(urls_to_scrape) < max_pages:
                        links = soup.find_all('a', href=True)
                        for link in links[:10]:  # Limit link discovery
                            href = link['href']
                            full_url = urljoin(current_url, href)
                            
                            # Only add links from same domain
                            if (urlparse(full_url).netloc == parsed_url.netloc and 
                                full_url not in urls_to_scrape and 
                                full_url not in scraped_urls):
                                urls_to_scrape.append(full_url)
                    
                    # Be respectful - add delay between requests
                    time.sleep(1)
                    
                except requests.exceptions.RequestException as e:
                    print_warning(f"⚠️ Failed to scrape {current_url}: {e}")
                    continue
            
            if not all_content:
                return {
                    'success': False,
                    'message': 'No content could be extracted from the URL(s)',
                    'content': ''
                }
            
            # Combine all content
            combined_content = '\n\n' + '='*80 + '\n\n'.join(all_content)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = urlparse(url).netloc.replace('.', '_')
            filename = f"scraped_{domain}_{timestamp}.txt"
            output_file = self.scraped_dir / filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            success_message = f"""
✅ Successfully scraped {len(scraped_urls)} page(s)
📁 Content saved to: {filename}
📊 Total content length: {len(combined_content):,} characters

💡 Next steps:
1. Review the scraped content in the file
2. Extract relevant Islamic Q&A pairs
3. Use the manual data entry to add structured training examples
"""
            
            print_success(f"✅ Scraping completed: {filename}")
            
            return {
                'success': True,
                'message': success_message,
                'content': combined_content,
                'file_path': str(output_file)
            }
            
        except Exception as e:
            error_message = f"Scraping failed: {str(e)}"
            print_error(f"❌ {error_message}")
            return {
                'success': False,
                'message': error_message,
                'content': ''
            }

    def scrape_multiple_urls(self, urls, max_pages_per_url=1):
        """Scrape content from multiple URLs"""
        all_results = []
        
        for url in urls:
            result = self.scrape_url(url, max_pages_per_url)
            all_results.append(result)
            
            # Add delay between different domains
            time.sleep(2)
        
        return all_results

    def get_scraped_files(self):
        """Get list of all scraped files"""
        scraped_files = list(self.scraped_dir.glob("*.txt"))
        return sorted(scraped_files, key=lambda x: x.stat().st_mtime, reverse=True)

    def read_scraped_file(self, filename):
        """Read content from a scraped file"""
        file_path = self.scraped_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
