# Search Engine Tool

A Python-based web crawler and search engine tool for indexing and searching web pages.

## Project Overview

This project implements a simple search engine that:
- Crawls web pages from https://quotes.toscrape.com/
- Builds an inverted index of all words found in the pages
- Allows users to search for pages containing specific terms
- Supports multi-word queries

## Features

- **Web Crawler**: Respects politeness window (6 seconds between requests)
- **Inverted Index**: Stores word statistics (frequency, positions) for each page
- **Case-Insensitive Search**: Treats 'Good' and 'good' as the same word
- **Command-Line Interface**: Easy-to-use shell commands

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. Clone this repository:
```bash
git clone <your-repository-url>
cd cwk2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the search tool:
```bash
python src/main.py
```

### Available Commands

#### 1. build
Crawls the website, builds the index, and saves it to the file system.
```
> build
```

#### 2. load
Loads a previously built index from the file system.
```
> load
```

#### 3. print <word>
Prints the inverted index for a specific word.
```
> print nonsense
```

#### 4. find <query>
Finds all pages containing the search terms.
```
> find indifference
> find good friends
```

#### 5. exit
Exits the search tool.
```
> exit
```

## Project Structure

```
cwk2/
├── src/
│   ├── crawler.py      # Web crawling functionality
│   ├── indexer.py      # Inverted index creation and management
│   ├── search.py       # Search query processing
│   └── main.py         # Command-line interface
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── data/
│   └── [compiled index files]
├── requirements.txt
└── README.md
```

## Testing

Run all tests:
```bash
python -m pytest tests/
```

Run specific test file:
```bash
python -m pytest tests/test_crawler.py
```

Run with coverage:
```bash
python -m pytest --cov=src tests/
```

## Dependencies

- **requests**: HTTP library for making web requests
- **beautifulsoup4**: HTML parsing library
- **pytest**: Testing framework
- **pytest-cov**: Code coverage plugin

See `requirements.txt` for specific versions.

## Development

This project follows incremental development with regular Git commits. Key development practices:

- Modular design with separate components (crawler, indexer, search)
- Comprehensive unit testing for each module
- Version control with meaningful commit messages
- Code documentation and type hints

## License

This project is created for educational purposes as part of COMP/XJCO3011 coursework.

## Author

[Your Name]
[Your Student ID]
