import { useState, useEffect, useRef } from 'react';
import { FaSearch, FaSpinner, FaTimes } from 'react-icons/fa';
import { searchAPI, authAPI } from '../services/api';
import PaperCard from '../components/PaperCard';
import { PaperGridSkeleton } from '../components/LoadingSkeleton';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import { useToast } from '../components/Toast';

function SearchPage({ onStatsUpdate }) {
  const [query, setQuery] = useState('');
  const [sources, setSources] = useState(['pubmed', 'arxiv', 'crossref', 'scholar', 'wos']);
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
    <div className="space-y-8 max-w-7xl mx-auto animate-fade-in">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 dark:text-slate-50">
          🔍 Search Literature
        </h1>
        <p className="text-base md:text-lg text-slate-600 dark:text-slate-400">
          Search across PubMed, arXiv, Crossref, Google Scholar, and Web of Science
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="space-y-6">
        {/* Search Input */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <input
              ref={searchInputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter search query (Press / or Ctrl+K to focus)"
              className="input pr-10"
              aria-label="Search query"
            />
            {query && (
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                onClick={clearSearch}
                aria-label="Clear search"
                title="Clear search (Esc)"
              >
                <FaTimes className="w-4 h-4" />
              </button>
            )}
          </div>
          <button
            type="submit"
            className="btn-primary flex items-center justify-center gap-2 sm:w-auto w-full"
            disabled={loading || !query.trim()}
          >
            {loading ? (
              <>
                <FaSpinner className="w-4 h-4 animate-spin" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <FaSearch className="w-4 h-4" />
                <span>Search</span>
              </>
            )}
          </button>
        </div>

        {/* Search History */}
        {searchHistory.length > 0 && !query && (
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
              Recent searches:
            </p>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((historyQuery, index) => (
                <button
                  key={index}
                  type="button"
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 transition-colors"
                  onClick={() => setQuery(historyQuery)}
                >
                  <FaSearch className="w-3 h-3" />
                  <span>{historyQuery}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="card space-y-6">
          {/* Sources */}
          <div className="space-y-3">
            <label className="block text-sm font-semibold text-slate-900 dark:text-slate-50">
              Sources:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={sources.includes('pubmed')}
                  onChange={() => toggleSource('pubmed')}
                  className="w-5 h-5 rounded border-2 border-slate-300 dark:border-slate-600 text-primary-600 focus:ring-4 focus:ring-primary-200 dark:focus:ring-primary-800 transition-all"
                />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  PubMed
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={sources.includes('arxiv')}
                  onChange={() => toggleSource('arxiv')}
                  className="w-5 h-5 rounded border-2 border-slate-300 dark:border-slate-600 text-primary-600 focus:ring-4 focus:ring-primary-200 dark:focus:ring-primary-800 transition-all"
                />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  arXiv
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={sources.includes('crossref')}
                  onChange={() => toggleSource('crossref')}
                  className="w-5 h-5 rounded border-2 border-slate-300 dark:border-slate-600 text-primary-600 focus:ring-4 focus:ring-primary-200 dark:focus:ring-primary-800 transition-all"
                />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  Crossref
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={sources.includes('scholar')}
                  onChange={() => toggleSource('scholar')}
                  className="w-5 h-5 rounded border-2 border-slate-300 dark:border-slate-600 text-primary-600 focus:ring-4 focus:ring-primary-200 dark:focus:ring-primary-800 transition-all"
                />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  Google Scholar
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={sources.includes('wos')}
                  onChange={() => toggleSource('wos')}
                  className="w-5 h-5 rounded border-2 border-slate-300 dark:border-slate-600 text-primary-600 focus:ring-4 focus:ring-primary-200 dark:focus:ring-primary-800 transition-all"
                />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  Web of Science
                  {!ucsbAuthenticated && (
                    <span className="text-warning-600 dark:text-warning-400 ml-1">*</span>
                  )}
                </span>
              </label>
            </div>
            {!ucsbAuthenticated && (
              <p className="text-xs text-warning-600 dark:text-warning-400">
                * Web of Science requires UCSB authentication (configure in Settings)
              </p>
            )}
          </div>

          {/* Other Filters */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Max Results */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-slate-900 dark:text-slate-50">
                Max Results:
              </label>
              <select
                value={maxResults}
                onChange={(e) => setMaxResults(Number(e.target.value))}
                className="input"
              >
                <option value={10}>10 results</option>
                <option value={20}>20 results</option>
                <option value={50}>50 results</option>
                <option value={100}>100 results</option>
              </select>
            </div>

            {/* Year Range */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-slate-900 dark:text-slate-50">
                Year Range:
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  placeholder="From"
                  value={yearStart}
                  onChange={(e) => setYearStart(e.target.value)}
                  className="input flex-1"
                  min="1900"
                  max={new Date().getFullYear()}
                />
                <span className="text-slate-400 dark:text-slate-600">—</span>
                <input
                  type="number"
                  placeholder="To"
                  value={yearEnd}
                  onChange={(e) => setYearEnd(e.target.value)}
                  className="input flex-1"
                  min="1900"
                  max={new Date().getFullYear()}
                />
              </div>
            </div>
          </div>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="flex items-start gap-3 p-4 rounded-lg bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 text-error-900 dark:text-error-100">
          <span className="font-semibold">Error:</span>
          <span>{error}</span>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <PaperGridSkeleton count={6} />
      )}

      {/* Search Results */}
      {!loading && results && (
        <div className="space-y-6">
          {/* Results Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
              Found {results.total_found} papers in {results.search_time.toFixed(2)}s
            </h2>
            <div className="flex flex-wrap gap-2">
              {Object.entries(results.statistics).map(([source, count]) => (
                <span
                  key={source}
                  className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${
                    source === 'pubmed' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
                    source === 'arxiv' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300' :
                    source === 'crossref' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300' :
                    source === 'scholar' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                    'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300'
                  }`}
                >
                  {source}: {count}
                </span>
              ))}
            </div>
          </div>

          {/* Papers Grid */}
          {results.papers && results.papers.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {results.papers.map((paper) => (
                <PaperCard key={paper.id} paper={paper} ucsbAuthenticated={ucsbAuthenticated} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 card">
              <p className="text-lg text-slate-600 dark:text-slate-400">
                No papers found. Try adjusting your search terms or filters.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!results && !loading && (
        <div className="text-center py-16 space-y-6 card">
          <div className="flex justify-center">
            <FaSearch className="w-16 h-16 text-slate-300 dark:text-slate-700" />
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              Ready to search academic literature
            </h3>
            <p className="text-base text-slate-600 dark:text-slate-400">
              Enter a search query to find papers across multiple databases
            </p>
          </div>
          <div className="max-w-md mx-auto text-left space-y-3">
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              Example queries:
            </p>
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <li className="flex items-start gap-2">
                <span className="text-primary-500 mt-0.5">•</span>
                <span>CRISPR gene editing</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-500 mt-0.5">•</span>
                <span>machine learning healthcare</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-500 mt-0.5">•</span>
                <span>climate change adaptation</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-500 mt-0.5">•</span>
                <span>quantum computing algorithms</span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchPage;
