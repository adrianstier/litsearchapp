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
    <div className="space-y-8 max-w-7xl mx-auto animate-fade-in">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 dark:text-slate-50">
          📊 Visualizations
        </h1>
        <p className="text-base text-slate-600 dark:text-slate-400">
          Explore your research data
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200 dark:border-slate-700">
        <button
          className={`
            px-4 py-2 font-medium text-sm transition-colors duration-200
            border-b-2 -mb-px
            ${activeTab === 'timeline'
              ? 'border-primary-600 text-primary-700 dark:text-primary-400'
              : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600'
            }
          `}
          onClick={() => setActiveTab('timeline')}
        >
          Timeline
        </button>
        <button
          className={`
            px-4 py-2 font-medium text-sm transition-colors duration-200
            border-b-2 -mb-px
            ${activeTab === 'network'
              ? 'border-primary-600 text-primary-700 dark:text-primary-400'
              : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600'
            }
          `}
          onClick={() => setActiveTab('network')}
        >
          Network
        </button>
        <button
          className={`
            px-4 py-2 font-medium text-sm transition-colors duration-200
            border-b-2 -mb-px
            ${activeTab === 'topics'
              ? 'border-primary-600 text-primary-700 dark:text-primary-400'
              : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600'
            }
          `}
          onClick={() => setActiveTab('topics')}
        >
          Topics
        </button>
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-16 space-y-4">
          <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
          <p className="text-slate-600 dark:text-slate-400">Loading visualizations...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Timeline Tab */}
          {activeTab === 'timeline' && timelineData && (
            <div className="card space-y-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                Publication Timeline
              </h2>
              <div className="bg-slate-50 dark:bg-slate-900/50 rounded-lg p-4">
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={timelineData.data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" opacity={0.3} />
                    <XAxis
                      dataKey="year"
                      stroke="#64748b"
                      style={{ fontSize: '0.875rem' }}
                    />
                    <YAxis
                      stroke="#64748b"
                      style={{ fontSize: '0.875rem' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        border: '1px solid #e2e8f0',
                        borderRadius: '0.5rem',
                        padding: '0.75rem'
                      }}
                    />
                    <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 bg-primary-50 dark:bg-primary-950/30 px-4 py-3 rounded-lg">
                <span className="font-medium">Year range:</span>
                <span>{timelineData.year_range[0]} - {timelineData.year_range[1]}</span>
              </div>
            </div>
          )}

          {/* Network Tab */}
          {activeTab === 'network' && networkData && (
            <div className="card space-y-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                Citation Network
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-950/50 dark:to-primary-900/30 p-6 rounded-xl text-center">
                  <div className="text-4xl font-extrabold text-primary-700 dark:text-primary-400">
                    {networkData.nodes.length}
                  </div>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mt-2">
                    Papers (Nodes)
                  </p>
                </div>
                <div className="bg-gradient-to-br from-secondary-50 to-secondary-100 dark:from-secondary-950/50 dark:to-secondary-900/30 p-6 rounded-xl text-center">
                  <div className="text-4xl font-extrabold text-secondary-700 dark:text-secondary-400">
                    {networkData.links.length}
                  </div>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mt-2">
                    Connections (Links)
                  </p>
                </div>
              </div>
              <div className="bg-info-50 dark:bg-info-950/30 border-l-4 border-info-500 px-4 py-3 rounded-r-lg">
                <p className="text-sm text-slate-700 dark:text-slate-300">
                  Network visualization shows connections between papers based on shared authors
                  and citations.
                </p>
              </div>
            </div>
          )}

          {/* Topics Tab */}
          {activeTab === 'topics' && topicsData && (
            <div className="card space-y-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                Topic Clusters
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {topicsData.clusters.map((cluster) => (
                  <div
                    key={cluster.cluster_id}
                    className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl p-5 hover:shadow-md hover:border-primary-300 dark:hover:border-primary-700 transition-all duration-200"
                  >
                    <h3 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-2">
                      {cluster.label}
                    </h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                      {cluster.size} papers
                    </p>
                    {cluster.keywords.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {cluster.keywords.map((keyword, idx) => (
                          <span
                            key={idx}
                            className="badge bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300"
                          >
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
