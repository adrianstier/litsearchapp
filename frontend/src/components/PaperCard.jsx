import { useState, useRef } from 'react';
import {
  FaFileAlt, FaDownload, FaExternalLinkAlt, FaQuoteLeft,
  FaCheckCircle, FaSpinner, FaBookmark, FaRegBookmark,
  FaShareAlt, FaCopy, FaChevronDown, FaChevronUp, FaEllipsisV
} from 'react-icons/fa';
import { downloadAPI } from '../services/api';
import { useClickOutside } from '../hooks/useKeyboardShortcuts';
import { useToast } from './Toast';
import './PaperCard.css';

function PaperCard({ paper, ucsbAuthenticated }) {
  const [downloading, setDownloading] = useState(false);
  const [downloadStatus, setDownloadStatus] = useState(null);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [showFullAbstract, setShowFullAbstract] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(false);
  const quickActionsRef = useRef(null);
  const toast = useToast();

  useClickOutside(quickActionsRef, () => setShowQuickActions(false));

  const handleDownload = async () => {
    setDownloading(true);
    setDownloadStatus(null);
    try {
      const response = await downloadAPI.downloadSingle(paper.id);
      if (response.data.success) {
        setDownloadStatus({ type: 'success', message: 'PDF downloaded successfully!' });
        toast.success('PDF downloaded successfully!');
      } else {
        setDownloadStatus({ type: 'error', message: response.data.error || 'Download failed' });
        toast.error(response.data.error || 'Download failed');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Download failed';
      setDownloadStatus({ type: 'error', message: errorMessage });
      toast.error(errorMessage);
    } finally {
      setDownloading(false);
    }
  };

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
    toast.success(isBookmarked ? 'Removed from bookmarks' : 'Added to bookmarks');
  };

  const handleCopyCitation = () => {
    const authors = paper.authors?.slice(0, 3).map(a => a.name).join(', ') || 'Unknown';
    const citation = `${authors}${paper.authors?.length > 3 ? ' et al.' : ''}. ${paper.title}. ${paper.journal || 'Journal'}${paper.year ? `, ${paper.year}` : ''}.${paper.doi ? ` DOI: ${paper.doi}` : ''}`;

    navigator.clipboard.writeText(citation).then(() => {
      toast.success('Citation copied to clipboard');
      setShowQuickActions(false);
    }).catch(() => {
      toast.error('Failed to copy citation');
    });
  };

  const handleShare = () => {
    if (navigator.share && paper.url) {
      navigator.share({
        title: paper.title,
        text: paper.abstract?.substring(0, 200) || '',
        url: paper.url,
      }).catch(() => {
        toast.info('Sharing cancelled');
      });
    } else {
      // Fallback: copy link to clipboard
      if (paper.url) {
        navigator.clipboard.writeText(paper.url).then(() => {
          toast.success('Link copied to clipboard');
        });
      } else {
        toast.warning('No URL available to share');
      }
    }
    setShowQuickActions(false);
  };

  const handleCopyDOI = () => {
    if (paper.doi) {
      navigator.clipboard.writeText(paper.doi).then(() => {
        toast.success('DOI copied to clipboard');
      }).catch(() => {
        toast.error('Failed to copy DOI');
      });
    }
  };

  return (
    <div className="paper-card">
      <div className="paper-header">
        <div className="paper-title-row">
          <h3 className="paper-title">{paper.title}</h3>
          <div className="paper-quick-actions" ref={quickActionsRef}>
            <button
              className="quick-action-toggle"
              onClick={() => setShowQuickActions(!showQuickActions)}
              aria-label="Quick actions"
              title="Quick actions"
            >
              <FaEllipsisV />
            </button>
            {showQuickActions && (
              <div className="quick-actions-menu">
                <button onClick={handleBookmark} className="quick-action-item">
                  {isBookmarked ? <FaBookmark /> : <FaRegBookmark />}
                  {isBookmarked ? 'Remove Bookmark' : 'Bookmark'}
                </button>
                <button onClick={handleCopyCitation} className="quick-action-item">
                  <FaCopy /> Copy Citation
                </button>
                <button onClick={handleShare} className="quick-action-item">
                  <FaShareAlt /> Share
                </button>
              </div>
            )}
          </div>
        </div>
        <div className="paper-sources">
          {paper.sources && paper.sources.map((source) => (
            <span key={source} className={`source-badge ${source}`}>
              {source}
            </span>
          ))}
        </div>
      </div>

      <div className="paper-authors">
        {paper.authors && paper.authors.length > 0 ? (
          <span>
            {paper.authors.slice(0, 3).map(a => a.name).join(', ')}
            {paper.authors.length > 3 && ` +${paper.authors.length - 3} more`}
          </span>
        ) : (
          <span className="no-authors">No authors listed</span>
        )}
      </div>

      {paper.abstract && (
        <div className="paper-abstract">
          <FaQuoteLeft size={12} />
          <p>
            {showFullAbstract
              ? paper.abstract
              : `${paper.abstract.substring(0, 200)}${paper.abstract.length > 200 ? '...' : ''}`
            }
          </p>
          {paper.abstract.length > 200 && (
            <button
              className="abstract-toggle"
              onClick={() => setShowFullAbstract(!showFullAbstract)}
              aria-label={showFullAbstract ? 'Show less' : 'Show more'}
            >
              {showFullAbstract ? (
                <>Show less <FaChevronUp /></>
              ) : (
                <>Show more <FaChevronDown /></>
              )}
            </button>
          )}
        </div>
      )}

      <div className="paper-meta">
        {paper.year && <span>📅 {paper.year}</span>}
        {paper.journal && <span>📰 {paper.journal}</span>}
        {paper.citations !== undefined && <span>📊 {paper.citations} citations</span>}
      </div>

      {paper.doi && (
        <div className="paper-doi">
          <strong>DOI:</strong>
          <span className="doi-text">{paper.doi}</span>
          <button
            className="doi-copy-btn"
            onClick={handleCopyDOI}
            aria-label="Copy DOI"
            title="Copy DOI to clipboard"
          >
            <FaCopy />
          </button>
        </div>
      )}

      {downloadStatus && (
        <div className={`download-status ${downloadStatus.type}`}>
          {downloadStatus.type === 'success' ? <FaCheckCircle /> : null}
          <span>{downloadStatus.message}</span>
        </div>
      )}

      <div className="paper-actions">
        <button
          onClick={handleDownload}
          className={`btn-download ${downloading ? 'downloading' : ''} ${ucsbAuthenticated ? 'ucsb-enabled' : ''}`}
          disabled={downloading}
          title={ucsbAuthenticated ? 'Download with UCSB access' : 'Download PDF'}
        >
          {downloading ? (
            <>
              <FaSpinner className="spinner" /> Downloading...
            </>
          ) : (
            <>
              <FaDownload /> {ucsbAuthenticated ? 'Download (UCSB)' : 'Download PDF'}
            </>
          )}
        </button>
        {paper.url && (
          <a href={paper.url} target="_blank" rel="noopener noreferrer" className="btn-external">
            <FaExternalLinkAlt /> View Online
          </a>
        )}
        {paper.pdf_url && (
          <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="btn-pdf">
            <FaFileAlt /> Direct PDF
          </a>
        )}
      </div>

      {ucsbAuthenticated && (
        <div className="ucsb-access-notice">
          ✨ UCSB institutional access enabled - Higher success rate for paywalled papers
        </div>
      )}
    </div>
  );
}

export default PaperCard;
