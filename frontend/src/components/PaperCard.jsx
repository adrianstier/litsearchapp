import { useState, useRef } from 'react';
import {
  FaFileAlt, FaDownload, FaExternalLinkAlt, FaQuoteLeft,
  FaCheckCircle, FaSpinner, FaBookmark, FaRegBookmark,
  FaShareAlt, FaCopy, FaChevronDown, FaChevronUp, FaEllipsisV
} from 'react-icons/fa';
import { downloadAPI } from '../services/api';
import { useClickOutside } from '../hooks/useKeyboardShortcuts';
import { useToast } from './Toast';

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
    <div className="card-hover border-l-4 border-l-primary-500 group">
      {/* Header */}
      <div className="space-y-3">
        {/* Title and Actions */}
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-50 leading-tight flex-1">
            {paper.title}
          </h3>

          {/* Quick Actions Menu */}
          <div className="relative flex-shrink-0" ref={quickActionsRef}>
            <button
              className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              onClick={() => setShowQuickActions(!showQuickActions)}
              aria-label="Quick actions"
              title="Quick actions"
            >
              <FaEllipsisV className="w-4 h-4" />
            </button>

            {showQuickActions && (
              <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 py-1 z-10 animate-scale-in">
                <button
                  onClick={handleBookmark}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                >
                  {isBookmarked ? <FaBookmark className="w-4 h-4" /> : <FaRegBookmark className="w-4 h-4" />}
                  <span>{isBookmarked ? 'Remove Bookmark' : 'Bookmark'}</span>
                </button>
                <button
                  onClick={handleCopyCitation}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                >
                  <FaCopy className="w-4 h-4" />
                  <span>Copy Citation</span>
                </button>
                <button
                  onClick={handleShare}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                >
                  <FaShareAlt className="w-4 h-4" />
                  <span>Share</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Source Badges */}
        {paper.sources && paper.sources.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {paper.sources.map((source) => (
              <span
                key={source}
                className={`
                  inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wide
                  ${source === 'pubmed' ? 'badge-pubmed' : ''}
                  ${source === 'arxiv' ? 'badge-arxiv' : ''}
                  ${source === 'crossref' ? 'badge-crossref' : ''}
                  ${source === 'scholar' ? 'badge-scholar' : ''}
                  ${source === 'wos' ? 'badge-wos' : ''}
                `}
              >
                {source}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Authors */}
      <div className="text-sm text-slate-600 dark:text-slate-400">
        {paper.authors && paper.authors.length > 0 ? (
          <span>
            {paper.authors.slice(0, 3).map(a => a.name).join(', ')}
            {paper.authors.length > 3 && (
              <span className="text-slate-500 dark:text-slate-500"> +{paper.authors.length - 3} more</span>
            )}
          </span>
        ) : (
          <span className="italic text-slate-400 dark:text-slate-600">No authors listed</span>
        )}
      </div>

      {/* Abstract */}
      {paper.abstract && (
        <div className="space-y-2">
          <div className="flex items-start gap-2">
            <FaQuoteLeft className="w-3 h-3 text-slate-400 dark:text-slate-600 flex-shrink-0 mt-1" />
            <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              {showFullAbstract
                ? paper.abstract
                : `${paper.abstract.substring(0, 200)}${paper.abstract.length > 200 ? '...' : ''}`
              }
            </p>
          </div>
          {paper.abstract.length > 200 && (
            <button
              className="inline-flex items-center gap-1.5 text-xs font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
              onClick={() => setShowFullAbstract(!showFullAbstract)}
              aria-label={showFullAbstract ? 'Show less' : 'Show more'}
            >
              <span>{showFullAbstract ? 'Show less' : 'Show more'}</span>
              {showFullAbstract ? (
                <FaChevronUp className="w-3 h-3" />
              ) : (
                <FaChevronDown className="w-3 h-3" />
              )}
            </button>
          )}
        </div>
      )}

      {/* Metadata */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600 dark:text-slate-400">
        {paper.year && (
          <span className="flex items-center gap-1.5">
            <span>📅</span>
            <span>{paper.year}</span>
          </span>
        )}
        {paper.journal && (
          <span className="flex items-center gap-1.5">
            <span>📰</span>
            <span className="line-clamp-1">{paper.journal}</span>
          </span>
        )}
        {paper.citations !== undefined && (
          <span className="flex items-center gap-1.5">
            <span>📊</span>
            <span>{paper.citations} citations</span>
          </span>
        )}
      </div>

      {/* DOI */}
      {paper.doi && (
        <div className="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-900 rounded-lg">
          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">DOI:</span>
          <span className="text-xs text-slate-600 dark:text-slate-400 flex-1 truncate font-mono">
            {paper.doi}
          </span>
          <button
            className="p-1.5 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
            onClick={handleCopyDOI}
            aria-label="Copy DOI"
            title="Copy DOI to clipboard"
          >
            <FaCopy className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* Download Status */}
      {downloadStatus && (
        <div className={`
          flex items-center gap-2 p-3 rounded-lg text-sm
          ${downloadStatus.type === 'success'
            ? 'bg-success-50 dark:bg-success-900/20 text-success-900 dark:text-success-100 border border-success-200 dark:border-success-800'
            : 'bg-error-50 dark:bg-error-900/20 text-error-900 dark:text-error-100 border border-error-200 dark:border-error-800'
          }
        `}>
          {downloadStatus.type === 'success' && <FaCheckCircle className="w-4 h-4 flex-shrink-0" />}
          <span>{downloadStatus.message}</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-2">
        <button
          onClick={handleDownload}
          className={`
            flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all
            ${ucsbAuthenticated
              ? 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white shadow-sm hover:shadow-md'
              : 'btn-primary'
            }
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
          disabled={downloading}
          title={ucsbAuthenticated ? 'Download with UCSB access' : 'Download PDF'}
        >
          {downloading ? (
            <>
              <FaSpinner className="w-4 h-4 animate-spin" />
              <span>Downloading...</span>
            </>
          ) : (
            <>
              <FaDownload className="w-4 h-4" />
              <span>{ucsbAuthenticated ? 'Download (UCSB)' : 'Download PDF'}</span>
            </>
          )}
        </button>

        {paper.url && (
          <a
            href={paper.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary flex items-center justify-center gap-2 px-4 py-2.5"
          >
            <FaExternalLinkAlt className="w-3 h-3" />
            <span className="hidden sm:inline">View Online</span>
          </a>
        )}

        {paper.pdf_url && (
          <a
            href={paper.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost flex items-center justify-center gap-2 px-4 py-2.5"
          >
            <FaFileAlt className="w-4 h-4" />
            <span className="hidden sm:inline">Direct PDF</span>
          </a>
        )}
      </div>

      {/* UCSB Access Notice */}
      {ucsbAuthenticated && (
        <div className="flex items-center gap-2 p-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
          <span className="text-xl">✨</span>
          <p className="text-xs text-primary-900 dark:text-primary-100 font-medium">
            UCSB institutional access enabled - Higher success rate for paywalled papers
          </p>
        </div>
      )}
    </div>
  );
}

export default PaperCard;
