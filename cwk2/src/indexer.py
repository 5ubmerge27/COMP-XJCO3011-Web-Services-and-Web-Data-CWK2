"""
Inverted Index Module

This module provides functionality to create and manage an inverted index
for efficient text search across multiple web pages.
"""

import json
import pickle
import re
from typing import Dict, List, Set, Optional
from collections import defaultdict


class InvertedIndex:
    """
    An inverted index that maps words to their occurrences in documents.
    
    The index structure is:
    {
        "word": {
            "url": {
                "frequency": int,
                "positions": [int, int, ...]
            }
        }
    }
    
    Attributes:
        index (Dict): The inverted index mapping words to document information
    """
    
    def __init__(self):
        """Initialize an empty inverted index."""
        self.index: Dict[str, Dict[str, Dict[str, any]]] = {}
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: The text to tokenize
            
        Returns:
            List of words (lowercase, alphanumeric only)
        """
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def _build_word_positions(self, words: List[str]) -> Dict[str, Dict[str, any]]:
        """
        Build word statistics from a list of words.
        
        Args:
            words: List of words from a document
            
        Returns:
            Dictionary mapping words to their frequency and positions
        """
        word_stats = defaultdict(lambda: {"frequency": 0, "positions": []})
        
        for position, word in enumerate(words):
            word_stats[word]["frequency"] += 1
            word_stats[word]["positions"].append(position)
        
        return dict(word_stats)
    
    def add_document(self, url: str, text: str):
        """
        Add a document to the inverted index.
        
        Args:
            url: The URL of the document
            text: The text content of the document
        """
        # Tokenize the text
        words = self._tokenize(text)
        
        # Build word statistics for this document
        word_stats = self._build_word_positions(words)
        
        # Add to inverted index
        for word, stats in word_stats.items():
            if word not in self.index:
                self.index[word] = {}
            
            self.index[word][url] = stats
    
    def build_from_pages(self, pages: Dict[str, str]):
        """
        Build the inverted index from a collection of pages.
        
        Args:
            pages: Dictionary mapping URLs to their text content
        """
        print(f"Building inverted index from {len(pages)} pages...")
        
        for url, text in pages.items():
            self.add_document(url, text)
        
        print(f"✓ Index built successfully!")
        print(f"  Total unique words: {len(self.index)}")
        print(f"  Total documents: {len(pages)}")
    
    def get_word_info(self, word: str) -> Optional[Dict[str, Dict[str, any]]]:
        """
        Get information about a word from the index.
        
        Args:
            word: The word to look up (case-insensitive)
            
        Returns:
            Dictionary mapping URLs to word statistics, or None if word not found
        """
        word = word.lower()
        return self.index.get(word)
    
    def get_pages_containing_word(self, word: str) -> List[str]:
        """
        Get all pages that contain a specific word.
        
        Args:
            word: The word to search for (case-insensitive)
            
        Returns:
            List of URLs containing the word
        """
        word_info = self.get_word_info(word)
        
        if word_info is None:
            return []
        
        return list(word_info.keys())
    
    def get_pages_containing_all_words(self, words: List[str]) -> List[str]:
        """
        Get all pages that contain all specified words.
        
        Args:
            words: List of words to search for
            
        Returns:
            List of URLs containing all the words
        """
        if not words:
            return []
        
        # Get pages for first word
        result_pages = set(self.get_pages_containing_word(words[0]))
        
        # Intersect with pages for remaining words
        for word in words[1:]:
            word_pages = set(self.get_pages_containing_word(word))
            result_pages = result_pages.intersection(word_pages)
        
        return list(result_pages)
    
    def get_word_frequency(self, word: str, url: str) -> int:
        """
        Get the frequency of a word in a specific document.
        
        Args:
            word: The word to look up
            url: The URL of the document
            
        Returns:
            Frequency of the word in the document, or 0 if not found
        """
        word_info = self.get_word_info(word)
        
        if word_info is None or url not in word_info:
            return 0
        
        return word_info[url]["frequency"]
    
    def get_total_words(self) -> int:
        """
        Get the total number of unique words in the index.
        
        Returns:
            Number of unique words
        """
        return len(self.index)
    
    def get_all_words(self) -> List[str]:
        """
        Get all words in the index.
        
        Returns:
            List of all unique words
        """
        return list(self.index.keys())
    
    def word_exists(self, word: str) -> bool:
        """
        Check if a word exists in the index.
        
        Args:
            word: The word to check
            
        Returns:
            True if word exists, False otherwise
        """
        return word.lower() in self.index
    
    def save_to_json(self, filepath: str):
        """
        Save the index to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
            print(f"✓ Index saved to {filepath}")
        except Exception as e:
            print(f"Error saving index to JSON: {e}")
            raise
    
    def load_from_json(self, filepath: str):
        """
        Load the index from a JSON file.
        
        Args:
            filepath: Path to the JSON file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
            print(f"✓ Index loaded from {filepath}")
            print(f"  Total unique words: {len(self.index)}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            raise
        except Exception as e:
            print(f"Error loading index from JSON: {e}")
            raise
    
    def save_to_pickle(self, filepath: str):
        """
        Save the index to a pickle file (more compact than JSON).
        
        Args:
            filepath: Path to save the pickle file
        """
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self.index, f)
            print(f"✓ Index saved to {filepath}")
        except Exception as e:
            print(f"Error saving index to pickle: {e}")
            raise
    
    def load_from_pickle(self, filepath: str):
        """
        Load the index from a pickle file.
        
        Args:
            filepath: Path to the pickle file
        """
        try:
            with open(filepath, 'rb') as f:
                self.index = pickle.load(f)
            print(f"✓ Index loaded from {filepath}")
            print(f"  Total unique words: {len(self.index)}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            raise
        except Exception as e:
            print(f"Error loading index from pickle: {e}")
            raise
    
    def print_word_info(self, word: str):
        """
        Print detailed information about a word in a formatted way.
        
        Args:
            word: The word to print information about
        """
        word_info = self.get_word_info(word)
        
        if word_info is None:
            print(f"Word '{word}' not found in index.")
            return
        
        print(f"\nInverted index for word: '{word}'")
        print("=" * 70)
        
        for url, stats in word_info.items():
            print(f"\n{url}")
            print(f"  Frequency: {stats['frequency']}")
            print(f"  Positions: {stats['positions'][:10]}", end="")
            if len(stats['positions']) > 10:
                print(f" ... (and {len(stats['positions']) - 10} more)")
            else:
                print()
        
        print("=" * 70)
        print(f"Total pages containing '{word}': {len(word_info)}")
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary containing index statistics
        """
        total_words = len(self.index)
        total_documents = len(set(
            url for word_info in self.index.values() 
            for url in word_info.keys()
        ))
        
        # Calculate average words per document
        word_counts = defaultdict(int)
        for word_info in self.index.values():
            for url, stats in word_info.items():
                word_counts[url] += stats['frequency']
        
        avg_words = sum(word_counts.values()) / len(word_counts) if word_counts else 0
        
        return {
            "total_unique_words": total_words,
            "total_documents": total_documents,
            "average_words_per_document": round(avg_words, 2)
        }


if __name__ == "__main__":
    # Example usage
    indexer = InvertedIndex()
    
    # Sample pages
    pages = {
        "https://example.com/page1": "Hello world! Hello Python programming.",
        "https://example.com/page2": "Python is great for web scraping.",
        "https://example.com/page3": "Hello there, welcome to the world of programming."
    }
    
    # Build index
    indexer.build_from_pages(pages)
    
    # Query examples
    print("\n" + "=" * 70)
    indexer.print_word_info("hello")
    
    print("\n" + "=" * 70)
    print("\nPages containing 'python':")
    for url in indexer.get_pages_containing_word("python"):
        print(f"  - {url}")
    
    print("\nPages containing both 'hello' and 'world':")
    for url in indexer.get_pages_containing_all_words(["hello", "world"]):
        print(f"  - {url}")
    
    # Statistics
    print("\n" + "=" * 70)
    stats = indexer.get_statistics()
    print("\nIndex Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
