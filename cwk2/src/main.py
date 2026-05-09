"""
Search Engine Tool - Command Line Interface

This is the main entry point for the search engine tool.
It provides a command-line interface with the following commands:
- build: Crawl website and build index
- load: Load previously built index
- print <word>: Print inverted index for a word
- find <query>: Find pages containing search terms
- exit/quit: Exit the program
"""

import os
import sys

# Support both direct execution and module import
try:
    from src.crawler import WebCrawler
    from src.indexer import InvertedIndex
    from src.search import SearchEngine
except ModuleNotFoundError:
    from crawler import WebCrawler
    from indexer import InvertedIndex
    from search import SearchEngine


class SearchEngineCLI:
    """
    Command-line interface for the search engine tool.
    """
    
    # Configuration
    TARGET_URL = "https://quotes.toscrape.com/"
    POLITENESS_DELAY = 6.0  # seconds
    MAX_PAGES = 50
    INDEX_FILE = "data/search_index.json"
    
    def __init__(self):
        """Initialize the CLI."""
        self.indexer = None
        self.search_engine = None
        self.index_loaded = False
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
    
    def print_welcome(self):
        """Print welcome message."""
        print("\n" + "=" * 70)
        print("  SEARCH ENGINE TOOL")
        print("  Target: https://quotes.toscrape.com/")
        print("=" * 70)
        print("\nAvailable commands:")
        print("  build           - Crawl website and build index")
        print("  load            - Load previously built index")
        print("  print <word>    - Print inverted index for a word")
        print("  find <query>    - Find pages containing search terms")
        print("  stats           - Show index statistics")
        print("  help            - Show this help message")
        print("  exit/quit       - Exit the program")
        print("=" * 70 + "\n")
    
    def cmd_build(self, args):
        """
        Build command: Crawl website and create index.
        
        Args:
            args: Command arguments (unused)
        """
        print("\n" + "=" * 70)
        print("BUILDING INDEX")
        print("=" * 70)
        
        # Step 1: Crawl website
        print(f"\n[1/3] Crawling website: {self.TARGET_URL}")
        print(f"      Politeness delay: {self.POLITENESS_DELAY} seconds")
        print(f"      Max pages: {self.MAX_PAGES}")
        print("-" * 70)
        
        crawler = WebCrawler(self.TARGET_URL, politeness_delay=self.POLITENESS_DELAY)
        pages = crawler.crawl(max_pages=self.MAX_PAGES)
        
        if not pages:
            print("\n✗ Error: No pages were crawled. Please check your internet connection.")
            return
        
        # Step 2: Build index
        print(f"\n[2/3] Building inverted index...")
        print("-" * 70)
        
        self.indexer = InvertedIndex()
        self.indexer.build_from_pages(pages)
        
        # Step 3: Save index
        print(f"\n[3/3] Saving index to {self.INDEX_FILE}...")
        print("-" * 70)
        
        try:
            self.indexer.save_to_json(self.INDEX_FILE)
            self.search_engine = SearchEngine(self.indexer)
            self.index_loaded = True
            
            print("\n" + "=" * 70)
            print("✓ BUILD COMPLETE")
            print("=" * 70)
            
            # Show statistics
            stats = self.indexer.get_statistics()
            print(f"\nIndex Statistics:")
            print(f"  Total unique words: {stats['total_unique_words']}")
            print(f"  Total documents: {stats['total_documents']}")
            print(f"  Average words per document: {stats['average_words_per_document']}")
            print("\nYou can now use 'find' and 'print' commands.")
            print("=" * 70 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error saving index: {e}")
    
    def cmd_load(self, args):
        """
        Load command: Load previously built index.
        
        Args:
            args: Command arguments (unused)
        """
        print("\n" + "=" * 70)
        print("LOADING INDEX")
        print("=" * 70)
        
        if not os.path.exists(self.INDEX_FILE):
            print(f"\n✗ Error: Index file '{self.INDEX_FILE}' not found.")
            print("  Please run 'build' command first to create the index.")
            print("=" * 70 + "\n")
            return
        
        try:
            print(f"\nLoading index from {self.INDEX_FILE}...")
            
            self.indexer = InvertedIndex()
            self.indexer.load_from_json(self.INDEX_FILE)
            self.search_engine = SearchEngine(self.indexer)
            self.index_loaded = True
            
            print("\n" + "=" * 70)
            print("✓ LOAD COMPLETE")
            print("=" * 70)
            
            # Show statistics
            stats = self.indexer.get_statistics()
            print(f"\nIndex Statistics:")
            print(f"  Total unique words: {stats['total_unique_words']}")
            print(f"  Total documents: {stats['total_documents']}")
            print(f"  Average words per document: {stats['average_words_per_document']}")
            print("\nYou can now use 'find' and 'print' commands.")
            print("=" * 70 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error loading index: {e}")
            print("=" * 70 + "\n")
    
    def cmd_print(self, args):
        """
        Print command: Print inverted index for a word.
        
        Args:
            args: List containing the word to print
        """
        if not self.index_loaded:
            print("\n✗ Error: No index loaded. Please run 'build' or 'load' first.\n")
            return
        
        if not args:
            print("\n✗ Error: Please specify a word to print.")
            print("  Usage: print <word>\n")
            return
        
        word = args[0].lower()
        
        print("\n" + "=" * 70)
        self.search_engine.print_word_info(word)
        print()
    
    def cmd_find(self, args):
        """
        Find command: Find pages containing search terms.
        
        Args:
            args: List of search terms
        """
        if not self.index_loaded:
            print("\n✗ Error: No index loaded. Please run 'build' or 'load' first.\n")
            return
        
        if not args:
            print("\n✗ Error: Please specify search terms.")
            print("  Usage: find <query>\n")
            return
        
        query = " ".join(args)
        
        print("\n" + "=" * 70)
        self.search_engine.print_search_results(query, max_results=10)
        print()
    
    def cmd_stats(self, args):
        """
        Stats command: Show index statistics.
        
        Args:
            args: Command arguments (unused)
        """
        if not self.index_loaded:
            print("\n✗ Error: No index loaded. Please run 'build' or 'load' first.\n")
            return
        
        print("\n" + "=" * 70)
        print("INDEX STATISTICS")
        print("=" * 70)
        
        stats = self.indexer.get_statistics()
        
        print(f"\nTotal unique words: {stats['total_unique_words']}")
        print(f"Total documents: {stats['total_documents']}")
        print(f"Average words per document: {stats['average_words_per_document']}")
        
        # Additional stats
        all_words = self.indexer.get_all_words()
        if all_words:
            print(f"\nSample words (first 10):")
            for word in sorted(all_words)[:10]:
                count = len(self.indexer.get_pages_containing_word(word))
                print(f"  - '{word}' (in {count} page(s))")
        
        print("=" * 70 + "\n")
    
    def cmd_help(self, args):
        """
        Help command: Show help message.
        
        Args:
            args: Command arguments (unused)
        """
        self.print_welcome()
    
    def cmd_exit(self, args):
        """
        Exit command: Exit the program.
        
        Args:
            args: Command arguments (unused)
        """
        print("\nThank you for using Search Engine Tool!")
        print("Goodbye!\n")
        sys.exit(0)
    
    def parse_command(self, user_input):
        """
        Parse user input into command and arguments.
        
        Args:
            user_input: The user's input string
            
        Returns:
            Tuple of (command, args_list)
        """
        parts = user_input.strip().split()
        
        if not parts:
            return None, []
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return command, args
    
    def execute_command(self, command, args):
        """
        Execute a command.
        
        Args:
            command: The command to execute
            args: List of command arguments
        """
        # Command mapping
        commands = {
            'build': self.cmd_build,
            'load': self.cmd_load,
            'print': self.cmd_print,
            'find': self.cmd_find,
            'stats': self.cmd_stats,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
        }
        
        if command in commands:
            commands[command](args)
        else:
            print(f"\n✗ Unknown command: '{command}'")
            print("  Type 'help' to see available commands.\n")
    
    def run(self):
        """Run the command-line interface."""
        self.print_welcome()
        
        while True:
            try:
                # Get user input
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                # Parse and execute command
                command, args = self.parse_command(user_input)
                
                if command:
                    self.execute_command(command, args)
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted by user.")
                self.cmd_exit([])
            except EOFError:
                print("\n")
                self.cmd_exit([])
            except Exception as e:
                print(f"\n✗ Error: {e}\n")


def main():
    """Main entry point."""
    cli = SearchEngineCLI()
    cli.run()


if __name__ == "__main__":
    main()
