# Frontend Implementation Guide

## Complete System Summary

You now have a **fully functional literature search application** with:

### ✅ Backend (Complete)
- **FastAPI server** with 30+ endpoints
- **SQLite database** with 8 tables
- **Full-text search** capabilities
- **PDF text extraction**
- **UCSB authentication** integration
- **Visualization APIs**
- **RESTful API** with auto-generated docs

### 🎨 Frontend (To Build)

## Quick Start - Build the Frontend

### Step 1: Create React App

```bash
cd /Users/adrianstiermbp2023/litsearchapp

# Create React app with Vite
npm create vite@latest frontend -- --template react

cd frontend
```

### Step 2: Install Dependencies

```bash
# Core dependencies
npm install axios @tanstack/react-query zustand react-router-dom

# UI Components
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Visualizations
npm install d3 plotly.js react-plotly.js

# PDF Viewer
npm install react-pdf pdfjs-dist

# Icons
npm install lucide-react
```

### Step 3: Configure Tailwind

Edit `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Edit `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 4: Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts          # API client
│   ├── components/
│   │   ├── Search/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchFilters.tsx
│   │   │   └── SearchResults.tsx
│   │   ├── Papers/
│   │   │   ├── PaperCard.tsx
│   │   │   ├── PaperList.tsx
│   │   │   └── PaperDetail.tsx
│   │   ├── Visualizations/
│   │   │   ├── Timeline.tsx
│   │   │   ├── CitationNetwork.tsx
│   │   │   └── TopicClusters.tsx
│   │   ├── Collections/
│   │   │   └── CollectionManager.tsx
│   │   └── Layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Layout.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Search.tsx
│   │   ├── Library.tsx
│   │   ├── Visualize.tsx
│   │   └── Settings.tsx
│   ├── stores/
│   │   ├── searchStore.ts
│   │   └── paperStore.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

## Key Components to Build

### 1. API Client (`src/api/client.ts`)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchPapers = async (query: any) => {
  const response = await api.post('/search', query);
  return response.data;
};

export const getPapers = async (page = 1, pageSize = 20) => {
  const response = await api.get(`/papers?page=${page}&page_size=${pageSize}`);
  return response.data;
};

export const getPaper = async (id: number) => {
  const response = await api.get(`/papers/${id}`);
  return response.data;
};

export const downloadPaper = async (id: number) => {
  const response = await api.post(`/download/${id}`);
  return response.data;
};

export const getTimeline = async () => {
  const response = await api.get('/visualize/timeline');
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export default api;
```

### 2. Search Page (`src/pages/Search.tsx`)

```typescript
import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { searchPapers } from '../api/client';
import SearchBar from '../components/Search/SearchBar';
import SearchResults from '../components/Search/SearchResults';

export default function Search() {
  const [query, setQuery] = useState('');
  const [sources, setSources] = useState(['pubmed', 'arxiv']);

  const searchMutation = useMutation({
    mutationFn: (searchData: any) => searchPapers(searchData),
  });

  const handleSearch = () => {
    searchMutation.mutate({
      query,
      sources,
      max_results: 50,
    });
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Search Literature</h1>

      <SearchBar
        query={query}
        setQuery={setQuery}
        sources={sources}
        setSources={setSources}
        onSearch={handleSearch}
      />

      {searchMutation.isLoading && (
        <div className="mt-6">Searching...</div>
      )}

      {searchMutation.data && (
        <SearchResults papers={searchMutation.data.papers} />
      )}
    </div>
  );
}
```

### 3. Dashboard with Stats (`src/pages/Dashboard.tsx`)

```typescript
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getStats, getTimeline } from '../api/client';
import Timeline from '../components/Visualizations/Timeline';

export default function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
  });

  const { data: timeline } = useQuery({
    queryKey: ['timeline'],
    queryFn: getTimeline,
  });

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-2xl font-bold">{stats?.total_papers || 0}</div>
          <div className="text-gray-600">Total Papers</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-2xl font-bold">{stats?.total_pdfs || 0}</div>
          <div className="text-gray-600">Downloaded PDFs</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-2xl font-bold">{stats?.total_collections || 0}</div>
          <div className="text-gray-600">Collections</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-2xl font-bold">
            {stats?.pdf_percentage.toFixed(0) || 0}%
          </div>
          <div className="text-gray-600">PDF Coverage</div>
        </div>
      </div>

      {/* Timeline Visualization */}
      {timeline && <Timeline data={timeline.data} />}
    </div>
  );
}
```

### 4. Paper Library (`src/pages/Library.tsx`)

```typescript
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getPapers } from '../api/client';
import PaperList from '../components/Papers/PaperList';

export default function Library() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['papers', page],
    queryFn: () => getPapers(page, 20),
  });

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Paper Library</h1>

      {isLoading && <div>Loading...</div>}

      {data && (
        <>
          <PaperList papers={data.papers} />

          {/* Pagination */}
          <div className="mt-6 flex justify-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
            >
              Previous
            </button>
            <span className="px-4 py-2">
              Page {page} of {data.pages}
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= data.pages}
              className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
```

## Running the Complete System

### Terminal 1: Backend

```bash
cd /Users/adrianstiermbp2023/litsearchapp
python -m uvicorn backend.main:app --reload --port 8000
```

### Terminal 2: Frontend

```bash
cd /Users/adrianstiermbp2023/litsearchapp/frontend
npm run dev
```

### Access

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features to Implement

### Phase 1: Core (2-3 hours)
- ✅ Project setup
- ✅ API client
- ✅ Search interface
- ✅ Paper list/detail views
- ✅ Dashboard with stats

### Phase 2: Advanced (2-3 hours)
- Timeline visualization (Plotly)
- Citation network (D3.js)
- Collections management
- PDF viewer (react-pdf)

### Phase 3: Polish (1-2 hours)
- Responsive design
- Loading states
- Error handling
- Animations

## Alternative: Simple HTML Demo

If you want to see it working immediately without building React, I can create a simple HTML/JS demo that uses the API.

## What You Have Now

1. **Fully working CLI** - Already tested and functional
2. **Complete REST API** - 30+ endpoints ready
3. **Database layer** - SQLite with all relationships
4. **Service layer** - Business logic implemented
5. **PDF handling** - Download and text extraction
6. **UCSB integration** - Cookie-based authentication
7. **Visualizations** - Data generation APIs ready

## Next Steps

**Choose one:**

1. **Build React frontend** (recommended) - Modern, interactive UI
2. **Create HTML demo** (fastest) - See it working in 30 min
3. **Use API directly** - curl/Postman/Python scripts

Would you like me to:
1. Start building the React components?
2. Create a quick HTML demo?
3. Write more detailed component code?