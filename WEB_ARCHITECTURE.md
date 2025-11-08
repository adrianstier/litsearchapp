# Web Frontend Architecture

## Overview

Full-stack web application with:
- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **Database**: SQLite with full-text search
- **Visualizations**: D3.js, Plotly
- **PDF Processing**: PyMuPDF for text extraction

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  - Search Interface                                         │
│  - Paper Visualizations (network, timeline, citations)     │
│  - PDF Viewer                                              │
│  - Collections Management                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/REST
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│  - /api/search - Execute searches                          │
│  - /api/papers - CRUD operations                           │
│  - /api/download - PDF downloads                           │
│  - /api/auth - UCSB authentication                         │
│  - /api/visualize - Generate graph data                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐  ┌──────────┐  ┌─────────┐
│SQLite DB│  │Search    │  │PDF Text │
│Papers   │  │Engine    │  │Extract  │
│PDFs     │  │(existing)│  │PyMuPDF  │
└─────────┘  └──────────┘  └─────────┘
```

## Features

### 1. Search Interface
- Advanced search with filters
- Real-time results
- Source selection
- Year range sliders
- Save searches

### 2. Visualizations
- **Citation Network**: Interactive graph of paper relationships
- **Timeline**: Papers by year with filters
- **Topic Clustering**: Similar papers grouped
- **Author Network**: Co-authorship visualization
- **Journal Distribution**: Pie/bar charts

### 3. Paper Management
- Collections/folders
- Tags and notes
- Export to BibTeX/RIS
- Full-text search across PDFs
- Reading progress tracking

### 4. PDF Viewer
- Built-in PDF reader
- Highlight and annotate
- Extract text
- Search within PDF

## Technology Stack

### Backend
- **FastAPI**: Modern, fast API framework
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation (already using)
- **PyMuPDF**: PDF text extraction
- **asyncio**: Async operations

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool
- **TanStack Query**: Data fetching
- **Zustand**: State management
- **D3.js**: Network visualizations
- **Plotly**: Charts and graphs
- **React-PDF**: PDF rendering
- **Tailwind CSS**: Styling

### Database
- **SQLite**: Local database
- **FTS5**: Full-text search
- **SQLAlchemy**: ORM

## Database Schema

```sql
-- Papers table
CREATE TABLE papers (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    doi TEXT UNIQUE,
    pmid TEXT,
    arxiv_id TEXT,
    abstract TEXT,
    year INTEGER,
    journal TEXT,
    citations INTEGER,
    paper_type TEXT,
    url TEXT,
    pdf_url TEXT,
    local_pdf_path TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(doi, pmid, arxiv_id)
);

-- Authors table
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    orcid TEXT
);

-- Paper-Author relationship
CREATE TABLE paper_authors (
    paper_id INTEGER,
    author_id INTEGER,
    author_order INTEGER,
    FOREIGN KEY (paper_id) REFERENCES papers(id),
    FOREIGN KEY (author_id) REFERENCES authors(id)
);

-- PDF content (full text)
CREATE TABLE pdf_content (
    paper_id INTEGER PRIMARY KEY,
    full_text TEXT,
    extracted_at TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

-- Full-text search index
CREATE VIRTUAL TABLE papers_fts USING fts5(
    title, abstract, content='papers'
);

CREATE VIRTUAL TABLE pdf_fts USING fts5(
    full_text, content='pdf_content'
);

-- Collections
CREATE TABLE collections (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP
);

-- Paper-Collection relationship
CREATE TABLE collection_papers (
    collection_id INTEGER,
    paper_id INTEGER,
    added_at TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES collections(id),
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

-- Search history
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    sources TEXT,
    filters TEXT,
    results_count INTEGER,
    searched_at TIMESTAMP
);

-- Tags
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Paper tags
CREATE TABLE paper_tags (
    paper_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (paper_id) REFERENCES papers(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- Notes
CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    paper_id INTEGER,
    content TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);
```

## API Endpoints

### Search
- `POST /api/search` - Execute search
- `GET /api/search/history` - Get search history
- `GET /api/search/{id}` - Get saved search

### Papers
- `GET /api/papers` - List papers (paginated)
- `GET /api/papers/{id}` - Get paper details
- `POST /api/papers` - Add paper
- `PUT /api/papers/{id}` - Update paper
- `DELETE /api/papers/{id}` - Delete paper
- `GET /api/papers/{id}/pdf` - Get PDF
- `GET /api/papers/{id}/text` - Get extracted text
- `POST /api/papers/{id}/extract` - Extract PDF text
- `GET /api/papers/search?q=` - Full-text search

### Collections
- `GET /api/collections` - List collections
- `POST /api/collections` - Create collection
- `GET /api/collections/{id}/papers` - Get papers in collection
- `POST /api/collections/{id}/papers` - Add paper to collection

### Visualization
- `GET /api/visualize/network` - Citation network data
- `GET /api/visualize/timeline` - Timeline data
- `GET /api/visualize/topics` - Topic clustering
- `GET /api/visualize/authors` - Author network

### Download
- `POST /api/download/{paper_id}` - Download paper
- `POST /api/download/batch` - Batch download

### Auth
- `POST /api/auth/import-cookies` - Import UCSB cookies
- `GET /api/auth/status` - Check auth status
- `DELETE /api/auth/clear` - Clear auth

## Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Search/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchFilters.tsx
│   │   │   └── SearchResults.tsx
│   │   ├── Papers/
│   │   │   ├── PaperCard.tsx
│   │   │   ├── PaperDetail.tsx
│   │   │   └── PaperList.tsx
│   │   ├── Visualizations/
│   │   │   ├── CitationNetwork.tsx
│   │   │   ├── Timeline.tsx
│   │   │   ├── TopicClusters.tsx
│   │   │   └── AuthorNetwork.tsx
│   │   ├── Collections/
│   │   │   ├── CollectionList.tsx
│   │   │   └── CollectionView.tsx
│   │   └── PDF/
│   │       ├── PDFViewer.tsx
│   │       └── PDFSearch.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Search.tsx
│   │   ├── Library.tsx
│   │   ├── Visualize.tsx
│   │   └── Settings.tsx
│   ├── api/
│   │   └── client.ts
│   ├── stores/
│   │   ├── searchStore.ts
│   │   └── papersStore.ts
│   └── App.tsx
├── package.json
└── vite.config.ts
```

## Implementation Plan

### Phase 1: Backend (2-3 hours)
1. Create database models
2. Build FastAPI server
3. Create API endpoints
4. Add PDF text extraction

### Phase 2: Frontend Basic (2-3 hours)
1. Set up React + Vite
2. Create search interface
3. Build paper list/detail views
4. Add PDF viewer

### Phase 3: Visualizations (2-3 hours)
1. Citation network graph
2. Timeline visualization
3. Topic clustering
4. Author networks

### Phase 4: Advanced Features (1-2 hours)
1. Collections management
2. Full-text search
3. Export functionality
4. Settings and preferences

## Running the Application

### Development
```bash
# Backend
cd backend
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

### Production
```bash
# Build frontend
cd frontend
npm run build

# Serve with FastAPI
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Deployment Options

1. **Local**: Run on localhost
2. **Docker**: Containerize both frontend and backend
3. **Cloud**: Deploy to Vercel (frontend) + Railway (backend)

## Next Steps

1. Implement database layer
2. Build FastAPI backend
3. Create React frontend
4. Add visualizations
5. Test and document