import { useState, useEffect, useRef } from 'react';
import { FaSearch, FaSpinner, FaTimes } from 'react-icons/fa';
import { searchAPI, authAPI } from '../services/api';
import PaperCard from '../components/PaperCard';
import { PaperGridSkeleton } from '../components/LoadingSkeleton';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import { useToast } from '../components/Toast';
import './SearchPage.css';

function SearchPage({ onStatsUpdate }) {
  const [query, setQuery] = useState('');
  const [sources, setSources] = useState(['pubmed', 'arxiv', 'crossref', 'semantic_scholar', 'openalex']);
  const [maxResults, setMaxResults] = useState(20);
  const [yearStart, setYearStart] = useState('');
  const [yearEnd, setYearEnd] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [ucsbAuthenticated, setUcsbAuthenticated] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);
  const searchInputRef = useRef(null);
  const toast = useToast();

  // Keyboard shortcuts
  useKeyboardShortcuts({
    '/': () => searchInputRef.current?.focus(),
    'ctrl+k': () => searchInputRef.current?.focus(),
    'Escape': () => {
      if (query) {
        setQuery('');
        searchInputRef.current?.blur();
      }
    },
  });

  useEffect(() => {
    checkUcsbAuth();
    loadSearchHistory();
  }, []);

  const checkUcsbAuth = async () => {
    try {
      const response = await authAPI.getStatus();
      setUcsbAuthenticated(response.data.authenticated);
    } catch (error) {
      console.error('Failed to check UCSB auth:', error);
    }
  };

  const loadSearchHistory = () => {
    try {
      const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
      setSearchHistory(history.slice(0, 5)); // Keep last 5 searches
    } catch (error) {
      console.error('Failed to load search history:', error);
    }
  };

  const saveToSearchHistory = (searchQuery) => {
    try {
      const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
      const updated = [searchQuery, ...history.filter(q => q !== searchQuery)].slice(0, 10);
      localStorage.setItem('searchHistory', JSON.stringify(updated));
      setSearchHistory(updated.slice(0, 5));
    } catch (error) {
      console.error('Failed to save search history:', error);
    }
  };

  const clearSearch = () => {
    setQuery('');
    setResults(null);
    setError(null);
    searchInputRef.current?.focus();
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const searchParams = {
        query: query.trim(),
        sources,
        max_results: maxResults,
      };

      if (yearStart) searchParams.year_start = parseInt(yearStart);
      if (yearEnd) searchParams.year_end = parseInt(yearEnd);

      const response = await searchAPI.search(searchParams);
      setResults(response.data);
      saveToSearchHistory(query.trim());

      if (response.data.total_found > 0) {
        toast.success(`Found ${response.data.total_found} papers in ${response.data.search_time.toFixed(2)}s`);
      } else {
        toast.info('No papers found. Try different search terms or filters.');
      }

      if (onStatsUpdate) onStatsUpdate();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Search failed. Please try again.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const toggleSource = (source) => {
    setSources((prev) =>
      prev.includes(source) ? prev.filter((s) => s !== source) : [...prev, source]
    );
  };

  return (
    <div className="search-page">
      <div className="search-header">
        <h1>Search Literature</h1>
        <p>Search across 400M+ papers from multiple sources</p>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <div className="search-input-wrapper">
            <input
              ref={searchInputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter search query (Press / or Ctrl+K to focus)"
              className="search-input"
              aria-label="Search query"
            />
            {query && (
              <button
                type="button"
                className="clear-search-btn"
                onClick={clearSearch}
                aria-label="Clear search"
                title="Clear search (Esc)"
              >
                <FaTimes />
              </button>
            )}
          </div>
          <button type="submit" className="search-button" disabled={loading || !query.trim()}>
            {loading ? <FaSpinner className="spinner" /> : <FaSearch />}
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {searchHistory.length > 0 && !query && (
          <div className="search-history">
            <p className="search-history-label">Recent searches:</p>
            <div className="search-history-items">
              {searchHistory.map((historyQuery, index) => (
                <button
                  key={index}
                  type="button"
                  className="search-history-item"
                  onClick={() => setQuery(historyQuery)}
                >
                  <FaSearch /> {historyQuery}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="search-filters">
          <div className="filter-group">
            <label className="filter-label">Sources:</label>
            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes('pubmed')}
                  onChange={() => toggleSource('pubmed')}
                />
                <span>PubMed</span>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes('arxiv')}
                  onChange={() => toggleSource('arxiv')}
                />
                <span>arXiv</span>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes('crossref')}
                  onChange={() => toggleSource('crossref')}
                />
                <span>Crossref</span>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes('semantic_scholar')}
                  onChange={() => toggleSource('semantic_scholar')}
                />
                <span>Semantic Scholar <span className="new-badge">AI</span></span>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes('openalex')}
                  onChange={() => toggleSource('openalex')}
                />
                <span>OpenAlex <span className="new-badge">250M</span></span>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes('scholar')}
                  onChange={() => toggleSource('scholar')}
                />
                <span>Google Scholar <span className="warning-badge">Limited</span></span>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes('wos')}
                  onChange={() => toggleSource('wos')}
                />
                <span>Web of Science {!ucsbAuthenticated && <span className="ucsb-required">*</span>}</span>
              </label>
            </div>
            {!ucsbAuthenticated && (
              <p className="ucsb-note">
                * Web of Science requires UCSB authentication
              </p>
            )}
          </div>

          <div className="filter-group">
            <label className="filter-label">Max Results:</label>
            <select value={maxResults} onChange={(e) => setMaxResults(Number(e.target.value))} className="form-select">
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Year Range:</label>
            <div className="year-range">
              <input
                type="number"
                placeholder="From"
                value={yearStart}
                onChange={(e) => setYearStart(e.target.value)}
                className="year-input"
              />
              <span className="year-separator">-</span>
              <input
                type="number"
                placeholder="To"
                value={yearEnd}
                onChange={(e) => setYearEnd(e.target.value)}
                className="year-input"
              />
            </div>
          </div>
        </div>
      </form>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && (
        <PaperGridSkeleton count={6} />
      )}

      {!loading && results && (
        <div className="search-results">
          <div className="results-header">
            <h2>
              Found {results.total_found} papers in {results.search_time.toFixed(2)}s
            </h2>
            <div className="results-stats">
              {Object.entries(results.statistics).map(([source, count]) => (
                <span key={source} className="stat-badge">
                  {source}: {count}
                </span>
              ))}
            </div>
          </div>

          {results.papers && results.papers.length > 0 ? (
            <div className="papers-grid">
              {results.papers.map((paper) => (
                <PaperCard key={paper.id} paper={paper} ucsbAuthenticated={ucsbAuthenticated} />
              ))}
            </div>
          ) : (
            <div className="no-results">
              <p>No papers found. Try adjusting your search terms or filters.</p>
            </div>
          )}
        </div>
      )}

      {!results && !loading && (
        <div className="search-placeholder">
          <FaSearch size={64} color="#ccc" />
          <p>Enter a search query to find academic papers</p>
          <div className="example-queries">
            <p><strong>Example queries:</strong></p>
            <ul>
              <li>CRISPR gene editing</li>
              <li>machine learning healthcare</li>
              <li>climate change adaptation</li>
              <li>quantum computing algorithms</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchPage;
