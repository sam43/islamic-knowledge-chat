"""
Enhanced Web Scraper with AI-powered content analysis
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
from pathlib import Path
import re
import os
from openai import OpenAI
from utils import print_success, print_error, print_info, print_warning

class WebScraper:
    def __init__(self):
        """Initialize the web scraper"""
        self.project_root = Path(__file__).parent
        self.scraped_dir = self.project_root / "scraped_content"
        self.scraped_dir.mkdir(exist_ok=True)
        
        # Initialize OpenAI client if available
        self.openai_client = None
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except Exception as e:
                print_warning(f"⚠️ Could not initialize OpenAI client: {e}")
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Session for connection reuse
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def clean_url(self, url):
        """Clean and validate URL"""
        if not url:
            return None
        
        # Remove leading/trailing whitespace
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slashes and spaces
        url = url.rstrip('/ ')
        
        return url

    def clean_text(self, text):
        """Clean and normalize scraped text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Cookie Policy|Privacy Policy|Terms of Service',
            r'Subscribe|Newsletter|Advertisement',
            r'Share your thoughts|Help us enhance',
            r'Download.*App|Get it on.*Store',
            r'Follow us on|Social Media',
            r'Copyright.*Reserved|All Rights Reserved'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()

    def ai_analyze_content(self, content, url):
        """Use AI to analyze and filter content quality"""
        if not self.openai_client or not content:
            return {
                'is_quality': True,
                'is_islamic': False,
                'confidence': 0.5,
                'summary': 'AI analysis not available'
            }
        
        try:
            prompt = f"""
Analyze this web content and determine:

1. Content Quality (0-1): Is this educational/informative content vs gibberish/ads/navigation?
2. Islamic Content (true/false): Does this contain Islamic knowledge (Quran, Hadith, Islamic practices)?
3. Confidence (0-1): How confident are you in this analysis?
4. Brief Summary: What is this content about?

Content to analyze:
{content[:2000]}...

Respond in JSON format:
{{
    "is_quality": true/false,
    "is_islamic": true/false, 
    "confidence": 0.0-1.0,
    "summary": "brief description"
}}
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert content analyst specializing in Islamic knowledge and web content quality assessment."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                if r'\`\`\`json' in ai_response:
                    ai_response = ai_response.split(r'\`\`\`json')[1].split(r'\`\`\`')[0]
                elif r'\`\`\`' in ai_response:
                    ai_response = ai_response.split(r'\`\`\`')[1]
   
                import json
                analysis = json.loads(ai_response)
                
                return {
                    'is_quality': analysis.get('is_quality', True),
                    'is_islamic': analysis.get('is_islamic', False),
                    'confidence': analysis.get('confidence', 0.5),
                    'summary': analysis.get('summary', 'Content analyzed')
                }
                
            except json.JSONDecodeError:
                print_warning("⚠️ Could not parse AI analysis response")
                return {
                    'is_quality': True,
                    'is_islamic': 'islamic' in content.lower() or 'quran' in content.lower(),
                    'confidence': 0.3,
                    'summary': 'AI parsing failed, using fallback'
                }
                
        except Exception as e:
            print_warning(f"⚠️ AI analysis failed: {e}")
            return {
                'is_quality': True,
                'is_islamic': False,
                'confidence': 0.2,
                'summary': f'AI analysis error: {str(e)}'
            }

    def detect_islamic_content(self, text):
        """Detect Islamic content using keyword matching and patterns"""
        islamic_keywords = [
            # Arabic terms
            'allah', 'muhammad', 'quran', 'qur\'an', 'hadith', 'hadis', 'sunnah',
            'islam', 'muslim', 'islamic', 'prophet', 'messenger',
            
            # Religious concepts
            'salah', 'prayer', 'zakat', 'charity', 'hajj', 'pilgrimage', 'sawm', 'fasting',
            'shahada', 'faith', 'iman', 'tawhid', 'shirk',
            
            # Sources
            'bukhari', 'muslim', 'abu dawood', 'tirmidhi', 'nasa\'i', 'ibn majah',
            'sahih', 'sunan', 'jami', 'musnad',
            
            # Quranic terms
            'surah', 'ayah', 'verse', 'chapter', 'revelation',
            
            # Islamic practices
            'mosque', 'masjid', 'imam', 'khutbah', 'dua', 'dhikr',
            'halal', 'haram', 'makruh', 'mustahab', 'fiqh', 'sharia'
        ]
        
        text_lower = text.lower()
        
        # Count Islamic keywords
        islamic_score = 0
        total_words = len(text.split())
        
        for keyword in islamic_keywords:
            count = text_lower.count(keyword)
            islamic_score += count
        
        # Calculate Islamic content ratio
        islamic_ratio = islamic_score / max(total_words, 1) * 100
        
        # Detect Quranic references (e.g., 2:255, Surah Al-Baqarah)
        quran_patterns = [
            r'\b\d{1,3}:\d{1,3}\b',  # 2:255 format
            r'surah\s+[\w\-]+',       # Surah names
            r'chapter\s+\d+',        # Chapter numbers
        ]
        
        quran_refs = 0
        for pattern in quran_patterns:
            quran_refs += len(re.findall(pattern, text_lower))
        
        # Detect Hadith references
        hadith_patterns = [
            r'sahih\s+(bukhari|muslim)',
            r'sunan\s+(abu\s+dawood|tirmidhi|nasa\'?i|ibn\s+majah)',
            r'jami\s+tirmidhi',
            r'musnad\s+ahmad'
        ]
        
        hadith_refs = 0
        for pattern in hadith_patterns:
            hadith_refs += len(re.findall(pattern, text_lower))
        
        return {
            'is_islamic': islamic_ratio > 0.5 or quran_refs > 0 or hadith_refs > 0,
            'islamic_score': islamic_ratio,
            'quran_references': quran_refs,
            'hadith_references': hadith_refs,
            'total_islamic_keywords': islamic_score
        }

    def extract_content(self, soup, url):
        """Extract meaningful content from BeautifulSoup object"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'noscript', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Get title
        title = soup.find('title')
        title_text = self.clean_text(title.get_text()) if title else ""
        
        # Extract all meaningful text content
        content_parts = []
        
        if title_text:
            content_parts.append(f"Title: {title_text}")
        
        # Get all text from body with better selectors
        body = soup.find('body')
        if not body:
            body = soup
        
        # Extract text from various elements with priority
        priority_selectors = [
            'main', 'article', '.content', '.main-content', 
            '.post-content', '.entry-content', '#content', '#main'
        ]
        
        main_content = None
        for selector in priority_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = body
        
        # Extract text from meaningful elements
        for element in main_content.find_all(['p', 'div', 'span', 'article', 'section', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'blockquote']):
            text = self.clean_text(element.get_text())
            if text and len(text) > 15:  # Minimum meaningful length
                content_parts.append(text)
        
        # If still no content, get all text
        if len(content_parts) <= 1:
            all_text = self.clean_text(main_content.get_text())
            if all_text:
                content_parts.append(all_text)
        
        # Join content
        full_content = '\n\n'.join(content_parts)
        
        return full_content

    def scrape_url(self, url, max_pages=1, islamic_only=False, use_ai_analysis=True):
        """Scrape content from a single URL or multiple pages with AI analysis"""
        try:
            # Clean URL
            url = self.clean_url(url)
            if not url:
                return {
                    'success': False,
                    'message': 'Invalid URL provided',
                    'content': '',
                    'analysis': None
                }
            
            print_info(f"🌐 Starting to scrape: {url}")
            
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    'success': False,
                    'message': 'Invalid URL format',
                    'content': '',
                    'analysis': None
                }
            
            all_content = []
            urls_to_scrape = [url]
            scraped_urls = set()
            
            for current_url in urls_to_scrape[:max_pages]:
                if current_url in scraped_urls:
                    continue
                
                try:
                    print_info(f"📄 Scraping page: {current_url}")
                    
                    # Make request with better error handling
                    response = self.session.get(current_url, timeout=15, allow_redirects=True)
                    
                    # Handle different HTTP status codes
                    if response.status_code == 404:
                        print_warning(f"⚠️ Page not found (404): {current_url}")
                        continue
                    elif response.status_code == 403:
                        print_warning(f"⚠️ Access forbidden (403): {current_url}")
                        continue
                    elif response.status_code >= 400:
                        print_warning(f"⚠️ HTTP {response.status_code}: {current_url}")
                        continue
                    
                    response.raise_for_status()
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    if 'text/html' not in content_type:
                        print_warning(f"⚠️ Skipping non-HTML content: {content_type}")
                        continue
                    
                    # Parse HTML with fallback parsers
                    try:
                        soup = BeautifulSoup(response.content, 'lxml')
                    except:
                        try:
                            soup = BeautifulSoup(response.content, 'html.parser')
                        except:
                            soup = BeautifulSoup(response.content, 'html5lib')
                    
                    # Extract content
                    content = self.extract_content(soup, current_url)
                    
                    if content and len(content.strip()) > 100:
                        # AI-powered content analysis
                        if use_ai_analysis and self.openai_client:
                            ai_analysis = self.ai_analyze_content(content, current_url)
                            
                            # Skip low-quality content if AI says so
                            if not ai_analysis['is_quality'] and ai_analysis['confidence'] > 0.7:
                                print_info(f"⏭️ Skipping low-quality content from {current_url}")
                                continue
                        else:
                            ai_analysis = None
                        
                        # Traditional Islamic content detection
                        islamic_analysis = self.detect_islamic_content(content)
                        
                        # Combine AI and traditional analysis
                        combined_islamic = islamic_analysis['is_islamic']
                        if ai_analysis:
                            combined_islamic = combined_islamic or ai_analysis['is_islamic']
                        
                        # If Islamic filter is on, only keep Islamic content
                        if islamic_only and not combined_islamic:
                            print_info(f"⏭️ Skipping non-Islamic content from {current_url}")
                            continue
                        
                        # Add metadata
                        metadata = f"""
URL: {current_url}
Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Content Length: {len(content)} characters
"""
                        if ai_analysis:
                            metadata += f"AI Quality Score: {ai_analysis['confidence']:.2f}\n"
                            metadata += f"AI Summary: {ai_analysis['summary']}\n"
                        
                        metadata += f"Islamic Score: {islamic_analysis['islamic_score']:.1f}%\n"
                        metadata += f"Quran References: {islamic_analysis['quran_references']}\n"
                        metadata += f"Hadith References: {islamic_analysis['hadith_references']}\n"
                        metadata += "---\n\n"
                        
                        full_content = metadata + content
                        
                        all_content.append({
                            'content': full_content,
                            'url': current_url,
                            'islamic_analysis': islamic_analysis,
                            'ai_analysis': ai_analysis
                        })
                        scraped_urls.add(current_url)
                    
                    # Find additional pages if max_pages > 1
                    if len(urls_to_scrape) < max_pages:
                        links = soup.find_all('a', href=True)
                        for link in links[:20]:
                            href = link['href']
                            full_url = urljoin(current_url, href)
                            
                            # Clean the discovered URL
                            full_url = self.clean_url(full_url)
                            
                            # Only add links from same domain
                            if (full_url and 
                                urlparse(full_url).netloc == parsed_url.netloc and 
                                full_url not in urls_to_scrape and 
                                full_url not in scraped_urls):
                                urls_to_scrape.append(full_url)
                    
                    # Respectful delay
                    time.sleep(1)
                    
                except requests.exceptions.RequestException as e:
                    print_warning(f"⚠️ Failed to scrape {current_url}: {e}")
                    continue
                except Exception as e:
                    print_warning(f"⚠️ Unexpected error scraping {current_url}: {e}")
                    continue
            
            if not all_content:
                return {
                    'success': False,
                    'message': 'No content could be extracted from the URL(s). The page might not exist, be blocked, or contain no meaningful content.',
                    'content': '',
                    'analysis': None
                }
            
            # Combine all content
            combined_content = ""
            total_islamic_score = 0
            total_quran_refs = 0
            total_hadith_refs = 0
            ai_quality_scores = []
            
            for item in all_content:
                combined_content += f"\n\n{'='*80}\n\n" + item['content']
                
                analysis = item['islamic_analysis']
                total_islamic_score += analysis['islamic_score']
                total_quran_refs += analysis['quran_references']
                total_hadith_refs += analysis['hadith_references']
                
                if item['ai_analysis']:
                    ai_quality_scores.append(item['ai_analysis']['confidence'])
            
            # Overall analysis
            overall_analysis = {
                'is_islamic': total_islamic_score > 0 or total_quran_refs > 0 or total_hadith_refs > 0,
                'islamic_score': total_islamic_score / len(all_content),
                'quran_references': total_quran_refs,
                'hadith_references': total_hadith_refs,
                'pages_scraped': len(scraped_urls),
                'ai_enabled': use_ai_analysis and self.openai_client is not None,
                'avg_ai_quality': sum(ai_quality_scores) / len(ai_quality_scores) if ai_quality_scores else 0
            }
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = urlparse(url).netloc.replace('.', '_')
            filename = f"scraped_{domain}_{timestamp}.txt"
            output_file = self.scraped_dir / filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            ai_status = "🤖 AI-Enhanced" if overall_analysis['ai_enabled'] else "📝 Traditional"
            
            success_message = f"""
✅ Successfully scraped {len(scraped_urls)} page(s) {ai_status}
📁 Content saved to: {filename}
📊 Total content length: {len(combined_content):,} characters
🕌 Islamic content score: {overall_analysis['islamic_score']:.1f}%
📖 Quran references found: {total_quran_refs}
📚 Hadith references found: {total_hadith_refs}
"""
            
            if overall_analysis['ai_enabled']:
                success_message += f"🤖 Average AI quality score: {overall_analysis['avg_ai_quality']:.2f}\n"
            
            success_message += """
💡 Next steps:
1. Review the scraped content in the file
2. Use 'Process with AI' to format as training data
3. Or manually extract Q&A pairs for training
"""
            
            print_success(f"✅ Scraping completed: {filename}")
            
            return {
                'success': True,
                'message': success_message,
                'content': combined_content,
                'file_path': str(output_file),
                'analysis': overall_analysis
            }
            
        except Exception as e:
            error_message = f"Scraping failed: {str(e)}"
            print_error(f"❌ {error_message}")
            return {
                'success': False,
                'message': error_message,
                'content': '',
                'analysis': None
            }

    def scrape_multiple_urls(self, urls, max_pages_per_url=1, islamic_only=False):
        """Scrape content from multiple URLs"""
        all_results = []
        
        for url in urls:
            result = self.scrape_url(url, max_pages_per_url, islamic_only)
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