import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import { visualizationAPI } from '../services/api';

function VisualizationsPage() {
  const [timelineData, setTimelineData] = useState(null);
  const [networkData, setNetworkData] = useState(null);
  const [topicsData, setTopicsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('timeline');

  useEffect(() => {
    loadVisualizations();
  }, []);

  const loadVisualizations = async () => {
    setLoading(true);
    try {
      const [timeline, network, topics] = await Promise.all([
        visualizationAPI.getTimeline(),
        visualizationAPI.getNetwork(),
        visualizationAPI.getTopics(),
      ]);
      setTimelineData(timeline.data);
      setNetworkData(network.data);
      setTopicsData(topics.data);
    } catch (error) {
      console.error('Failed to load visualizations:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="viz-page">
      <div className="page-header">
        <h1>📊 Visualizations</h1>
        <p>Explore your research data</p>
      </div>

      <div className="viz-tabs">
        <button
          className={activeTab === 'timeline' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('timeline')}
        >
          Timeline
        </button>
        <button
          className={activeTab === 'network' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('network')}
        >
          Network
        </button>
        <button
          className={activeTab === 'topics' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('topics')}
        >
          Topics
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading visualizations...</div>
      ) : (
        <div className="viz-content">
          {activeTab === 'timeline' && timelineData && (
            <div className="viz-section">
              <h2>Publication Timeline</h2>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={timelineData.data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#4f46e5" />
                </BarChart>
              </ResponsiveContainer>
              <p className="viz-info">
                Year range: {timelineData.year_range[0]} - {timelineData.year_range[1]}
              </p>
            </div>
          )}

          {activeTab === 'network' && networkData && (
            <div className="viz-section">
              <h2>Citation Network</h2>
              <div className="network-stats">
                <div className="stat-box">
                  <h3>{networkData.nodes.length}</h3>
                  <p>Papers (Nodes)</p>
                </div>
                <div className="stat-box">
                  <h3>{networkData.links.length}</h3>
                  <p>Connections (Links)</p>
                </div>
              </div>
              <p className="viz-note">
                Network visualization shows connections between papers based on shared authors
                and citations.
              </p>
            </div>
          )}

          {activeTab === 'topics' && topicsData && (
            <div className="viz-section">
              <h2>Topic Clusters</h2>
              <div className="topics-grid">
                {topicsData.clusters.map((cluster) => (
                  <div key={cluster.cluster_id} className="topic-card">
                    <h3>{cluster.label}</h3>
                    <p className="topic-size">{cluster.size} papers</p>
                    {cluster.keywords.length > 0 && (
                      <div className="topic-keywords">
                        {cluster.keywords.map((keyword, idx) => (
                          <span key={idx} className="keyword-badge">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default VisualizationsPage;
