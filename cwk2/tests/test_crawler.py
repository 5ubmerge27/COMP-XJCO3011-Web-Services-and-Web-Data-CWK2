"""
Unit tests for the WebCrawler module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.crawler import WebCrawler
import time


class TestWebCrawler:
    """Test cases for WebCrawler class"""
    
    def test_initialization(self):
        """Test crawler initialization"""
        crawler = WebCrawler("https://example.com", politeness_delay=3.0)
        
        assert crawler.base_url == "https://example.com"
        assert crawler.politeness_delay == 3.0
        assert len(crawler.visited_urls) == 0
        assert len(crawler.pages) == 0
    
    def test_default_politeness_delay(self):
        """Test default politeness delay is 6 seconds"""
        crawler = WebCrawler("https://example.com")
        assert crawler.politeness_delay == 6.0
    
    def test_is_valid_url_same_domain(self):
        """Test URL validation for same domain"""
        crawler = WebCrawler("https://quotes.toscrape.com/")
        
        # Valid URLs
        assert crawler._is_valid_url("https://quotes.toscrape.com/page/2")
        assert crawler._is_valid_url("https://quotes.toscrape.com/tag/love")
        
        # Invalid URLs (different domain)
        assert not crawler._is_valid_url("https://google.com")
        assert not crawler._is_valid_url("https://example.com/page")
    
    def test_is_valid_url_file_types(self):
        """Test URL validation excludes certain file types"""
        crawler = WebCrawler("https://example.com")
        
        assert not crawler._is_valid_url("https://example.com/image.jpg")
        assert not crawler._is_valid_url("https://example.com/doc.pdf")
        assert not crawler._is_valid_url("https://example.com/photo.png")
    
    def test_is_valid_url_fragments(self):
        """Test URL validation excludes fragments"""
        crawler = WebCrawler("https://example.com")
        
        assert not crawler._is_valid_url("https://example.com/page#section")
    
    def test_extract_text_basic(self):
        """Test basic text extraction from HTML"""
        crawler = WebCrawler("https://example.com")
        
        html = """
        <html>
            <body>
                <h1>Hello World</h1>
                <p>This is a test.</p>
            </body>
        </html>
        """
        
        text = crawler.extract_text(html)
        assert "Hello World" in text
        assert "This is a test" in text
    
    def test_extract_text_removes_scripts(self):
        """Test that script and style tags are removed"""
        crawler = WebCrawler("https://example.com")
        
        html = """
        <html>
            <head>
                <script>var x = 1;</script>
                <style>body { color: red; }</style>
            </head>
            <body>
                <p>Visible text</p>
            </body>
        </html>
        """
        
        text = crawler.extract_text(html)
        assert "Visible text" in text
        assert "var x = 1" not in text
        assert "color: red" not in text
    
    def test_extract_text_cleans_whitespace(self):
        """Test that excessive whitespace is cleaned"""
        crawler = WebCrawler("https://example.com")
        
        html = """
        <html>
            <body>
                <p>Word1    Word2
                
                Word3</p>
            </body>
        </html>
        """
        
        text = crawler.extract_text(html)
        # Should have single spaces between words
        assert "Word1 Word2 Word3" in text
    
    def test_extract_links_absolute_urls(self):
        """Test extraction of absolute URLs"""
        crawler = WebCrawler("https://quotes.toscrape.com/")
        
        html = """
        <html>
            <body>
                <a href="https://quotes.toscrape.com/page/2">Page 2</a>
                <a href="https://quotes.toscrape.com/tag/love">Love</a>
            </body>
        </html>
        """
        
        links = crawler.extract_links(html, "https://quotes.toscrape.com/")
        
        assert "https://quotes.toscrape.com/page/2" in links
        assert "https://quotes.toscrape.com/tag/love" in links
    
    def test_extract_links_relative_urls(self):
        """Test extraction and conversion of relative URLs"""
        crawler = WebCrawler("https://quotes.toscrape.com/")
        
        html = """
        <html>
            <body>
                <a href="/page/2">Page 2</a>
                <a href="tag/love">Love</a>
            </body>
        </html>
        """
        
        links = crawler.extract_links(html, "https://quotes.toscrape.com/")
        
        assert "https://quotes.toscrape.com/page/2" in links
        assert "https://quotes.toscrape.com/tag/love" in links
    
    def test_extract_links_filters_external(self):
        """Test that external links are filtered out"""
        crawler = WebCrawler("https://quotes.toscrape.com/")
        
        html = """
        <html>
            <body>
                <a href="https://quotes.toscrape.com/page/2">Internal</a>
                <a href="https://google.com">External</a>
            </body>
        </html>
        """
        
        links = crawler.extract_links(html, "https://quotes.toscrape.com/")
        
        assert "https://quotes.toscrape.com/page/2" in links
        assert "https://google.com" not in links
    
    @patch('src.crawler.requests.get')
    def test_fetch_page_success(self, mock_get):
        """Test successful page fetch"""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        crawler = WebCrawler("https://example.com", politeness_delay=0)
        html = crawler.fetch_page("https://example.com/page")
        
        assert html == "<html><body>Test</body></html>"
        mock_get.assert_called_once()
    
    @patch('src.crawler.requests.get')
    def test_fetch_page_failure(self, mock_get):
        """Test page fetch failure handling"""
        mock_get.side_effect = Exception("Network error")
        
        crawler = WebCrawler("https://example.com", politeness_delay=0)
        html = crawler.fetch_page("https://example.com/page")
        
        assert html == ""
    
    def test_politeness_delay(self):
        """Test that politeness delay is respected"""
        crawler = WebCrawler("https://example.com", politeness_delay=0.1)
        
        start_time = time.time()
        crawler._respect_politeness()
        crawler._respect_politeness()
        end_time = time.time()
        
        elapsed = end_time - start_time
        # Should have waited at least the politeness delay
        assert elapsed >= 0.1
    
    def test_get_pages(self):
        """Test getting crawled pages"""
        crawler = WebCrawler("https://example.com")
        crawler.pages = {"url1": "text1", "url2": "text2"}
        
        pages = crawler.get_pages()
        assert len(pages) == 2
        assert pages["url1"] == "text1"
    
    def test_get_page_count(self):
        """Test getting page count"""
        crawler = WebCrawler("https://example.com")
        crawler.pages = {"url1": "text1", "url2": "text2"}
        
        assert crawler.get_page_count() == 2
    
    @patch('src.crawler.requests.get')
    def test_crawl_respects_max_pages(self, mock_get):
        """Test that crawl respects max_pages limit"""
        # Mock response with links
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <p>Test content</p>
                <a href="/page2">Page 2</a>
                <a href="/page3">Page 3</a>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        crawler = WebCrawler("https://example.com", politeness_delay=0)
        pages = crawler.crawl(max_pages=2)
        
        # Should stop at max_pages
        assert len(pages) <= 2
    
    def test_extract_text_empty_html(self):
        """Test text extraction from empty HTML"""
        crawler = WebCrawler("https://example.com")
        text = crawler.extract_text("")
        assert text == ""
    
    def test_extract_links_no_links(self):
        """Test link extraction when no links present"""
        crawler = WebCrawler("https://example.com")
        html = "<html><body><p>No links here</p></body></html>"
        links = crawler.extract_links(html, "https://example.com")
        assert len(links) == 0
