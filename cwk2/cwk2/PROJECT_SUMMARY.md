# Search Engine Tool - Project Summary

## 📊 Project Overview

A complete search engine implementation for crawling, indexing, and searching web pages from https://quotes.toscrape.com/

**Course**: COMP/XJCO3011 - Web Services and Web Data  
**Assignment**: Coursework 2 - Search Engine Tool  
**Completion Date**: May 2026

---

## ✅ Implementation Status

### Core Features (100% Complete)

- ✅ **Web Crawler** - Crawls website with 6-second politeness window
- ✅ **Inverted Index** - Stores word frequencies and positions
- ✅ **Search Engine** - Single and multi-word queries with ranking
- ✅ **Command-Line Interface** - All 4 required commands implemented
- ✅ **Persistence** - Save/load index to JSON format
- ✅ **Comprehensive Testing** - 123 unit and integration tests

---

## 📁 Project Structure

```
cwk2/
├── src/
│   ├── __init__.py         # Package initialization
│   ├── crawler.py          # Web crawling (244 lines)
│   ├── indexer.py          # Inverted index (380 lines)
│   ├── search.py           # Search engine (383 lines)
│   └── main.py             # CLI interface (330 lines)
├── tests/
│   ├── __init__.py
│   ├── test_crawler.py     # 19 tests
│   ├── test_indexer.py     # 33 tests
│   ├── test_search.py      # 43 tests
│   └── test_main.py        # 28 tests
├── data/
│   └── .gitkeep
├── .gitignore
├── README.md
├── requirements.txt
└── PROJECT_SUMMARY.md
```

**Total Lines of Code**: ~1,337 lines (excluding tests)  
**Total Test Cases**: 123 tests  
**Test Coverage**: 83%

---

## 🎯 Command-Line Interface

### Available Commands

```bash
> build              # Crawl website and build index
> load               # Load previously built index
> print <word>       # Print inverted index for a word
> find <query>       # Find pages containing search terms
> stats              # Show index statistics
> help               # Show help message
> exit/quit          # Exit the program
```

### Usage Examples

```bash
# Start the tool
python src/main.py

# Build index (first time)
> build

# Search for single word
> find love

# Search for multiple words (AND operation)
> find good friends

# Print word information
> print nonsense

# View statistics
> stats

# Exit
> exit
```

---

## 🔧 Technical Implementation

### 1. Web Crawler (`crawler.py`)

**Key Features:**
- Respects 6-second politeness window between requests
- Extracts clean text from HTML (removes scripts, styles)
- Handles relative and absolute URLs
- Filters external links and file types
- Case-insensitive word processing

**Main Classes:**
- `WebCrawler` - Main crawler class with configurable politeness delay

**Dependencies:**
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing

---

### 2. Inverted Index (`indexer.py`)

**Key Features:**
- Stores word frequency and positions for each page
- Case-insensitive indexing
- Efficient lookup and retrieval
- Supports JSON and Pickle serialization

**Data Structure:**
```python
{
    "word": {
        "url": {
            "frequency": int,
            "positions": [int, int, ...]
        }
    }
}
```

**Main Classes:**
- `InvertedIndex` - Core index data structure

**Key Methods:**
- `build_from_pages()` - Build index from crawled pages
- `get_word_info()` - Get word statistics
- `get_pages_containing_word()` - Single word search
- `get_pages_containing_all_words()` - Multi-word search
- `save_to_json()` / `load_from_json()` - Persistence

---

### 3. Search Engine (`search.py`)

**Key Features:**
- Single and multi-word queries
- Ranking by term frequency (TF)
- Case-insensitive search
- Query validation and cleaning

**Main Classes:**
- `SearchEngine` - Main search interface
- `QueryValidator` - Query validation utilities

**Ranking Algorithm:**
- Score = Sum of term frequencies across all query terms
- Results sorted by score (descending)

---

### 4. Command-Line Interface (`main.py`)

**Key Features:**
- Interactive shell interface
- Error handling and user feedback
- Progress indicators during crawling
- Formatted output for search results

**Main Classes:**
- `SearchEngineCLI` - Command-line interface controller

**Configuration:**
- Target URL: https://quotes.toscrape.com/
- Politeness Delay: 6.0 seconds
- Max Pages: 50
- Index File: data/search_index.json

---

## 🧪 Testing

### Test Coverage Summary

| Module | Statements | Coverage |
|--------|-----------|----------|
| crawler.py | 104 | 85% |
| indexer.py | 141 | 77% |
| search.py | 126 | 83% |
| main.py | 176 | 86% |
| **TOTAL** | **548** | **83%** |

### Test Categories

**Unit Tests:**
- Crawler: URL validation, text extraction, link parsing
- Indexer: Tokenization, index building, persistence
- Search: Query parsing, ranking, result retrieval
- CLI: Command parsing, error handling

**Integration Tests:**
- Full workflow: build → search → print
- Load and search workflow
- Error scenarios

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_crawler.py -v
```

---

## 📦 Dependencies

```
requests==2.31.0        # HTTP library
beautifulsoup4==4.12.3  # HTML parsing
pytest==7.4.3           # Testing framework
pytest-cov==4.1.0       # Coverage plugin
```

**Installation:**
```bash
pip install -r requirements.txt
```

---

## 🎓 Key Learning Outcomes

### Technical Skills Demonstrated

1. **Web Crawling**
   - HTTP request handling
   - HTML parsing with BeautifulSoup
   - Politeness and rate limiting
   - URL normalization

2. **Data Structures**
   - Inverted index design
   - Efficient word lookup
   - Position tracking

3. **Search Algorithms**
   - Term frequency ranking
   - Multi-word query processing
   - Result scoring and sorting

4. **Software Engineering**
   - Modular design (4 separate modules)
   - Comprehensive testing (123 tests, 83% coverage)
   - Error handling and validation
   - User-friendly CLI

5. **Python Best Practices**
   - Type hints
   - Docstrings
   - PEP 8 style
   - Object-oriented design

---

## 🚀 Performance Characteristics

### Crawling Performance
- **Politeness Delay**: 6 seconds between requests
- **Time to crawl 50 pages**: ~5-6 minutes
- **Network efficiency**: Single request per page

### Index Performance
- **Build time**: ~1 second for 50 pages
- **Index size**: ~500KB for 50 pages (JSON)
- **Search time**: <1ms for typical queries

### Memory Usage
- **Crawler**: Minimal (processes one page at a time)
- **Index**: ~10MB for 50 pages in memory
- **Search**: Constant time lookup

---

## 🔍 Example Output

### Build Command
```
> build

======================================================================
BUILDING INDEX
======================================================================

[1/3] Crawling website: https://quotes.toscrape.com/
      Politeness delay: 6.0 seconds
      Max pages: 50
----------------------------------------------------------------------
Fetching: https://quotes.toscrape.com
✓ Crawled 1/50: https://quotes.toscrape.com
...
----------------------------------------------------------------------
Crawling complete! Total pages crawled: 50

[2/3] Building inverted index...
----------------------------------------------------------------------
✓ Index built successfully!
  Total unique words: 1250
  Total documents: 50

[3/3] Saving index to data/search_index.json...
----------------------------------------------------------------------
✓ Index saved to data/search_index.json

======================================================================
✓ BUILD COMPLETE
======================================================================

Index Statistics:
  Total unique words: 1250
  Total documents: 50
  Average words per document: 245.6
```

### Find Command
```
> find love inspirational

======================================================================
Search query: 'love inspirational'
======================================================================
Found 8 result(s):

1. https://quotes.toscrape.com/tag/inspirational/
   Relevance score: 15.00
   Term frequencies: 'love': 8, 'inspirational': 7

2. https://quotes.toscrape.com/tag/love/
   Relevance score: 12.00
   Term frequencies: 'love': 10, 'inspirational': 2
...
======================================================================
```

---

## 📝 Design Decisions

### 1. Data Structure Choice
**Decision**: Dictionary-based inverted index  
**Rationale**: O(1) lookup time, easy serialization, Python-native

### 2. Persistence Format
**Decision**: JSON (with Pickle as alternative)  
**Rationale**: Human-readable, debuggable, cross-platform

### 3. Ranking Algorithm
**Decision**: Simple term frequency (TF)  
**Rationale**: Effective for small corpus, easy to understand and implement

### 4. Politeness Implementation
**Decision**: Time-based delay with tracking  
**Rationale**: Ensures compliance, simple to verify

### 5. Case Sensitivity
**Decision**: Case-insensitive throughout  
**Rationale**: Better user experience, matches requirement

---

## ✨ Future Enhancements (Optional)

- [ ] TF-IDF ranking for better relevance
- [ ] Phrase search (exact match)
- [ ] Stemming/lemmatization
- [ ] Web interface (Flask/Django)
- [ ] Incremental indexing
- [ ] Multi-threaded crawling (with politeness)
- [ ] Search result caching
- [ ] Fuzzy matching

---

## 📚 References

- **Target Website**: https://quotes.toscrape.com/
- **Requests Documentation**: https://docs.python-requests.org/
- **BeautifulSoup Documentation**: https://www.crummy.com/software/BeautifulSoup/
- **Inverted Index**: https://en.wikipedia.org/wiki/Inverted_index

---

## ✅ Checklist for Submission

- [x] All 4 commands implemented (build, load, print, find)
- [x] 6-second politeness window enforced
- [x] Case-insensitive search
- [x] Inverted index with frequency and positions
- [x] Save/load functionality
- [x] Comprehensive testing (123 tests)
- [x] README.md with usage instructions
- [x] requirements.txt with dependencies
- [x] Clean project structure
- [x] Git version control ready
- [x] Code documentation and comments

---

**Project Status**: ✅ **COMPLETE AND READY FOR SUBMISSION**

**Next Steps**:
1. Upload to GitHub
2. Record 5-minute video demonstration
3. Submit via Minerva
