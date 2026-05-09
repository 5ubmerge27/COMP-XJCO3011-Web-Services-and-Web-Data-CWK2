"""
Unit tests for the SearchEngine module
"""

import pytest
from src.search import SearchEngine, QueryValidator
from src.indexer import InvertedIndex


class TestSearchEngine:
    """Test cases for SearchEngine class"""
    
    @pytest.fixture
    def sample_indexer(self):
        """Create a sample indexer for testing"""
        indexer = InvertedIndex()
        pages = {
            "url1": "hello world python programming",
            "url2": "python is great for programming",
            "url3": "hello there welcome to the world",
            "url4": "web scraping with python"
        }
        indexer.build_from_pages(pages)
        return indexer
    
    @pytest.fixture
    def search_engine(self, sample_indexer):
        """Create a search engine with sample data"""
        return SearchEngine(sample_indexer)
    
    def test_initialization_empty(self):
        """Test search engine initialization without indexer"""
        engine = SearchEngine()
        assert engine.indexer is not None
        assert engine.indexer.get_total_words() == 0
    
    def test_initialization_with_indexer(self, sample_indexer):
        """Test search engine initialization with indexer"""
        engine = SearchEngine(sample_indexer)
        assert engine.indexer == sample_indexer
        assert engine.indexer.get_total_words() > 0
    
    def test_set_indexer(self, sample_indexer):
        """Test setting a new indexer"""
        engine = SearchEngine()
        engine.set_indexer(sample_indexer)
        assert engine.indexer == sample_indexer
    
    def test_parse_query_single_word(self, search_engine):
        """Test parsing single word query"""
        terms = search_engine._parse_query("python")
        assert terms == ["python"]
    
    def test_parse_query_multiple_words(self, search_engine):
        """Test parsing multiple word query"""
        terms = search_engine._parse_query("hello world")
        assert terms == ["hello", "world"]
    
    def test_parse_query_with_punctuation(self, search_engine):
        """Test parsing query with punctuation"""
        terms = search_engine._parse_query("hello, world!")
        assert terms == ["hello", "world"]
    
    def test_parse_query_case_insensitive(self, search_engine):
        """Test query parsing is case insensitive"""
        terms = search_engine._parse_query("HELLO World")
        assert terms == ["hello", "world"]
    
    def test_search_single_word(self, search_engine):
        """Test searching for a single word"""
        results = search_engine.search("python")
        
        assert len(results) == 3
        assert "url1" in results
        assert "url2" in results
        assert "url4" in results
    
    def test_search_multiple_words(self, search_engine):
        """Test searching for multiple words (AND operation)"""
        results = search_engine.search("hello world")
        
        assert len(results) == 2
        assert "url1" in results
        assert "url3" in results
    
    def test_search_no_results(self, search_engine):
        """Test search with no matching results"""
        results = search_engine.search("nonexistent")
        assert results == []
    
    def test_search_empty_query(self, search_engine):
        """Test search with empty query"""
        results = search_engine.search("")
        assert results == []
    
    def test_search_whitespace_only(self, search_engine):
        """Test search with whitespace only"""
        results = search_engine.search("   ")
        assert results == []
    
    def test_search_case_insensitive(self, search_engine):
        """Test search is case insensitive"""
        results1 = search_engine.search("python")
        results2 = search_engine.search("PYTHON")
        results3 = search_engine.search("Python")
        
        assert results1 == results2 == results3
    
    def test_search_with_ranking_single_word(self, search_engine):
        """Test ranked search for single word"""
        results = search_engine.search_with_ranking("python")
        
        assert len(results) == 3
        # Results should be tuples of (url, score)
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
        # Scores should be in descending order
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)
    
    def test_search_with_ranking_multiple_words(self, search_engine):
        """Test ranked search for multiple words"""
        results = search_engine.search_with_ranking("python programming")
        
        assert len(results) == 2
        # url1 and url2 both have both words
        urls = [url for url, _ in results]
        assert "url1" in urls
        assert "url2" in urls
    
    def test_search_with_ranking_no_results(self, search_engine):
        """Test ranked search with no results"""
        results = search_engine.search_with_ranking("nonexistent")
        assert results == []
    
    def test_calculate_score(self, search_engine):
        """Test score calculation"""
        # url1 has "python" once and "programming" once
        score = search_engine._calculate_score("url1", ["python", "programming"])
        assert score == 2.0
        
        # url2 has "python" once and "programming" once
        score = search_engine._calculate_score("url2", ["python", "programming"])
        assert score == 2.0
    
    def test_calculate_score_single_term(self, search_engine):
        """Test score calculation for single term"""
        score = search_engine._calculate_score("url1", ["python"])
        assert score == 1.0
    
    def test_search_single_word_method(self, search_engine):
        """Test search_single_word method"""
        results = search_engine.search_single_word("python")
        
        assert len(results) == 3
        assert "url1" in results
    
    def test_search_single_word_empty(self, search_engine):
        """Test search_single_word with empty string"""
        results = search_engine.search_single_word("")
        assert results == []
    
    def test_search_single_word_whitespace(self, search_engine):
        """Test search_single_word with whitespace"""
        results = search_engine.search_single_word("  python  ")
        assert len(results) == 3
    
    def test_search_phrase(self, search_engine):
        """Test search_phrase method"""
        results = search_engine.search_phrase("hello world")
        
        assert len(results) == 2
        assert "url1" in results
        assert "url3" in results
    
    def test_get_search_results_with_context(self, search_engine):
        """Test getting search results with context"""
        results = search_engine.get_search_results_with_context("python")
        
        assert "url1" in results
        assert "total_frequency" in results["url1"]
        assert "snippets" in results["url1"]
        assert results["url1"]["total_frequency"] == 1
    
    def test_get_search_results_with_context_multiple_terms(self, search_engine):
        """Test context results for multiple terms"""
        results = search_engine.get_search_results_with_context("python programming")
        
        assert "url1" in results
        assert results["url1"]["total_frequency"] == 2
        assert results["url1"]["term_count"] == 2
    
    def test_get_word_info(self, search_engine):
        """Test getting word info through search engine"""
        info = search_engine.get_word_info("python")
        
        assert info is not None
        assert "url1" in info
        assert "url2" in info
    
    def test_get_word_info_not_found(self, search_engine):
        """Test getting info for non-existent word"""
        info = search_engine.get_word_info("nonexistent")
        assert info is None
    
    def test_get_statistics(self, search_engine):
        """Test getting search engine statistics"""
        stats = search_engine.get_statistics()
        
        assert "index_statistics" in stats
        assert "total_searchable_words" in stats
        assert stats["total_searchable_words"] > 0
    
    def test_search_special_characters(self, search_engine):
        """Test search with special characters"""
        results = search_engine.search("python!!!")
        # Should still find python
        assert len(results) == 3
    
    def test_search_with_numbers(self):
        """Test search with numbers in query"""
        indexer = InvertedIndex()
        indexer.add_document("url1", "Python 3 is great")
        engine = SearchEngine(indexer)
        
        results = engine.search("python 3")
        assert len(results) == 1
    
    def test_ranking_order(self):
        """Test that ranking orders results correctly"""
        indexer = InvertedIndex()
        pages = {
            "url1": "python",  # 1 occurrence
            "url2": "python python",  # 2 occurrences
            "url3": "python python python"  # 3 occurrences
        }
        indexer.build_from_pages(pages)
        engine = SearchEngine(indexer)
        
        results = engine.search_with_ranking("python")
        
        # url3 should be first (highest score)
        assert results[0][0] == "url3"
        assert results[1][0] == "url2"
        assert results[2][0] == "url1"
    
    def test_multi_word_search_partial_match(self, search_engine):
        """Test multi-word search doesn't return partial matches"""
        results = search_engine.search("python nonexistent")
        # Should return empty because not all words are present
        assert results == []


class TestQueryValidator:
    """Test cases for QueryValidator class"""
    
    def test_is_valid_query_valid(self):
        """Test validation of valid queries"""
        assert QueryValidator.is_valid_query("python") is True
        assert QueryValidator.is_valid_query("hello world") is True
        assert QueryValidator.is_valid_query("Python 3") is True
    
    def test_is_valid_query_empty(self):
        """Test validation of empty query"""
        assert QueryValidator.is_valid_query("") is False
        assert QueryValidator.is_valid_query("   ") is False
    
    def test_is_valid_query_special_chars_only(self):
        """Test validation of query with only special characters"""
        assert QueryValidator.is_valid_query("!!!") is False
        assert QueryValidator.is_valid_query("@#$") is False
    
    def test_is_valid_query_with_special_chars(self):
        """Test validation of query with words and special chars"""
        assert QueryValidator.is_valid_query("hello!") is True
        assert QueryValidator.is_valid_query("python?") is True
    
    def test_clean_query_whitespace(self):
        """Test cleaning query whitespace"""
        cleaned = QueryValidator.clean_query("  hello   world  ")
        assert cleaned == "hello world"
    
    def test_clean_query_case(self):
        """Test cleaning query converts to lowercase"""
        cleaned = QueryValidator.clean_query("HELLO World")
        assert cleaned == "hello world"
    
    def test_clean_query_combined(self):
        """Test cleaning query with multiple issues"""
        cleaned = QueryValidator.clean_query("  HELLO   WORLD  ")
        assert cleaned == "hello world"
    
    def test_get_query_terms_single(self):
        """Test extracting single term"""
        terms = QueryValidator.get_query_terms("python")
        assert terms == ["python"]
    
    def test_get_query_terms_multiple(self):
        """Test extracting multiple terms"""
        terms = QueryValidator.get_query_terms("hello world python")
        assert terms == ["hello", "world", "python"]
    
    def test_get_query_terms_with_punctuation(self):
        """Test extracting terms with punctuation"""
        terms = QueryValidator.get_query_terms("hello, world!")
        assert terms == ["hello", "world"]
    
    def test_get_query_terms_case_insensitive(self):
        """Test term extraction is case insensitive"""
        terms = QueryValidator.get_query_terms("HELLO World")
        assert terms == ["hello", "world"]
    
    def test_get_query_terms_empty(self):
        """Test extracting terms from empty query"""
        terms = QueryValidator.get_query_terms("")
        assert terms == []
