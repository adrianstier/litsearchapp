import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { papersAPI, discoveryAPI } from '../services/api';
import { PaperGridSkeleton } from '../components/LoadingSkeleton';
import CitationNetwork from '../components/CitationNetwork';
import CitationNetworkD3 from '../components/CitationNetworkD3';
import AIFeaturesPanel from '../components/AIFeaturesPanel';
import '../styles/PaperDetailPage.css';

export default function PaperDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // Discovery data
  const [recommendations, setRecommendations] = useState([]);
  const [citations, setCitations] = useState([]);
  const [references, setReferences] = useState([]);
  const [relatedPapers, setRelatedPapers] = useState([]);
  const [network, setNetwork] = useState(null);

  // Loading states
  const [loadingDiscovery, setLoadingDiscovery] = useState({
    recommendations: false,
    citations: false,
    references: false,
    related: false,
    network: false
  });

  useEffect(() => {
    loadPaper();
  }, [id]);

  useEffect(() => {
    if (paper && activeTab !== 'overview') {
      loadDiscoveryData(activeTab);
    }
  }, [activeTab, paper]);

  const loadPaper = async () => {
    try {
      setLoading(true);
      const response = await papersAPI.getById(id);
      setPaper(response.data);
    } catch (error) {
      console.error('Failed to load paper:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDiscoveryData = async (tab) => {
    if (!paper) return;

    try {
      setLoadingDiscovery(prev => ({ ...prev, [tab]: true }));

      switch (tab) {
        case 'recommendations':
          if (recommendations.length === 0) {
            const res = await discoveryAPI.getRecommendations(id, 20);
            setRecommendations(res.data.recommendations || []);
          }
          break;
        case 'citations':
          if (citations.length === 0) {
            const res = await discoveryAPI.getCitations(id, 50);
            setCitations(res.data.citations || []);
          }
          break;
        case 'references':
          if (references.length === 0) {
            const res = await discoveryAPI.getReferences(id, 50);
            setReferences(res.data.references || []);
          }
          break;
        case 'related':
          if (relatedPapers.length === 0) {
            const res = await discoveryAPI.getRelated(id, 20);
            setRelatedPapers(res.data.related_papers || []);
          }
          break;
        case 'network':
          if (!network) {
            const res = await discoveryAPI.getNetwork(id, 1);
            setNetwork(res.data);
          }
          break;
      }
    } catch (error) {
      console.error(`Failed to load ${tab}:`, error);
    } finally {
      setLoadingDiscovery(prev => ({ ...prev, [tab]: false }));
    }
  };

  const formatAuthors = (authors) => {
    if (!authors || authors.length === 0) return 'Unknown';
    if (authors.length === 1) return authors[0].name;
    if (authors.length === 2) return `${authors[0].name} and ${authors[1].name}`;
    return `${authors[0].name} et al.`;
  };

  const renderPaperCard = (p) => (
    <div key={p.id} className="mini-paper-card" onClick={() => navigate(`/paper/${p.id}`)}>
      <div className="mini-paper-header">
        <h4>{p.title}</h4>
        {p.year && <span className="year-badge">{p.year}</span>}
      </div>
      <div className="mini-paper-authors">{formatAuthors(p.authors)}</div>
      {p.journal && <div className="mini-paper-journal">{p.journal}</div>}
      <div className="mini-paper-meta">
        {p.citations !== undefined && (
          <span className="meta-item">
            <span className="meta-icon">📊</span> {p.citations} citations
          </span>
        )}
        {p.sources && p.sources.length > 0 && (
          <span className="meta-item">
            <span className="meta-icon">🔗</span> {p.sources.join(', ')}
          </span>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="paper-detail-page">
        <PaperGridSkeleton count={3} />
      </div>
    );
  }

  if (!paper) {
    return (
      <div className="paper-detail-page">
        <div className="error-message">
          <h2>Paper Not Found</h2>
          <p>The paper you're looking for doesn't exist.</p>
          <button onClick={() => navigate('/')} className="btn btn-primary">
            Back to Search
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="paper-detail-page">
      {/* Header */}
      <div className="paper-detail-header">
        <button onClick={() => navigate(-1)} className="back-button">
          ← Back
        </button>
        <h1>{paper.title}</h1>
        <div className="paper-meta-info">
          <div className="authors">{formatAuthors(paper.authors)}</div>
          <div className="meta-row">
            {paper.year && <span className="meta-badge">📅 {paper.year}</span>}
            {paper.journal && <span className="meta-badge">📰 {paper.journal}</span>}
            {paper.citations !== undefined && (
              <span className="meta-badge">📊 {paper.citations} citations</span>
            )}
            {paper.doi && <span className="meta-badge">🔗 DOI: {paper.doi}</span>}
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <span className="tab-icon">📄</span> Overview
        </button>
        <button
          className={`tab-button ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          <span className="tab-icon">✨</span> Recommendations
          {recommendations.length > 0 && <span className="tab-count">{recommendations.length}</span>}
        </button>
        <button
          className={`tab-button ${activeTab === 'citations' ? 'active' : ''}`}
          onClick={() => setActiveTab('citations')}
        >
          <span className="tab-icon">⬆️</span> Cited By
          {citations.length > 0 && <span className="tab-count">{citations.length}</span>}
        </button>
        <button
          className={`tab-button ${activeTab === 'references' ? 'active' : ''}`}
          onClick={() => setActiveTab('references')}
        >
          <span className="tab-icon">⬇️</span> References
          {references.length > 0 && <span className="tab-count">{references.length}</span>}
        </button>
        <button
          className={`tab-button ${activeTab === 'related' ? 'active' : ''}`}
          onClick={() => setActiveTab('related')}
        >
          <span className="tab-icon">🔍</span> Related
          {relatedPapers.length > 0 && <span className="tab-count">{relatedPapers.length}</span>}
        </button>
        <button
          className={`tab-button ${activeTab === 'network' ? 'active' : ''}`}
          onClick={() => setActiveTab('network')}
        >
          <span className="tab-icon">🕸️</span> Citation Network
        </button>
        <button
          className={`tab-button ${activeTab === 'ai' ? 'active' : ''}`}
          onClick={() => setActiveTab('ai')}
        >
          <span className="tab-icon">🤖</span> AI Analysis
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="paper-section">
              <h3>Abstract</h3>
              <p className="abstract">
                {paper.abstract || 'No abstract available.'}
              </p>
            </div>

            {paper.keywords && paper.keywords.length > 0 && (
              <div className="paper-section">
                <h3>Keywords</h3>
                <div className="keywords">
                  {paper.keywords.map((kw, idx) => (
                    <span key={idx} className="keyword-tag">{kw}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="paper-section">
              <h3>Sources</h3>
              <div className="sources">
                {paper.sources && paper.sources.map((source, idx) => (
                  <span key={idx} className="source-badge">{source}</span>
                ))}
              </div>
            </div>

            {paper.pdf_url && (
              <div className="paper-section">
                <h3>PDF Access</h3>
                <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="btn btn-primary">
                  📄 Open PDF
                </a>
              </div>
            )}

            {paper.url && (
              <div className="paper-section">
                <h3>External Link</h3>
                <a href={paper.url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                  🔗 View on Publisher Site
                </a>
              </div>
            )}
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="discovery-tab">
            <div className="tab-header">
              <h2>✨ AI-Powered Recommendations</h2>
              <p>Papers recommended by Semantic Scholar's AI based on content similarity</p>
            </div>
            {loadingDiscovery.recommendations ? (
              <PaperGridSkeleton count={5} />
            ) : recommendations.length > 0 ? (
              <div className="paper-grid">
                {recommendations.map(renderPaperCard)}
              </div>
            ) : (
              <div className="empty-state">
                <p>No recommendations available for this paper.</p>
                <p className="hint">This paper may not be indexed in Semantic Scholar.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'citations' && (
          <div className="discovery-tab">
            <div className="tab-header">
              <h2>⬆️ Papers Citing This Work</h2>
              <p>Later works that reference this paper</p>
            </div>
            {loadingDiscovery.citations ? (
              <PaperGridSkeleton count={5} />
            ) : citations.length > 0 ? (
              <div className="paper-grid">
                {citations.map(renderPaperCard)}
              </div>
            ) : (
              <div className="empty-state">
                <p>No citations found for this paper.</p>
                <p className="hint">This paper may not have citations yet or may not be indexed in OpenAlex.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'references' && (
          <div className="discovery-tab">
            <div className="tab-header">
              <h2>⬇️ References</h2>
              <p>Earlier works cited by this paper</p>
            </div>
            {loadingDiscovery.references ? (
              <PaperGridSkeleton count={5} />
            ) : references.length > 0 ? (
              <div className="paper-grid">
                {references.map(renderPaperCard)}
              </div>
            ) : (
              <div className="empty-state">
                <p>No references found for this paper.</p>
                <p className="hint">This paper may not have references metadata or may not be indexed in OpenAlex.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'related' && (
          <div className="discovery-tab">
            <div className="tab-header">
              <h2>🔍 Related Papers</h2>
              <p>Papers with similar topics and concepts</p>
            </div>
            {loadingDiscovery.related ? (
              <PaperGridSkeleton count={5} />
            ) : relatedPapers.length > 0 ? (
              <div className="paper-grid">
                {relatedPapers.map(renderPaperCard)}
              </div>
            ) : (
              <div className="empty-state">
                <p>No related papers found.</p>
                <p className="hint">This paper may not have enough topic metadata.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'network' && (
          <div className="discovery-tab">
            <div className="tab-header">
              <h2>🕸️ Citation Network</h2>
              <p>Interactive visualization of citation relationships</p>
            </div>
            <CitationNetworkD3 paperId={parseInt(id)} width={800} height={500} />
            {loadingDiscovery.network ? (
              <PaperGridSkeleton count={3} />
            ) : network ? (
              <div className="network-details">
                <h3>Network Details</h3>
                <CitationNetwork data={network} />
              </div>
            ) : null}
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="discovery-tab">
            <div className="tab-header">
              <h2>🤖 AI-Powered Analysis</h2>
              <p>Use AI to summarize, extract data, and find similar papers</p>
            </div>
            <AIFeaturesPanel paper={paper} />
          </div>
        )}
      </div>
    </div>
  );
}
