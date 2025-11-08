# Literature Search Application

An intelligent academic literature search tool that aggregates results from multiple databases, downloads PDFs, and provides comprehensive search capabilities.

## Features

- **Multi-source search**: Search across PubMed, arXiv, and Crossref simultaneously
- **Intelligent deduplication**: Automatically merges duplicate papers from different sources
- **PDF retrieval**: Download open-access PDFs from PMC, arXiv, and Unpaywall
- **Smart ranking**: Papers ranked by relevance, citations, and recency
- **Rich CLI**: Beautiful command-line interface with tables and progress indicators
- **Flexible filtering**: Filter by year, paper type, authors, and journals

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install from source

```bash
# Clone the repository (or create the directory)
cd litsearchapp

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Quick Start

### Basic search

```bash
# Simple search
litsearch search "CRISPR gene editing"

# Search with specific sources and download PDFs
litsearch search "machine learning healthcare" -s pubmed -s arxiv --download

# Quick search (minimal output)
litsearch quick "coral bleaching"
```

### Advanced search

```bash
# Search with filters
litsearch search "cancer immunotherapy" \
    --sources pubmed arxiv crossref \
    --year-start 2020 \
    --year-end 2024 \
    --max-results 100 \
    --output results.json \
    --download
```

### Get specific paper

```bash
# Get by DOI
litsearch get "10.1038/nature12373"

# Get by PubMed ID
litsearch get "35360497" --source pubmed

# Get by arXiv ID
litsearch get "2301.08727" --source arxiv
```

### Download PDFs from saved results

```bash
# Download papers from previous search
litsearch download results.json --max-papers 50
```

## Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Optional API keys for enhanced features
ANTHROPIC_API_KEY=your_key_here  # For AI synthesis
OPENAI_API_KEY=your_key_here     # Alternative to Anthropic
SERPAPI_KEY=your_key_here        # For Google Scholar (paid)

# Rate limiting (requests per second)
PUBMED_RATE_LIMIT=3
ARXIV_RATE_LIMIT=1
CROSSREF_RATE_LIMIT=2

# Directories
CACHE_DIR=./cache
PAPERS_DIR=./papers
OUTPUT_DIR=./output
```

## Search Sources

### Currently Supported

1. **PubMed**: Biomedical literature via NCBI E-utilities (free, no API key required)
2. **arXiv**: Preprints in physics, mathematics, computer science, etc. (free)
3. **Crossref**: DOI registry with broad academic coverage (free)

### Coming Soon

- Google Scholar (via scholarly library)
- Semantic Scholar
- Web of Science (requires subscription)

## Command Reference

### `search` - Main search command

```bash
litsearch search QUERY [OPTIONS]

Options:
  -s, --sources [pubmed|arxiv|crossref|scholar]  Sources to search
  -n, --max-results INTEGER                       Maximum results
  --year-start INTEGER                            Start year filter
  --year-end INTEGER                              End year filter
  -o, --output PATH                               Save results to JSON
  --download/--no-download                        Download PDFs
```

### `download` - Download PDFs from results

```bash
litsearch download RESULTS_FILE [OPTIONS]

Options:
  -n, --max-papers INTEGER     Maximum papers to download
  -c, --concurrent INTEGER     Concurrent downloads
```

### `get` - Get specific paper

```bash
litsearch get IDENTIFIER [OPTIONS]

Options:
  -s, --source [pubmed|arxiv|crossref]  Source hint
```

### `quick` - Quick search with defaults

```bash
litsearch quick QUERY
```

### `config` - Show configuration

```bash
litsearch config
```

## Output Format

Search results can be saved as JSON with complete metadata:

```json
{
  "query": {
    "query": "search terms",
    "sources": ["pubmed", "arxiv"],
    "max_results": 50
  },
  "statistics": {
    "total_papers": 47,
    "search_time": 3.24,
    "avg_citations": 23.5,
    "papers_by_source": {
      "pubmed": 30,
      "arxiv": 17
    }
  },
  "papers": [
    {
      "title": "Paper Title",
      "authors": [...],
      "year": 2023,
      "doi": "10.1234/example",
      "abstract": "...",
      "citations": 42
    }
  ]
}
```

## Features in Development

- [ ] AI-powered synthesis of search results
- [ ] Citation network analysis
- [ ] Google Scholar integration
- [ ] Export to BibTeX/RIS
- [ ] Web interface
- [ ] Saved search alerts
- [ ] Full-text search in downloaded PDFs

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License

## Acknowledgments

- PubMed E-utilities for biomedical literature access
- arXiv for open access to scientific preprints
- Crossref for DOI metadata
- Unpaywall for open access paper discovery