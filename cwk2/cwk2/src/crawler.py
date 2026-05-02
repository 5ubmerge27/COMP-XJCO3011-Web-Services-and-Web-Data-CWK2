"""
Web Crawler Module

This module provides functionality to crawl web pages from a target website
while respecting politeness constraints.
"""

import requests
from bs4 import BeautifulSoup
from typing import Set, Dict, List
from urllib.parse import urljoin, urlparse
import time
import re


class WebCrawler:
    """
    A web crawler that fetches and parses web pages.
    
    Attributes:
        base_url (str): The base URL to start crawling from
        politeness_delay (float): Delay in seconds between requests (default: 6)
        visited_urls (Set[str]): Set of URLs that have been visited
        pages (Dict[str, str]): Dictionary mapping URLs to their HTML content
    """
    
    def __init__(self, base_url: str, politeness_delay: float = 6.0):
        """
        Initialize the web crawler.
        
        Args:
            base_url: The starting URL for crawling
            politeness_delay: Seconds to wait between requests (default: 6)
        """
        self.base_url = base_url
        self.politeness_delay = politeness_delay
        self.visited_urls: Set[str] = set()
        self.pages: Dict[str, str] = {}
        self.last_request_time = 0.0
        
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid and belongs to the same domain.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if the URL is valid and from the same domain, False otherwise
        """
        try:
            parsed_base = urlparse(self.base_url)
            parsed_url = urlparse(url)
            
            # Check if same domain
            if parsed_url.netloc != parsed_base.netloc:
                return False
                
            # Avoid fragments and certain file types
            if parsed_url.fragment or url.endswith(('.pdf', '.jpg', '.png', '.gif')):
                return False
                
            return True
        except Exception:
            return False
    
    def _respect_politeness(self):
        """
        Ensure politeness delay is respected between requests.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.politeness_delay:
            sleep_time = self.politeness_delay - time_since_last_request
            print(f"Waiting {sleep_time:.2f} seconds (politeness delay)...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def fetch_page(self, url: str) -> str:
        """
        Fetch a single web page and return its HTML content.
        
        Args:
            url: The URL to fetch
            
        Returns:
            The HTML content of the page, or empty string if fetch fails
        """
        try:
            self._respect_politeness()
            
            print(f"Fetching: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def extract_links(self, html: str, current_url: str) -> List[str]:
        """
        Extract all valid links from an HTML page.
        
        Args:
            html: The HTML content to parse
            current_url: The URL of the current page (for resolving relative links)
            
        Returns:
            List of absolute URLs found in the page
        """
        links = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                # Convert relative URLs to absolute
                absolute_url = urljoin(current_url, href)
                
                # Remove trailing slashes for consistency
                absolute_url = absolute_url.rstrip('/')
                
                if self._is_valid_url(absolute_url):
                    links.append(absolute_url)
                    
        except Exception as e:
            print(f"Error extracting links: {e}")
        
        return links
    
    def extract_text(self, html: str) -> str:
        """
        Extract clean text content from HTML.
        
        Args:
            html: The HTML content to parse
            
        Returns:
            Cleaned text content from the page
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'meta', 'link']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def crawl(self, max_pages: int = 50) -> Dict[str, str]:
        """
        Crawl the website starting from the base URL.
        
        Args:
            max_pages: Maximum number of pages to crawl (default: 50)
            
        Returns:
            Dictionary mapping URLs to their text content
        """
        to_visit = [self.base_url.rstrip('/')]
        pages_crawled = 0
        
        print(f"Starting crawl from: {self.base_url}")
        print(f"Politeness delay: {self.politeness_delay} seconds")
        print("-" * 60)
        
        while to_visit and pages_crawled < max_pages:
            url = to_visit.pop(0)
            
            # Skip if already visited
            if url in self.visited_urls:
                continue
            
            # Fetch the page
            html = self.fetch_page(url)
            
            if not html:
                self.visited_urls.add(url)
                continue
            
            # Extract text content
            text = self.extract_text(html)
            
            if text:
                self.pages[url] = text
                pages_crawled += 1
                print(f"✓ Crawled {pages_crawled}/{max_pages}: {url}")
            
            # Mark as visited
            self.visited_urls.add(url)
            
            # Extract and add new links
            links = self.extract_links(html, url)
            for link in links:
                if link not in self.visited_urls and link not in to_visit:
                    to_visit.append(link)
        
        print("-" * 60)
        print(f"Crawling complete! Total pages crawled: {len(self.pages)}")
        
        return self.pages
    
    def get_pages(self) -> Dict[str, str]:
        """
        Get the crawled pages.
        
        Returns:
            Dictionary mapping URLs to their text content
        """
        return self.pages
    
    def get_page_count(self) -> int:
        """
        Get the number of pages crawled.
        
        Returns:
            Number of pages in the collection
        """
        return len(self.pages)


if __name__ == "__main__":
    # Example usage
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=6.0)
    pages = crawler.crawl(max_pages=10)
    
    print(f"\nCrawled {len(pages)} pages:")
    for url in list(pages.keys())[:5]:
        print(f"  - {url}")
        print(f"    Text preview: {pages[url][:100]}...")
