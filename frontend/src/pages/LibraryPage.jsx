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
    <div className="library-page">
      <div className="page-header">
        <h1>📚 Paper Library</h1>
        <p>Browse and search your saved papers</p>
      </div>

      <div className="library-search">
        <form onSubmit={handleSearch} className="search-bar">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search in library..."
            className="search-input"
          />
          <button type="submit" className="search-btn">
            <FaSearch /> Search
          </button>
        </form>
      </div>

      {loading ? (
        <div className="loading">
          <FaSpinner className="spinner" size={48} />
          <p>Loading papers...</p>
        </div>
      ) : (
        <>
          <div className="library-stats">
            <p>
              Showing {papers.length} of {total} papers
            </p>
          </div>

          <div className="papers-grid">
            {papers.map((paper) => (
              <PaperCard key={paper.id} paper={paper} ucsbAuthenticated={ucsbAuthenticated} />
            ))}
          </div>

          {papers.length === 0 && (
            <div className="no-papers">
              <p>No papers in your library yet.</p>
              <p>Start by searching for papers!</p>
            </div>
          )}

          {total > 20 && (
            <div className="pagination">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="pagination-btn"
              >
                Previous
              </button>
              <span className="page-info">
                Page {page} of {Math.ceil(total / 20)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(total / 20)}
                className="pagination-btn"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default LibraryPage;
