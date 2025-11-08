# Application Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface (CLI)                   │
│                    src/cli/main.py                         │
│  Commands: search, quick, get, download, config            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Search Orchestrator                       │
│                src/search/orchestrator.py                   │
│  - Parallel execution                                       │
│  - Result aggregation                                       │
│  - Ranking algorithm                                        │
└───────┬──────────┬──────────┬──────────────────────────────┘
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌──────────┐
   │PubMed  │ │ arXiv  │ │Crossref  │
   │Search  │ │Search  │ │  Search  │
   └────────┘ └────────┘ └──────────┘
        │          │          │
        └──────────┴──────────┘
                   │
                   ▼
        ┌───────────────────┐
        │   Deduplicator    │
        │  - DOI matching   │
        │  - PMID matching  │
        │  - Title similarity│
        └─────────┬─────────┘
                  │
                  ▼
        ┌──────────────────┐
        │   Paper Models   │
        │   (Pydantic)     │
        └─────────┬────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────┐   ┌──────────────┐
│ PDF Retriever│   │ JSON Export  │
│  - PMC       │   │  - Results   │
│  - arXiv     │   │  - Metadata  │
│  - Unpaywall │   └──────────────┘
└──────────────┘
```

## Component Details

### 1. CLI Layer (`src/cli/main.py`)
- **Purpose**: User interface
- **Framework**: Click + Rich
- **Features**:
  - Command parsing
  - Progress indicators
  - Table formatting
  - Error display

### 2. Search Orchestrator (`src/search/orchestrator.py`)
- **Purpose**: Coordinate multi-source searches
- **Features**:
  - Parallel API calls
  - Result aggregation
  - Ranking algorithm
  - Error handling per source

### 3. Search Providers
#### PubMed (`src/search/pubmed.py`)
- **API**: NCBI E-utilities
- **Coverage**: Biomedical literature
- **Features**: Full metadata, PMC links

#### arXiv (`src/search/arxiv.py`)
- **API**: arXiv API
- **Coverage**: Preprints
- **Features**: Direct PDF access

#### Crossref (`src/search/crossref.py`)
- **API**: Crossref REST API
- **Coverage**: DOI registry
- **Features**: Citation counts

### 4. Deduplicator (`src/search/deduplicator.py`)
- **Strategy**:
  1. Exact DOI matching
  2. Exact PMID matching
  3. Title similarity (85% threshold)
- **Output**: Merged paper records

### 5. Data Models (`src/models.py`)
- **Framework**: Pydantic
- **Models**:
  - `Paper`: Paper metadata
  - `Author`: Author information
  - `SearchQuery`: Search parameters
  - `SearchResult`: Search results

### 6. PDF Retriever (`src/retrieval/pdf_retriever.py`)
- **Strategies** (in order):
  1. PubMed Central
  2. arXiv
  3. Direct URL
  4. Unpaywall
- **Features**: Concurrent downloads

### 7. Utilities
#### Config (`src/utils/config.py`)
- Environment variables
- Directory management
- Default settings

#### Rate Limiter (`src/utils/rate_limiter.py`)
- Token bucket algorithm
- Per-source limits
- Async support

## Data Flow

```
User Query
    │
    ▼
CLI Parsing
    │
    ▼
SearchQuery Model
    │
    ▼
Orchestrator
    │
    ├──────┬──────┐
    ▼      ▼      ▼
  PubMed arXiv Crossref
    │      │      │
    └──────┴──────┘
          │
          ▼
    Raw Results
          │
          ▼
   Deduplication
          │
          ▼
    Paper Models
          │
    ┌─────┴─────┐
    ▼           ▼
 Ranking    Storage
    │
    ▼
 Display/Export
```

## Error Handling

```
┌──────────────┐
│ API Call     │
└──────┬───────┘
       │
       ├─ Success ──────────────────┐
       │                            │
       └─ Error                     │
           │                        │
           ├─ Rate Limit            │
           │   └─ Wait & Retry      │
           │                        │
           ├─ Network Error         │
           │   └─ Log & Continue    │
           │                        │
           └─ Parse Error           │
               └─ Log & Skip        │
                                    │
                                    ▼
                            ┌───────────────┐
                            │ Partial Results│
                            └───────────────┘
```

## Concurrency Model

```
Main Thread
    │
    └─ ThreadPoolExecutor (max 5 workers)
           │
           ├─ Worker 1: PubMed search
           ├─ Worker 2: arXiv search
           ├─ Worker 3: Crossref search
           ├─ Worker 4: PDF download 1
           └─ Worker 5: PDF download 2
                    │
                    └─ Rate limiter ensures proper spacing
```

## File Organization

```
src/
├── models.py              # Data models (Pydantic)
│   └── Paper, Author, SearchQuery, SearchResult
│
├── search/
│   ├── base.py           # BaseSearchProvider (ABC)
│   ├── pubmed.py         # PubMed implementation
│   ├── arxiv.py          # arXiv implementation
│   ├── crossref.py       # Crossref implementation
│   ├── orchestrator.py   # SearchOrchestrator
│   └── deduplicator.py   # Deduplicator
│
├── retrieval/
│   └── pdf_retriever.py  # PDFRetriever
│
├── utils/
│   ├── config.py         # Config
│   └── rate_limiter.py   # RateLimiter
│
├── auth/
│   └── session_manager.py # SessionManager
│
└── cli/
    └── main.py           # CLI (Click + Rich)
```

## Design Patterns

### 1. Strategy Pattern
- **Where**: Search providers
- **Why**: Easy to add new sources
- **Example**: `BaseSearchProvider` → `PubMedSearch`, `ArxivSearch`

### 2. Facade Pattern
- **Where**: SearchOrchestrator
- **Why**: Simplify complex multi-source operations
- **Example**: Single `search()` method coordinates all sources

### 3. Builder Pattern
- **Where**: Pydantic models
- **Why**: Flexible object construction with validation
- **Example**: `Paper.model_validate(data)`

### 4. Singleton Pattern
- **Where**: Config
- **Why**: Single source of truth for settings
- **Example**: `Config` class with class variables

## Extension Points

### Adding a New Search Source

1. Create new file: `src/search/newsource.py`
2. Inherit from `BaseSearchProvider`
3. Implement `search()` and `get_paper_by_id()`
4. Register in `SearchOrchestrator.__init__()`
5. Add to `Source` enum in `models.py`

Example:
```python
from src.search.base import BaseSearchProvider
from src.models import Source

class NewSourceSearch(BaseSearchProvider):
    def __init__(self):
        super().__init__(rate_limit=2.0)
        self.source = Source.NEW_SOURCE
    
    def search(self, query: SearchQuery) -> List[Paper]:
        # Implementation
        pass
    
    def get_paper_by_id(self, id: str) -> Optional[Paper]:
        # Implementation
        pass
```

### Adding a New CLI Command

1. Add function to `src/cli/main.py`
2. Decorate with `@cli.command()`
3. Use Click options for parameters
4. Use Rich for output formatting

Example:
```python
@cli.command()
@click.argument('topic')
def analyze(topic: str):
    """Analyze papers on a topic"""
    # Implementation
    pass
```

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Search | O(n) per source | O(n) |
| Deduplication | O(n²) worst case | O(n) |
| Ranking | O(n log n) | O(1) |
| PDF Download | O(1) per paper | O(1) |

Where n = number of papers

## Security Considerations

1. **API Keys**: Stored in `.env`, never committed
2. **Rate Limiting**: Respects API terms of service
3. **Input Validation**: Pydantic models validate all data
4. **File Paths**: Sanitized to prevent path traversal
5. **Network**: Timeouts prevent hanging
6. **Dependencies**: Minimal, well-maintained packages

## Scalability

### Current Limits
- Papers per search: 100 per source (configurable)
- Concurrent requests: 5 (configurable)
- PDF downloads: 3 concurrent (configurable)

### Scaling Options
1. **Caching**: Add Redis for result caching
2. **Queue**: Add Celery for background processing
3. **Database**: Switch from JSON to PostgreSQL
4. **API**: Wrap in FastAPI for web service

## Testing Strategy

```
Tests
├── Unit Tests
│   ├── test_models.py          # Data models
│   ├── test_deduplicator.py    # Deduplication logic
│   ├── test_rate_limiter.py    # Rate limiting
│   └── test_ranking.py         # Ranking algorithm
│
├── Integration Tests
│   ├── test_pubmed.py          # PubMed API
│   ├── test_arxiv.py           # arXiv API
│   └── test_crossref.py        # Crossref API
│
└── End-to-End Tests
    ├── test_search.py          # Full search flow
    └── test_cli.py             # CLI commands
```

## Deployment

```
Development
    │
    ├─ pip install -r requirements.txt
    └─ python -m src.cli.main
    
Production
    │
    ├─ pip install -e .
    ├─ litsearch (installed command)
    └─ Optional: Docker container
```

---

**Architecture Version**: 0.1.0
**Last Updated**: November 7, 2025
