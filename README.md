# Literature Search Application

A full-stack academic literature search platform that aggregates results from 7 major databases, provides intelligent deduplication and ranking, and offers ResearchRabbit-style discovery features through citation networks.

## Key Features

- **Multi-source search**: Search across PubMed, arXiv, Crossref, Google Scholar, Web of Science, Semantic Scholar, and OpenAlex simultaneously
- **Intelligent deduplication**: Automatically merge duplicate papers using DOI, PMID, arXiv ID, and title similarity matching
- **Smart ranking**: Papers ranked by relevance, citations, recency, and source diversity
- **ResearchRabbit-style discovery**: Explore citations, references, recommendations, and related papers
- **Citation network visualization**: Interactive graph visualization of paper relationships
- **UCSB library integration**: Access paywalled content through institutional proxy
- **Modern UI**: React frontend with dark/light themes, responsive design, and keyboard shortcuts
- **PDF retrieval**: Multi-strategy download from PMC, arXiv, Unpaywall, and institutional access

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 16+
- pip and npm

### Installation

```bash
# Clone the repository
git clone https://github.com/adrianstier/litsearchapp.git
cd litsearchapp

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the Application

**Start both servers** (recommended to run in separate terminals):

```bash
# Terminal 1: Start backend (port 8000)
cd backend
uvicorn main:app --reload

# Terminal 2: Start frontend (port 5173)
cd frontend
npm run dev
```

**Access the application**: Open http://localhost:5173 in your browser

## Search Sources

| Source | Coverage | Rate Limit | Auth Required |
|--------|----------|------------|---------------|
| PubMed | 35M+ biomedical papers | 3/s | No |
| arXiv | 2M+ preprints | 1/s | No |
| Crossref | 150M+ DOI records | 2/s | No |
| Google Scholar | Citation database | 0.5/s | No |
| Web of Science | Premium research DB | 0.5/s | UCSB |
| Semantic Scholar | 200M+ papers with AI | 2/s | No |
| OpenAlex | 250M+ works | 10/s | No |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React Frontend │ ←→  │   FastAPI Backend │ ←→  │   SQLite Database │
│   (Port 5173)    │     │   (Port 8000)    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │   External APIs       │
                    │   (7 Search Sources)  │
                    └──────────────────────┘
```

### Tech Stack

**Backend**: Python, FastAPI, SQLAlchemy, SQLite, Pydantic
**Frontend**: React 19, Vite, React Router, Axios, Recharts, vis-network

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Search | `/` | Multi-source search with filters |
| Library | `/library` | Browse saved papers with full-text search |
| Paper Detail | `/paper/:id` | Discovery tabs (citations, references, recommendations, network) |
| Collections | `/collections` | Organize papers into folders |
| Visualizations | `/visualizations` | Timeline, network, and topic charts |
| Settings | `/settings` | UCSB authentication setup |

## API Endpoints

The backend exposes 30+ REST endpoints:

- **Search**: `POST /api/search`, `GET /api/search/history`
- **Papers**: CRUD operations, PDF download, text extraction
- **Discovery**: Recommendations, citations, references, related papers, network
- **Collections**: Create, list, add papers
- **Downloads**: Single and batch PDF download
- **Visualizations**: Timeline, network, topics
- **Auth**: UCSB cookie import, status, clear

## Configuration

Create a `.env` file in the project root:

```bash
# Optional API keys
ANTHROPIC_API_KEY=      # For AI synthesis
OPENAI_API_KEY=         # Alternative AI
SERPAPI_KEY=            # Google Scholar enhancement
CROSSREF_MAILTO=        # Polite pool access

# Rate limits (requests per second)
PUBMED_RATE_LIMIT=3
ARXIV_RATE_LIMIT=1
CROSSREF_RATE_LIMIT=2

# Directories
CACHE_DIR=./cache
PAPERS_DIR=./papers
OUTPUT_DIR=./output
```

## UCSB Library Access

To access paywalled content through UCSB library:

1. Log into the UCSB library website in your browser
2. Export your cookies using a browser extension
3. Go to Settings page in the app
4. Upload the cookies file
5. The app will use these credentials for proxy access

## CLI Usage (Legacy)

The application also includes a CLI for quick searches:

```bash
# Simple search
litsearch search "CRISPR gene editing"

# Search with specific sources
litsearch search "machine learning healthcare" -s pubmed -s arxiv --download

# Quick search
litsearch quick "coral bleaching"

# Get specific paper by DOI
litsearch get "10.1038/nature12373"
```

## Documentation

- **[Product Requirements Document (PRD)](docs/PRD.md)** - Complete product specifications, features, and technical requirements
- **[AI Agent Development System](agents/README.md)** - 10 specialized AI agents for developing and improving the application

## Project Structure

```
litsearchapp/
├── agents/                  # AI development agents
│   ├── README.md           # Agent overview and usage
│   ├── WORKFLOW-INTEGRATION.md
│   └── agent-*.md          # 10 specialized agents
├── artifacts/              # Agent outputs (PRDs, plans, etc.)
├── backend/                 # FastAPI REST API
│   ├── main.py             # Main application (30+ endpoints)
│   └── services/           # Business logic
├── frontend/               # React + Vite application
│   ├── src/
│   │   ├── pages/         # 6 main pages
│   │   ├── components/    # Reusable components
│   │   ├── services/      # API client
│   │   └── context/       # Theme provider
│   └── package.json
├── src/                    # Core Python library
│   ├── models.py           # Pydantic data models
│   ├── search/             # 7 search providers
│   │   ├── orchestrator.py # Multi-source coordinator
│   │   ├── pubmed.py
│   │   ├── arxiv.py
│   │   ├── crossref.py
│   │   ├── scholar.py
│   │   ├── wos.py
│   │   ├── semantic_scholar.py
│   │   └── openalex.py
│   ├── retrieval/          # PDF download
│   ├── database/           # SQLAlchemy models
│   └── auth/               # UCSB authentication
├── database/               # SQLite database
├── docs/                   # Documentation
│   └── PRD.md             # Product Requirements
└── requirements.txt        # Python dependencies
```

## Development

### Running Tests

```bash
# Run backend tests
pytest tests/ -v

# Run frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build
```

## Roadmap

### Current (v1.0)
- ✅ Multi-source search (7 sources)
- ✅ Intelligent deduplication
- ✅ Smart ranking
- ✅ Discovery features (citations, references, recommendations)
- ✅ Citation network visualization
- ✅ UCSB library authentication
- ✅ Modern React UI with themes
- ✅ PDF retrieval and extraction

### Future
- [ ] AI-powered synthesis of search results
- [ ] Export to BibTeX/RIS/EndNote
- [ ] Browser extension
- [ ] Email alerts for saved searches
- [ ] Multi-user support
- [ ] Full-text search within PDFs

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License

## Acknowledgments

- PubMed E-utilities for biomedical literature access
- arXiv for open access to scientific preprints
- Crossref for DOI metadata
- Semantic Scholar for AI-enhanced paper metadata
- OpenAlex for open research metadata
- Unpaywall for open access paper discovery
