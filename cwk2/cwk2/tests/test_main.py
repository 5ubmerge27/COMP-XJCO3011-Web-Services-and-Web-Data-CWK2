"""
Integration tests for the main CLI module
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.main import SearchEngineCLI
from src.indexer import InvertedIndex


class TestSearchEngineCLI:
    """Test cases for SearchEngineCLI class"""
    
    @pytest.fixture
    def cli(self):
        """Create a CLI instance for testing"""
        return SearchEngineCLI()
    
    @pytest.fixture
    def cli_with_index(self, tmp_path):
        """Create a CLI instance with a loaded index"""
        cli = SearchEngineCLI()
        cli.INDEX_FILE = str(tmp_path / "test_index.json")
        
        # Create a simple index
        indexer = InvertedIndex()
        pages = {
            "url1": "hello world python",
            "url2": "python programming"
        }
        indexer.build_from_pages(pages)
        indexer.save_to_json(cli.INDEX_FILE)
        
        # Load it
        cli.indexer = indexer
        from src.search import SearchEngine
        cli.search_engine = SearchEngine(indexer)
        cli.index_loaded = True
        
        return cli
    
    def test_initialization(self, cli):
        """Test CLI initialization"""
        assert cli.indexer is None
        assert cli.search_engine is None
        assert cli.index_loaded is False
    
    def test_parse_command_single_word(self, cli):
        """Test parsing single word command"""
        command, args = cli.parse_command("build")
        
        assert command == "build"
        assert args == []
    
    def test_parse_command_with_args(self, cli):
        """Test parsing command with arguments"""
        command, args = cli.parse_command("print hello")
        
        assert command == "print"
        assert args == ["hello"]
    
    def test_parse_command_multiple_args(self, cli):
        """Test parsing command with multiple arguments"""
        command, args = cli.parse_command("find hello world")
        
        assert command == "find"
        assert args == ["hello", "world"]
    
    def test_parse_command_empty(self, cli):
        """Test parsing empty command"""
        command, args = cli.parse_command("")
        
        assert command is None
        assert args == []
    
    def test_parse_command_whitespace(self, cli):
        """Test parsing whitespace only"""
        command, args = cli.parse_command("   ")
        
        assert command is None
        assert args == []
    
    def test_parse_command_case_insensitive(self, cli):
        """Test command parsing is case insensitive"""
        command1, _ = cli.parse_command("BUILD")
        command2, _ = cli.parse_command("build")
        command3, _ = cli.parse_command("BuIlD")
        
        assert command1 == command2 == command3 == "build"
    
    def test_cmd_print_no_index(self, cli, capsys):
        """Test print command without loaded index"""
        cli.cmd_print(["hello"])
        
        captured = capsys.readouterr()
        assert "No index loaded" in captured.out
    
    def test_cmd_print_no_args(self, cli_with_index, capsys):
        """Test print command without arguments"""
        cli_with_index.cmd_print([])
        
        captured = capsys.readouterr()
        assert "Please specify a word" in captured.out
    
    def test_cmd_print_with_word(self, cli_with_index, capsys):
        """Test print command with valid word"""
        cli_with_index.cmd_print(["python"])
        
        captured = capsys.readouterr()
        assert "python" in captured.out.lower()
    
    def test_cmd_find_no_index(self, cli, capsys):
        """Test find command without loaded index"""
        cli.cmd_find(["hello"])
        
        captured = capsys.readouterr()
        assert "No index loaded" in captured.out
    
    def test_cmd_find_no_args(self, cli_with_index, capsys):
        """Test find command without arguments"""
        cli_with_index.cmd_find([])
        
        captured = capsys.readouterr()
        assert "Please specify search terms" in captured.out
    
    def test_cmd_find_with_query(self, cli_with_index, capsys):
        """Test find command with valid query"""
        cli_with_index.cmd_find(["python"])
        
        captured = capsys.readouterr()
        assert "Search query" in captured.out
    
    def test_cmd_stats_no_index(self, cli, capsys):
        """Test stats command without loaded index"""
        cli.cmd_stats([])
        
        captured = capsys.readouterr()
        assert "No index loaded" in captured.out
    
    def test_cmd_stats_with_index(self, cli_with_index, capsys):
        """Test stats command with loaded index"""
        cli_with_index.cmd_stats([])
        
        captured = capsys.readouterr()
        assert "INDEX STATISTICS" in captured.out
        assert "Total unique words" in captured.out
    
    def test_cmd_load_file_not_found(self, cli, capsys, tmp_path):
        """Test load command when file doesn't exist"""
        cli.INDEX_FILE = str(tmp_path / "nonexistent.json")
        cli.cmd_load([])
        
        captured = capsys.readouterr()
        assert "not found" in captured.out
    
    def test_cmd_load_success(self, cli, capsys, tmp_path):
        """Test successful load command"""
        # Create index file
        index_file = tmp_path / "test_index.json"
        indexer = InvertedIndex()
        indexer.add_document("url1", "hello world")
        indexer.save_to_json(str(index_file))
        
        cli.INDEX_FILE = str(index_file)
        cli.cmd_load([])
        
        assert cli.index_loaded is True
        assert cli.indexer is not None
        
        captured = capsys.readouterr()
        assert "LOAD COMPLETE" in captured.out
    
    def test_cmd_help(self, cli, capsys):
        """Test help command"""
        cli.cmd_help([])
        
        captured = capsys.readouterr()
        assert "Available commands" in captured.out
        assert "build" in captured.out
        assert "load" in captured.out
    
    def test_cmd_exit(self, cli):
        """Test exit command"""
        with pytest.raises(SystemExit):
            cli.cmd_exit([])
    
    def test_execute_command_valid(self, cli_with_index, capsys):
        """Test executing valid command"""
        cli_with_index.execute_command("stats", [])
        
        captured = capsys.readouterr()
        assert "INDEX STATISTICS" in captured.out
    
    def test_execute_command_invalid(self, cli, capsys):
        """Test executing invalid command"""
        cli.execute_command("invalid", [])
        
        captured = capsys.readouterr()
        assert "Unknown command" in captured.out
    
    def test_execute_command_quit(self, cli):
        """Test quit command (alias for exit)"""
        with pytest.raises(SystemExit):
            cli.execute_command("quit", [])
    
    @patch('src.main.WebCrawler')
    def test_cmd_build_no_pages(self, mock_crawler_class, cli, capsys):
        """Test build command when no pages are crawled"""
        # Mock crawler to return empty pages
        mock_crawler = Mock()
        mock_crawler.crawl.return_value = {}
        mock_crawler_class.return_value = mock_crawler
        
        cli.cmd_build([])
        
        captured = capsys.readouterr()
        assert "No pages were crawled" in captured.out
    
    @patch('src.main.WebCrawler')
    def test_cmd_build_success(self, mock_crawler_class, cli, capsys, tmp_path):
        """Test successful build command"""
        # Mock crawler to return sample pages
        mock_crawler = Mock()
        mock_crawler.crawl.return_value = {
            "url1": "hello world",
            "url2": "python programming"
        }
        mock_crawler_class.return_value = mock_crawler
        
        cli.INDEX_FILE = str(tmp_path / "test_index.json")
        cli.cmd_build([])
        
        assert cli.index_loaded is True
        assert cli.indexer is not None
        assert os.path.exists(cli.INDEX_FILE)
        
        captured = capsys.readouterr()
        assert "BUILD COMPLETE" in captured.out
    
    def test_data_directory_creation(self):
        """Test that data directory is created on initialization"""
        # This test verifies the directory exists after init
        cli = SearchEngineCLI()
        assert os.path.exists("data")
    
    def test_print_welcome(self, cli, capsys):
        """Test welcome message printing"""
        cli.print_welcome()
        
        captured = capsys.readouterr()
        assert "SEARCH ENGINE TOOL" in captured.out
        assert "Available commands" in captured.out


class TestCLIIntegration:
    """Integration tests for the complete CLI workflow"""
    
    @patch('src.main.WebCrawler')
    def test_full_workflow_build_and_search(self, mock_crawler_class, tmp_path, capsys):
        """Test complete workflow: build, search, print"""
        # Setup
        cli = SearchEngineCLI()
        cli.INDEX_FILE = str(tmp_path / "test_index.json")
        
        # Mock crawler
        mock_crawler = Mock()
        mock_crawler.crawl.return_value = {
            "url1": "hello world python programming",
            "url2": "python is great"
        }
        mock_crawler_class.return_value = mock_crawler
        
        # Step 1: Build
        cli.cmd_build([])
        assert cli.index_loaded is True
        
        # Step 2: Find
        cli.cmd_find(["python"])
        captured = capsys.readouterr()
        assert "url1" in captured.out or "url2" in captured.out
        
        # Step 3: Print
        cli.cmd_print(["python"])
        captured = capsys.readouterr()
        assert "python" in captured.out.lower()
    
    def test_full_workflow_load_and_search(self, tmp_path, capsys):
        """Test complete workflow: create index, load, search"""
        # Setup
        cli = SearchEngineCLI()
        cli.INDEX_FILE = str(tmp_path / "test_index.json")
        
        # Create index file manually
        indexer = InvertedIndex()
        pages = {
            "url1": "hello world",
            "url2": "python programming"
        }
        indexer.build_from_pages(pages)
        indexer.save_to_json(cli.INDEX_FILE)
        
        # Load
        cli.cmd_load([])
        assert cli.index_loaded is True
        
        # Search
        cli.cmd_find(["hello"])
        captured = capsys.readouterr()
        assert "url1" in captured.out
