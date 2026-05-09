"""
Search Engine Module

This module provides search functionality using the inverted index
to find and rank pages based on search queries.
"""

from typing import List, Dict, Tuple, Optional
from src.indexer import InvertedIndex
import re


class SearchEngine:
    """
    A search engine that uses an inverted index to find relevant pages.
    
    Attributes:
        indexer (InvertedIndex): The inverted index to search
    """
    
    def __init__(self, indexer: Optional[InvertedIndex] = None):
        """
        Initialize the search engine.
        
        Args:
            indexer: An InvertedIndex instance (optional)
        """
        self.indexer = indexer if indexer is not None else InvertedIndex()
    
    def set_indexer(self, indexer: InvertedIndex):
        """
        Set or replace the indexer.
        
        Args:
            indexer: The InvertedIndex to use
        """
        self.indexer = indexer
    
    def _parse_query(self, query: str) -> List[str]:
        """
        Parse a search query into individual terms.
        
        Args:
            query: The search query string
            
        Returns:
            List of search terms (lowercase, cleaned)
        """
        # Extract words (alphanumeric sequences)
        terms = re.findall(r'\b\w+\b', query.lower())
        return terms
    
    def search(self, query: str) -> List[str]:
        """
        Search for pages matching the query.
        
        For single-word queries, returns all pages containing the word.
        For multi-word queries, returns pages containing ALL words.
        
        Args:
            query: The search query string
            
        Returns:
            List of URLs matching the query
        """
        if not query or not query.strip():
            return []
        
        # Parse query into terms
        terms = self._parse_query(query)
        
        if not terms:
            return []
        
        # Single term search
        if len(terms) == 1:
            return self.indexer.get_pages_containing_word(terms[0])
        
        # Multi-term search (AND operation)
        return self.indexer.get_pages_containing_all_words(terms)
    
    def search_with_ranking(self, query: str) -> List[Tuple[str, float]]:
        """
        Search for pages and rank them by relevance.
        
        Ranking is based on term frequency (TF) - pages with higher
        frequency of query terms are ranked higher.
        
        Args:
            query: The search query string
            
        Returns:
            List of (URL, score) tuples, sorted by score (descending)
        """
        # Get matching pages
        pages = self.search(query)
        
        if not pages:
            return []
        
        # Parse query terms
        terms = self._parse_query(query)
        
        # Calculate scores for each page
        page_scores = []
        for url in pages:
            score = self._calculate_score(url, terms)
            page_scores.append((url, score))
        
        # Sort by score (descending)
        page_scores.sort(key=lambda x: x[1], reverse=True)
        
        return page_scores
    
    def _calculate_score(self, url: str, terms: List[str]) -> float:
        """
        Calculate relevance score for a page.
        
        Score is the sum of term frequencies for all query terms.
        
        Args:
            url: The URL to score
            terms: List of search terms
            
        Returns:
            Relevance score
        """
        score = 0.0
        
        for term in terms:
            frequency = self.indexer.get_word_frequency(term, url)
            score += frequency
        
        return score
    
    def search_single_word(self, word: str) -> List[str]:
        """
        Search for pages containing a single word.
        
        Args:
            word: The word to search for
            
        Returns:
            List of URLs containing the word
        """
        if not word or not word.strip():
            return []
        
        # Clean the word
        word = word.strip().lower()
        
        return self.indexer.get_pages_containing_word(word)
    
    def search_phrase(self, phrase: str) -> List[str]:
        """
        Search for pages containing all words in a phrase.
        
        This is equivalent to an AND search - all words must be present.
        
        Args:
            phrase: The phrase to search for
            
        Returns:
            List of URLs containing all words in the phrase
        """
        return self.search(phrase)
    
    def get_search_results_with_context(self, query: str, context_words: int = 10) -> Dict[str, Dict]:
        """
        Get search results with context snippets.
        
        Args:
            query: The search query
            context_words: Number of words to show around each match
            
        Returns:
            Dictionary mapping URLs to result information
        """
        results = {}
        pages = self.search(query)
        terms = self._parse_query(query)
        
        for url in pages:
            # Get word info for each term
            snippets = []
            total_frequency = 0
            
            for term in terms:
                word_info = self.indexer.get_word_info(term)
                if word_info and url in word_info:
                    freq = word_info[url]['frequency']
                    positions = word_info[url]['positions']
                    total_frequency += freq
                    
                    # Add first position as snippet reference
                    if positions:
                        snippets.append({
                            'term': term,
                            'position': positions[0],
                            'frequency': freq
                        })
            
            results[url] = {
                'total_frequency': total_frequency,
                'snippets': snippets,
                'term_count': len(terms)
            }
        
        return results
    
    def print_search_results(self, query: str, max_results: int = 10):
        """
        Print search results in a formatted way.
        
        Args:
            query: The search query
            max_results: Maximum number of results to display
        """
        print(f"\nSearch query: '{query}'")
        print("=" * 70)
        
        # Get ranked results
        results = self.search_with_ranking(query)
        
        if not results:
            print("No results found.")
            return
        
        print(f"Found {len(results)} result(s):\n")
        
        # Display results
        for i, (url, score) in enumerate(results[:max_results], 1):
            print(f"{i}. {url}")
            print(f"   Relevance score: {score:.2f}")
            
            # Show term frequencies
            terms = self._parse_query(query)
            term_freqs = []
            for term in terms:
                freq = self.indexer.get_word_frequency(term, url)
                if freq > 0:
                    term_freqs.append(f"'{term}': {freq}")
            
            if term_freqs:
                print(f"   Term frequencies: {', '.join(term_freqs)}")
            print()
        
        if len(results) > max_results:
            print(f"... and {len(results) - max_results} more result(s)")
        
        print("=" * 70)
    
    def get_word_info(self, word: str) -> Optional[Dict]:
        """
        Get detailed information about a word.
        
        Args:
            word: The word to look up
            
        Returns:
            Dictionary with word information, or None if not found
        """
        return self.indexer.get_word_info(word)
    
    def print_word_info(self, word: str):
        """
        Print detailed information about a word.
        
        Args:
            word: The word to print information about
        """
        self.indexer.print_word_info(word)
    
    def get_statistics(self) -> Dict:
        """
        Get search engine statistics.
        
        Returns:
            Dictionary with statistics
        """
        index_stats = self.indexer.get_statistics()
        
        return {
            'index_statistics': index_stats,
            'total_searchable_words': self.indexer.get_total_words()
        }


class QueryValidator:
    """
    Utility class for validating and processing search queries.
    """
    
    @staticmethod
    def is_valid_query(query: str) -> bool:
        """
        Check if a query is valid.
        
        Args:
            query: The query to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not query or not query.strip():
            return False
        
        # Check if query contains at least one alphanumeric character
        if not re.search(r'\w', query):
            return False
        
        return True
    
    @staticmethod
    def clean_query(query: str) -> str:
        """
        Clean and normalize a query.
        
        Args:
            query: The query to clean
            
        Returns:
            Cleaned query string
        """
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Convert to lowercase
        query = query.lower()
        
        return query
    
    @staticmethod
    def get_query_terms(query: str) -> List[str]:
        """
        Extract terms from a query.
        
        Args:
            query: The query string
            
        Returns:
            List of query terms
        """
        return re.findall(r'\b\w+\b', query.lower())


if __name__ == "__main__":
    # Example usage
    from src.indexer import InvertedIndex
    
    # Create sample index
    indexer = InvertedIndex()
    pages = {
        "https://example.com/page1": "Hello world! Python programming is great.",
        "https://example.com/page2": "Python is a powerful programming language.",
        "https://example.com/page3": "Hello there! Welcome to the world of coding.",
        "https://example.com/page4": "Web scraping with Python and BeautifulSoup."
    }
    indexer.build_from_pages(pages)
    
    # Create search engine
    search_engine = SearchEngine(indexer)
    
    # Example searches
    print("=" * 70)
    search_engine.print_search_results("python")
    
    print("\n" + "=" * 70)
    search_engine.print_search_results("python programming")
    
    print("\n" + "=" * 70)
    search_engine.print_search_results("hello world")
    
    # Word info
    print("\n" + "=" * 70)
    search_engine.print_word_info("python")
    
    # Statistics
    print("\n" + "=" * 70)
    stats = search_engine.get_statistics()
    print("\nSearch Engine Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
