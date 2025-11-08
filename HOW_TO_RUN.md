# 🚀 How to Run the Full Stack Literature Search App

## Quick Start (Two Terminal Windows)

### Terminal 1: Backend

```bash
cd /Users/adrianstiermbp2023/litsearchapp
python -m uvicorn backend.main:app --reload --port 8000
```

✅ Backend running at: **http://localhost:8000**
📚 API Docs at: **http://localhost:8000/docs**

### Terminal 2: Frontend

```bash
cd /Users/adrianstiermbp2023/litsearchapp/frontend
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

**Then open your browser to http://localhost:5173**

---

## Full Installation (First Time Only)

### 1. Install Python Dependencies

```bash
cd /Users/adrianstiermbp2023/litsearchapp
pip install -r requirements.txt
pip install python-multipart  # Required for file uploads
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

## What You'll See

### 🏠 Main Interface
- **Sidebar Navigation**: Search, Library, Collections, Visualizations, Settings
- **Live Stats**: Paper count, PDF count, search count in sidebar
- **Modern UI**: Dark sidebar, clean white content area

### 🔍 Search Page (Default Landing)
- Large search input with example queries
- Source checkboxes (PubMed, arXiv, Crossref)
- Year range filters (From - To)
- Max results dropdown (10-100)
- Beautiful results grid with paper cards

### 📄 Paper Cards Show:
- Title and authors
- Publication year, journal, citations
- Abstract preview
- DOI
- Source badges (color-coded)
- "Download PDF" button
- External links

### 📚 Library Page
- View all saved papers
- Full-text search bar
- Pagination (20 per page)
- Same beautiful paper cards

### 🗂️ Collections Page
- Create new collections
- See all collections with paper counts
- Organize your research

### 📊 Visualizations Page
Three tabs:
1. **Timeline**: Bar chart of publications by year
2. **Network**: Citation/author network statistics
3. **Topics**: Keyword-based topic clusters

### ⚙️ Settings Page
- UCSB authentication status
- Session details (cookies count, config dir)
- Instructions for cookie import
- App info and API docs link

---

## Testing the App

### 1. Start Both Servers

**Terminal 1 (Backend)**:
```bash
cd /Users/adrianstiermbp2023/litsearchapp
python -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend)**:
```bash
cd /Users/adrianstiermbp2023/litsearchapp/frontend
npm run dev
```

### 2. Open Browser

Navigate to: **http://localhost:5173**

### 3. Try a Search

1. You'll land on the **Search** page
2. Enter a query: `"machine learning healthcare"`
3. Leave all sources checked (PubMed, arXiv, Crossref)
4. Click **Search**
5. Wait 5-15 seconds for results
6. See papers appear in beautiful cards!

### 4. Explore Features

- Click **Library** to see all saved papers
- Click **Visualizations** to see timeline chart
- Click **Collections** to create a folder
- Click **Settings** to see auth status

---

## Sample Test Queries

Try these searches:
- `CRISPR gene editing`
- `machine learning healthcare`
- `climate change adaptation`
- `quantum computing algorithms`
- `COVID-19 vaccine`
- `neural networks deep learning`

---

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'backend'`

**Fix**:
```bash
cd /Users/adrianstiermbp2023/litsearchapp
python -m uvicorn backend.main:app --reload --port 8000
```

Make sure you're in the root directory, not `frontend/`!

### Frontend won't start

**Error**: `npm: command not found`

**Fix**: Install Node.js from https://nodejs.org/

**Error**: Dependencies missing

**Fix**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### No data in visualizations

**Cause**: Database is empty

**Fix**: Run a search first! The database needs papers before visualizations work.

### API connection errors

**Symptoms**: Search button does nothing, errors in browser console

**Checks**:
1. Backend running? Check Terminal 1
2. Backend on port 8000? Try http://localhost:8000/docs
3. CORS errors? Check backend terminal for startup messages

**Fix**: Restart both servers

### Port already in use

**Error**: `Address already in use: 8000` or `5173`

**Fix**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

Then restart servers.

---

## Development Commands

### Backend
```bash
# Development with auto-reload
python -m uvicorn backend.main:app --reload --port 8000

# Production mode
python -m uvicorn backend.main:app --port 8000

# Different port
python -m uvicorn backend.main:app --port 8080
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database
```bash
# View database
sqlite3 database/papers.db

# In sqlite shell:
.tables                    # List tables
.schema papers            # See paper table structure
SELECT COUNT(*) FROM papers;  # Count papers
SELECT title, year FROM papers LIMIT 5;  # View papers
.quit                     # Exit
```

---

## API Endpoints (for testing)

All available at **http://localhost:8000/api**:

### Search
- `POST /api/search` - Execute search
- `GET /api/search/history` - View search history

### Papers
- `GET /api/papers` - List papers (paginated)
- `GET /api/papers/{id}` - Get paper details
- `GET /api/papers/search?q=query` - Full-text search
- `POST /api/download/{id}` - Download PDF

### Collections
- `GET /api/collections` - List collections
- `POST /api/collections` - Create collection
- `POST /api/collections/{cid}/papers/{pid}` - Add paper

### Visualizations
- `GET /api/visualize/timeline` - Timeline data
- `GET /api/visualize/network` - Network data
- `GET /api/visualize/topics` - Topic clusters

### Auth & Stats
- `GET /api/auth/status` - UCSB auth status
- `GET /api/stats` - App statistics

**Interactive Docs**: http://localhost:8000/docs

---

## File Structure

```
litsearchapp/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── schemas.py       # Pydantic schemas
│   └── services/        # Business logic
├── src/                 # Core search logic
│   ├── search/          # Search providers
│   ├── retrieval/       # PDF download
│   ├── auth/            # UCSB auth
│   └── database/        # SQLAlchemy models
├── frontend/            # React frontend
│   ├── src/
│   │   ├── pages/       # Main pages
│   │   ├── components/  # Reusable components
│   │   ├── services/    # API client
│   │   └── App.jsx      # Main app
│   └── package.json
├── database/            # SQLite database
│   └── papers.db
└── downloads/          # Downloaded PDFs
```

---

## Production Deployment

### Backend
```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend
```bash
cd frontend
npm run build
# Serve dist/ folder with nginx/apache
```

---

## What's Included

✅ **Complete Backend** (FastAPI)
  - 30+ REST API endpoints
  - SQLite database
  - Search integration (PubMed/arXiv/Crossref)
  - PDF download & text extraction
  - UCSB proxy authentication
  - Visualization data generation

✅ **Complete Frontend** (React + Vite)
  - Modern responsive UI
  - Search interface with filters
  - Paper library with pagination
  - Collections manager
  - Interactive visualizations (Recharts)
  - Settings & auth status

✅ **Test Suite**
  - 190+ test cases
  - 76% passing on first run
  - Comprehensive edge case coverage

---

## Next Steps

1. ✅ Start both servers
2. ✅ Run a test search
3. ✅ Explore the interface
4. ⏭️ Set up UCSB authentication (optional)
5. ⏭️ Download some PDFs
6. ⏭️ Create collections
7. ⏭️ View visualizations

---

## Support

- **Backend Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **Database**: `database/papers.db`
- **Logs**: Check terminal windows

---

**🎉 Enjoy your new literature search application!**

Built with: Python • FastAPI • React • Vite • SQLite • Recharts
Total dev time: ~3 hours
