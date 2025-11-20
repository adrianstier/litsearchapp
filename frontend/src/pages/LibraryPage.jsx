import { useState, useEffect } from 'react';
import { FaSearch, FaSpinner } from 'react-icons/fa';
import { papersAPI, authAPI } from '../services/api';
import PaperCard from '../components/PaperCard';

function LibraryPage() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [ucsbAuthenticated, setUcsbAuthenticated] = useState(false);

  useEffect(() => {
    loadPapers();
    checkUcsbAuth();
  }, [page]);

  const checkUcsbAuth = async () => {
    try {
      const response = await authAPI.getStatus();
      setUcsbAuthenticated(response.data.authenticated);
    } catch (error) {
      console.error('Failed to check UCSB auth:', error);
    }
  };

  const loadPapers = async () => {
    setLoading(true);
    try {
      const response = await papersAPI.getAll(page, 20);
      setPapers(response.data.papers);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Failed to load papers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadPapers();
      return;
    }

    setLoading(true);
    try {
      const response = await papersAPI.search(searchQuery);
      setPapers(response.data);
      setTotal(response.data.length);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-fade-in">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 dark:text-slate-50">
          📚 Paper Library
        </h1>
        <p className="text-base text-slate-600 dark:text-slate-400">
          Browse and search your saved papers
        </p>
      </div>

      {/* Search Bar */}
      <div className="card">
        <form onSubmit={handleSearch} className="flex gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search in library..."
            className="input flex-1"
            aria-label="Search in library"
          />
          <button type="submit" className="btn-primary flex items-center gap-2">
            <FaSearch />
            <span>Search</span>
          </button>
        </form>
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-16 space-y-4">
          <FaSpinner className="w-12 h-12 text-primary-600 animate-spin" />
          <p className="text-slate-600 dark:text-slate-400">Loading papers...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Stats */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Showing <span className="font-semibold text-slate-900 dark:text-slate-50">{papers.length}</span> of{' '}
              <span className="font-semibold text-slate-900 dark:text-slate-50">{total}</span> papers
            </p>
          </div>

          {/* Papers Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {papers.map((paper) => (
              <PaperCard key={paper.id} paper={paper} ucsbAuthenticated={ucsbAuthenticated} />
            ))}
          </div>

          {/* Empty State */}
          {papers.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 space-y-4 text-center">
              <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center text-3xl">
                📚
              </div>
              <div className="space-y-1">
                <p className="text-lg font-semibold text-slate-900 dark:text-slate-50">
                  No papers in your library yet
                </p>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Start by searching for papers!
                </p>
              </div>
            </div>
          )}

          {/* Pagination */}
          {total > 20 && (
            <div className="flex items-center justify-center gap-4 pt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-sm text-slate-700 dark:text-slate-300 font-medium">
                Page {page} of {Math.ceil(total / 20)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(total / 20)}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default LibraryPage;
