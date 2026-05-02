"""
Unit tests for the InvertedIndex module
"""

import pytest
import os
import json
import tempfile
from src.indexer import InvertedIndex


class TestInvertedIndex:
    """Test cases for InvertedIndex class"""
    
    def test_initialization(self):
        """Test indexer initialization"""
        indexer = InvertedIndex()
        assert len(indexer.index) == 0
        assert indexer.get_total_words() == 0
    
    def test_tokenize_basic(self):
        """Test basic tokenization"""
        indexer = InvertedIndex()
        
        text = "Hello World Python"
        words = indexer._tokenize(text)
        
        assert words == ["hello", "world", "python"]
    
    def test_tokenize_with_punctuation(self):
        """Test tokenization removes punctuation"""
        indexer = InvertedIndex()
        
        text = "Hello, World! How are you?"
        words = indexer._tokenize(text)
        
        assert "hello" in words
        assert "world" in words
        assert "," not in words
        assert "!" not in words
    
    def test_tokenize_case_insensitive(self):
        """Test tokenization is case-insensitive"""
        indexer = InvertedIndex()
        
        text = "Hello HELLO hello"
        words = indexer._tokenize(text)
        
        assert all(word == "hello" for word in words)
    
    def test_build_word_positions(self):
        """Test building word positions and frequencies"""
        indexer = InvertedIndex()
        
        words = ["hello", "world", "hello", "python"]
        stats = indexer._build_word_positions(words)
        
        assert stats["hello"]["frequency"] == 2
        assert stats["hello"]["positions"] == [0, 2]
        assert stats["world"]["frequency"] == 1
        assert stats["world"]["positions"] == [1]
    
    def test_add_document_basic(self):
        """Test adding a single document"""
        indexer = InvertedIndex()
        
        indexer.add_document("url1", "Hello world")
        
        assert "hello" in indexer.index
        assert "world" in indexer.index
        assert "url1" in indexer.index["hello"]
    
    def test_add_document_with_frequency(self):
        """Test word frequency is tracked correctly"""
        indexer = InvertedIndex()
        
        indexer.add_document("url1", "hello world hello")
        
        assert indexer.index["hello"]["url1"]["frequency"] == 2
        assert indexer.index["world"]["url1"]["frequency"] == 1
    
    def test_add_document_with_positions(self):
        """Test word positions are tracked correctly"""
        indexer = InvertedIndex()
        
        indexer.add_document("url1", "hello world hello")
        
        assert indexer.index["hello"]["url1"]["positions"] == [0, 2]
        assert indexer.index["world"]["url1"]["positions"] == [1]
    
    def test_add_multiple_documents(self):
        """Test adding multiple documents"""
        indexer = InvertedIndex()
        
        indexer.add_document("url1", "hello world")
        indexer.add_document("url2", "hello python")
        
        assert "url1" in indexer.index["hello"]
        assert "url2" in indexer.index["hello"]
        assert "world" in indexer.index
        assert "python" in indexer.index
    
    def test_build_from_pages(self):
        """Test building index from multiple pages"""
        indexer = InvertedIndex()
        
        pages = {
            "url1": "hello world",
            "url2": "python programming",
            "url3": "hello python"
        }
        
        indexer.build_from_pages(pages)
        
        assert indexer.get_total_words() == 4  # hello, world, python, programming
        assert len(indexer.get_pages_containing_word("hello")) == 2
    
    def test_get_word_info_exists(self):
        """Test getting word info for existing word"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world")
        
        info = indexer.get_word_info("hello")
        
        assert info is not None
        assert "url1" in info
        assert info["url1"]["frequency"] == 1
    
    def test_get_word_info_not_exists(self):
        """Test getting word info for non-existing word"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world")
        
        info = indexer.get_word_info("python")
        
        assert info is None
    
    def test_get_word_info_case_insensitive(self):
        """Test word lookup is case-insensitive"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "Hello World")
        
        info1 = indexer.get_word_info("hello")
        info2 = indexer.get_word_info("HELLO")
        info3 = indexer.get_word_info("HeLLo")
        
        assert info1 is not None
        assert info1 == info2 == info3
    
    def test_get_pages_containing_word(self):
        """Test getting pages containing a word"""
        indexer = InvertedIndex()
        
        pages = {
            "url1": "hello world",
            "url2": "python programming",
            "url3": "hello python"
        }
        indexer.build_from_pages(pages)
        
        pages_with_hello = indexer.get_pages_containing_word("hello")
        
        assert len(pages_with_hello) == 2
        assert "url1" in pages_with_hello
        assert "url3" in pages_with_hello
    
    def test_get_pages_containing_word_not_found(self):
        """Test getting pages for non-existing word"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world")
        
        pages = indexer.get_pages_containing_word("python")
        
        assert pages == []
    
    def test_get_pages_containing_all_words_single(self):
        """Test getting pages containing a single word"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world python")
        
        pages = indexer.get_pages_containing_all_words(["hello"])
        
        assert "url1" in pages
    
    def test_get_pages_containing_all_words_multiple(self):
        """Test getting pages containing multiple words"""
        indexer = InvertedIndex()
        
        pages_data = {
            "url1": "hello world python",
            "url2": "hello world",
            "url3": "python programming"
        }
        indexer.build_from_pages(pages_data)
        
        pages = indexer.get_pages_containing_all_words(["hello", "world"])
        
        assert len(pages) == 2
        assert "url1" in pages
        assert "url2" in pages
        assert "url3" not in pages
    
    def test_get_pages_containing_all_words_no_match(self):
        """Test getting pages when no page contains all words"""
        indexer = InvertedIndex()
        
        pages_data = {
            "url1": "hello world",
            "url2": "python programming"
        }
        indexer.build_from_pages(pages_data)
        
        pages = indexer.get_pages_containing_all_words(["hello", "python"])
        
        assert pages == []
    
    def test_get_pages_containing_all_words_empty_list(self):
        """Test getting pages with empty word list"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world")
        
        pages = indexer.get_pages_containing_all_words([])
        
        assert pages == []
    
    def test_get_word_frequency(self):
        """Test getting word frequency in a document"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world hello hello")
        
        freq = indexer.get_word_frequency("hello", "url1")
        
        assert freq == 3
    
    def test_get_word_frequency_not_in_doc(self):
        """Test getting frequency for word not in document"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world")
        
        freq = indexer.get_word_frequency("python", "url1")
        
        assert freq == 0
    
    def test_get_word_frequency_word_not_exists(self):
        """Test getting frequency for non-existing word"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world")
        
        freq = indexer.get_word_frequency("nonexistent", "url1")
        
        assert freq == 0
    
    def test_get_total_words(self):
        """Test getting total unique words"""
        indexer = InvertedIndex()
        
        pages = {
            "url1": "hello world",
            "url2": "hello python programming"
        }
        indexer.build_from_pages(pages)
        
        assert indexer.get_total_words() == 4  # hello, world, python, programming
    
    def test_get_all_words(self):
        """Test getting all words"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world python")
        
        words = indexer.get_all_words()
        
        assert len(words) == 3
        assert "hello" in words
        assert "world" in words
        assert "python" in words
    
    def test_word_exists(self):
        """Test checking if word exists"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world")
        
        assert indexer.word_exists("hello") is True
        assert indexer.word_exists("HELLO") is True
        assert indexer.word_exists("python") is False
    
    def test_save_and_load_json(self):
        """Test saving and loading index as JSON"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            # Save
            indexer.save_to_json(temp_path)
            
            # Load into new indexer
            new_indexer = InvertedIndex()
            new_indexer.load_from_json(temp_path)
            
            # Verify
            assert new_indexer.get_total_words() == indexer.get_total_words()
            assert new_indexer.word_exists("hello")
            assert new_indexer.word_exists("world")
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_save_and_load_pickle(self):
        """Test saving and loading index as pickle"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world python")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            temp_path = f.name
        
        try:
            # Save
            indexer.save_to_pickle(temp_path)
            
            # Load into new indexer
            new_indexer = InvertedIndex()
            new_indexer.load_from_pickle(temp_path)
            
            # Verify
            assert new_indexer.get_total_words() == indexer.get_total_words()
            assert new_indexer.word_exists("hello")
            assert new_indexer.get_word_frequency("hello", "url1") == 1
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_load_json_file_not_found(self):
        """Test loading from non-existent JSON file"""
        indexer = InvertedIndex()
        
        with pytest.raises(FileNotFoundError):
            indexer.load_from_json("nonexistent.json")
    
    def test_load_pickle_file_not_found(self):
        """Test loading from non-existent pickle file"""
        indexer = InvertedIndex()
        
        with pytest.raises(FileNotFoundError):
            indexer.load_from_pickle("nonexistent.pkl")
    
    def test_get_statistics(self):
        """Test getting index statistics"""
        indexer = InvertedIndex()
        
        pages = {
            "url1": "hello world",
            "url2": "python programming hello"
        }
        indexer.build_from_pages(pages)
        
        stats = indexer.get_statistics()
        
        assert stats["total_unique_words"] == 4
        assert stats["total_documents"] == 2
        assert "average_words_per_document" in stats
    
    def test_empty_document(self):
        """Test adding empty document"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "")
        
        assert indexer.get_total_words() == 0
    
    def test_document_with_numbers(self):
        """Test document containing numbers"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "Python 3 is great")
        
        assert indexer.word_exists("python")
        assert indexer.word_exists("3")
        assert indexer.word_exists("is")
        assert indexer.word_exists("great")
    
    def test_special_characters_only(self):
        """Test document with only special characters"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "!@#$%^&*()")
        
        assert indexer.get_total_words() == 0
