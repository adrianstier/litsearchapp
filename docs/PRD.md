# Product Requirements Document (PRD)

## Literature Search Application

**Version:** 1.0
**Last Updated:** November 2024
**Status:** Production Ready

---

## Executive Summary

The Literature Search Application is a full-stack academic research tool that aggregates results from 7 major academic databases, provides intelligent deduplication and ranking, and offers advanced discovery features similar to ResearchRabbit. The application helps researchers efficiently find, organize, and explore academic literature through a modern web interface with institutional (UCSB) library integration.

---

## Problem Statement

### Current Pain Points for Researchers

1. **Fragmented Search Experience**: Researchers must manually search multiple databases (PubMed, arXiv, Google Scholar, etc.) and manually combine results
2. **Duplicate Results**: Same papers appear across multiple sources with inconsistent metadata
3. **Limited Discovery**: Traditional search only finds papers matching keywords, missing related work and citation networks
4. **Paywall Barriers**: Accessing full PDFs often requires navigating institutional access separately
5. **Poor Organization**: Managing papers across multiple tools without unified library management
6. **Time-Intensive**: Manual deduplication, ranking, and paper collection takes hours

### Target Users

- **Primary**: Graduate students and postdoctoral researchers conducting literature reviews
- **Secondary**: Faculty researchers, research librarians, and scientific writers
- **Tertiary**: Industry R&D professionals needing academic literature access

---

## Product Vision

Create a unified literature search platform that:
- Aggregates results from all major academic sources in one search
- Intelligently deduplicates and ranks results
- Provides ResearchRabbit-style discovery through citation networks
- Integrates institutional library access for paywall bypass
- Offers modern, responsive UI with professional aesthetics

---

## Goals and Success Metrics

### Goals

| Goal | Description | Priority |
|------|-------------|----------|
| **G1** | Enable single-query search across 7+ academic databases | P0 |
| **G2** | Eliminate duplicate papers through intelligent deduplication | P0 |
| **G3** | Provide citation-based discovery (citations, references, related) | P0 |
| **G4** | Support UCSB institutional library access for paywalled content | P1 |
| **G5** | Deliver modern, responsive UI with dark/light themes | P1 |
| **G6** | Enable paper organization through collections and tags | P2 |
| **G7** | Visualize research landscape through charts and networks | P2 |

### Success Metrics

| Metric | Target | Current Status |
|--------|--------|----------------|
| Search response time | < 5 seconds for 50 papers | ✅ Achieved (1-5s) |
| Deduplication accuracy | > 95% duplicate detection | ✅ Achieved |
| Sources integrated | 7 sources | ✅ Achieved |
| API endpoints | 30+ endpoints | ✅ Achieved (30+) |
| Test coverage | > 150 test cases | ✅ Achieved (190+) |

---

## Features

### Core Features (P0)

#### 1. Multi-Source Search
**Description**: Execute a single search query across multiple academic databases simultaneously

**Supported Sources**:
| Source | Type | Coverage | Rate Limit | Auth Required |
|--------|------|----------|------------|---------------|
| PubMed | Official API | 35M+ biomedical papers | 3/s | No |
| arXiv | Official API | 2M+ preprints | 1/s | No |
| Crossref | Official API | 150M+ DOI records | 2/s | No |
| Google Scholar | Web scraping | Citation database | 0.5/s | No |
| Web of Science | UCSB Proxy | Premium research DB | 0.5/s | Yes (UCSB) |
| Semantic Scholar | Official API | 200M+ papers | 2/s | No |
| OpenAlex | Official API | 250M+ works | 10/s | No |

**Acceptance Criteria**:
- [ ] User can select any combination of sources
- [ ] Searches execute in parallel (< 5 seconds)
- [ ] Results aggregate with source attribution
- [ ] Rate limiting prevents API bans
- [ ] Failed sources don't block other results

#### 2. Intelligent Deduplication
**Description**: Automatically identify and merge duplicate papers from different sources

**Deduplication Strategy**:
1. Exact DOI matching
2. Exact PMID matching
3. Exact arXiv ID matching
4. Title similarity matching (85% threshold)
5. Metadata merging from all sources

**Acceptance Criteria**:
- [ ] Same paper from multiple sources appears once
- [ ] Best metadata from all sources is preserved
- [ ] Source attribution shows all origins
- [ ] Title similarity uses fuzzy matching

#### 3. Smart Ranking Algorithm
**Description**: Rank search results by relevance, citations, recency, and source diversity

**Ranking Formula**:
```
Score = title_matches × 20
      + abstract_matches × 5
      + log10(citations) × 5
      + recency_bonus (0-20)
      + multi_source_bonus × 10
      + paper_type_bonus (15)
```

**Acceptance Criteria**:
- [ ] Most relevant papers appear first
- [ ] Recent papers receive recency boost
- [ ] Highly-cited papers score higher
- [ ] Papers found in multiple sources rank higher

#### 4. Paper Discovery (ResearchRabbit-style)
**Description**: Enable citation network exploration from any paper

**Discovery Features**:
| Feature | Data Source | Description |
|---------|-------------|-------------|
| Recommendations | Semantic Scholar | AI-powered similar papers |
| Citations | OpenAlex | Papers that cite this paper |
| References | OpenAlex | Papers this paper cites |
| Related | OpenAlex | Concept-similar papers |
| Network | OpenAlex | Visual citation graph |

**Acceptance Criteria**:
- [ ] Each paper has discovery tabs
- [ ] Recommendations use AI similarity
- [ ] Citation/reference counts displayed
- [ ] Network visualization is interactive
- [ ] Discovered papers can be saved to library

---

### Important Features (P1)

#### 5. UCSB Library Authentication
**Description**: Enable access to paywalled content through institutional proxy

**Implementation**:
- Cookie-based authentication (no credential storage)
- Session file persistence
- Automatic proxy URL construction
- Status indicator in UI

**Acceptance Criteria**:
- [ ] User can import browser cookies
- [ ] Auth status displays correctly
- [ ] Paywalled PDFs download through proxy
- [ ] Session persists across restarts
- [ ] Clear auth option available

#### 6. PDF Retrieval
**Description**: Download full-text PDFs using multiple strategies

**Retrieval Strategies** (in order):
1. UCSB Library proxy (if authenticated)
2. PubMed Central (if PMCID exists)
3. arXiv (direct PDF access)
4. Direct URL from paper metadata
5. Unpaywall open access API

**Acceptance Criteria**:
- [ ] Attempt all strategies in sequence
- [ ] Track download status per paper
- [ ] Store PDFs locally with consistent naming
- [ ] Extract text from downloaded PDFs
- [ ] Support batch downloads

#### 7. Modern Responsive UI
**Description**: Professional web interface with modern design patterns

**UI Features**:
- Glassmorphism design with subtle gradients
- Dark/light theme toggle with persistence
- Responsive layout (mobile, tablet, desktop)
- Loading skeletons for better UX
- Toast notifications for feedback
- Keyboard shortcuts (Ctrl+K for search)

**Acceptance Criteria**:
- [ ] Theme preference persists
- [ ] Mobile layout is usable
- [ ] Loading states prevent layout shift
- [ ] Actions provide immediate feedback
- [ ] Accessibility standards met

---

### Nice-to-Have Features (P2)

#### 8. Collections and Organization
**Description**: Organize papers into collections and apply tags

**Features**:
- Create/rename/delete collections
- Add/remove papers from collections
- Apply tags to papers
- Add notes to papers

**Acceptance Criteria**:
- [ ] Collections display paper counts
- [ ] Bulk operations supported
- [ ] Tags are searchable
- [ ] Notes support markdown

#### 9. Visualizations
**Description**: Visualize research landscape and trends

**Visualization Types**:
- Timeline chart (papers by year)
- Citation network graph
- Topic clustering

**Acceptance Criteria**:
- [ ] Charts render responsively
- [ ] Network is interactive (zoom/pan)
- [ ] Data updates in real-time

#### 10. Search History
**Description**: Track and replay previous searches

**Features**:
- Automatic search logging
- Click to replay search
- Filter history by date
- Clear history option

---

## Technical Requirements

### Architecture

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

### Technology Stack

**Backend**:
- Python 3.10+
- FastAPI (REST API framework)
- SQLAlchemy (ORM)
- SQLite (database)
- Pydantic (data validation)
- Requests (HTTP client)

**Frontend**:
- React 19.x
- Vite (build tool)
- React Router 7.x
- Axios (HTTP client)
- Recharts (charts)
- vis-network (graph visualization)

**External APIs**:
- NCBI E-utilities (PubMed)
- arXiv API
- Crossref REST API
- Semantic Scholar API
- OpenAlex API
- Unpaywall API

### Database Schema

**Core Tables**:
- `papers` - Main paper metadata (30+ fields)
- `authors` - Author records
- `paper_authors` - Many-to-many junction
- `collections` - User collections
- `collection_papers` - Many-to-many junction
- `pdf_content` - Extracted PDF text
- `search_history` - Query logs
- `tags` - Tag records
- `paper_tags` - Many-to-many junction
- `notes` - Paper annotations

### API Endpoints

**Total**: 30+ REST endpoints

**Categories**:
- Search (2 endpoints)
- Papers (8 endpoints)
- Downloads (2 endpoints)
- Collections (4 endpoints)
- Visualizations (3 endpoints)
- Discovery (5 endpoints)
- Authentication (3 endpoints)
- Statistics (1 endpoint)

### Performance Requirements

| Metric | Requirement |
|--------|-------------|
| Search latency | < 5 seconds for 50 papers |
| Deduplication | < 100ms for 200 papers |
| PDF download | < 5 seconds per paper |
| Page load | < 2 seconds |
| Memory usage | < 100MB backend |

### Security Requirements

- No credential storage (cookie-based auth only)
- CORS configured for localhost development
- Rate limiting on all external APIs
- Input validation via Pydantic
- SQL injection prevention via ORM

---

## User Stories

### Search

**US-1**: As a researcher, I want to search multiple databases at once so that I don't miss relevant papers.

**US-2**: As a researcher, I want duplicate papers merged automatically so that I don't waste time reviewing the same paper twice.

**US-3**: As a researcher, I want results ranked by relevance so that I find the most important papers first.

### Discovery

**US-4**: As a researcher, I want to see papers that cite a specific paper so that I can trace the research forward.

**US-5**: As a researcher, I want to see what papers a specific paper cites so that I can understand its foundations.

**US-6**: As a researcher, I want AI recommendations for similar papers so that I can discover related work.

### Downloads

**US-7**: As a UCSB researcher, I want to download paywalled PDFs through my library so that I can access full content.

**US-8**: As a researcher, I want to batch download multiple PDFs so that I can build my reading library quickly.

### Organization

**US-9**: As a researcher, I want to organize papers into collections so that I can manage different projects.

**US-10**: As a researcher, I want to add notes to papers so that I can remember key insights.

---

## Constraints and Assumptions

### Constraints

1. **Rate Limits**: Must respect API rate limits to avoid bans
2. **Google Scholar**: Web scraping is fragile and may break
3. **Institutional Access**: Only UCSB proxy currently supported
4. **No API Keys Required**: Core functionality works without paid APIs

### Assumptions

1. Users have Python 3.10+ and Node.js 16+ installed
2. Users have reliable internet connection
3. UCSB users have valid library credentials
4. SQLite sufficient for single-user workload

### Dependencies

- External APIs remain available and stable
- UCSB library proxy endpoints don't change
- No breaking changes in React 19 or FastAPI

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Google Scholar blocking | High | Medium | Implement user-agent rotation, rate limiting |
| API rate limit exceeded | Medium | Low | Token bucket algorithm, exponential backoff |
| UCSB proxy changes | Low | High | Monitor access, have fallback strategies |
| Data loss | Low | High | Database backups, transaction safety |

---

## Future Roadmap

### Phase 2 (Planned)

- [ ] AI-powered synthesis of search results
- [ ] Export to BibTeX/RIS/EndNote
- [ ] Browser extension for one-click saving
- [ ] Email alerts for saved searches
- [ ] Multi-user support with accounts
- [ ] PostgreSQL support for scalability

### Phase 3 (Exploration)

- [ ] Full-text search within downloaded PDFs
- [ ] Automated literature review generation
- [ ] Integration with reference managers (Zotero, Mendeley)
- [ ] Collaborative annotations
- [ ] Research trend analysis

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| DOI | Digital Object Identifier - unique paper identifier |
| PMID | PubMed Identifier |
| PMCID | PubMed Central Identifier |
| arXiv ID | arXiv preprint identifier |
| Deduplication | Process of merging duplicate records |
| Citation network | Graph of papers connected by citations |

### B. References

- [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [arXiv API](https://arxiv.org/help/api)
- [Crossref API](https://www.crossref.org/documentation/retrieve-metadata/)
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [OpenAlex API](https://docs.openalex.org/)

### C. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Nov 2024 | Development Team | Initial PRD |

---

*This document serves as the single source of truth for the Literature Search Application's product requirements and specifications.*
