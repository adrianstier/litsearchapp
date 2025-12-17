/**
 * AI Features Panel Component
 * Provides AI-powered paper analysis features
 */

import React, { useState } from 'react';
import { aiAPI, discoveryAPI } from '../services/api';
import './AIFeaturesPanel.css';

export function AIFeaturesPanel({ paper, onClose }) {
  const [activeTab, setActiveTab] = useState('summary');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Summary
  const [summary, setSummary] = useState(null);

  // Extraction
  const [extractFields, setExtractFields] = useState(['methodology', 'sample_size', 'main_finding']);
  const [extractedData, setExtractedData] = useState(null);

  // Similar papers
  const [similarPapers, setSimilarPapers] = useState(null);

  const generateSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiAPI.summarize([paper.id]);
      if (response.data.summaries && response.data.summaries.length > 0) {
        setSummary(response.data.summaries[0].summary);
      }
    } catch (err) {
      setError('Failed to generate summary. Make sure OPENAI_API_KEY is set.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const extractData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiAPI.extract(paper.id, extractFields);
      setExtractedData(response.data.extracted);
    } catch (err) {
      setError('Failed to extract data. Make sure OPENAI_API_KEY is set.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const findSimilar = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await discoveryAPI.getSimilar(paper.id, 5);
      setSimilarPapers(response.data.similar);
    } catch (err) {
      setError('Failed to find similar papers.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleField = (field) => {
    if (extractFields.includes(field)) {
      setExtractFields(extractFields.filter(f => f !== field));
    } else {
      setExtractFields([...extractFields, field]);
    }
  };

  const availableFields = [
    'methodology',
    'sample_size',
    'population',
    'intervention',
    'outcomes',
    'main_finding',
    'effect_size',
    'limitations',
    'p_value',
    'duration',
    'setting'
  ];

  return (
    <div className="ai-features-panel">
      <div className="ai-panel-header">
        <h3>AI Analysis</h3>
        {onClose && (
          <button className="close-button" onClick={onClose}>×</button>
        )}
      </div>

      <div className="ai-tabs">
        <button
          className={`ai-tab ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
        <button
          className={`ai-tab ${activeTab === 'extract' ? 'active' : ''}`}
          onClick={() => setActiveTab('extract')}
        >
          Extract Data
        </button>
        <button
          className={`ai-tab ${activeTab === 'similar' ? 'active' : ''}`}
          onClick={() => setActiveTab('similar')}
        >
          Similar Papers
        </button>
      </div>

      {error && (
        <div className="ai-error">
          {error}
        </div>
      )}

      <div className="ai-content">
        {activeTab === 'summary' && (
          <div className="ai-section">
            <p className="section-description">
              Generate a concise AI summary of this paper's key findings and methodology.
            </p>

            {summary ? (
              <div className="ai-result summary-result">
                <h4>Summary</h4>
                <p>{summary}</p>
              </div>
            ) : (
              <button
                className="ai-action-button"
                onClick={generateSummary}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Summary'}
              </button>
            )}
          </div>
        )}

        {activeTab === 'extract' && (
          <div className="ai-section">
            <p className="section-description">
              Extract structured data from this paper. Select the fields you want to extract.
            </p>

            <div className="field-selector">
              {availableFields.map(field => (
                <label key={field} className="field-checkbox">
                  <input
                    type="checkbox"
                    checked={extractFields.includes(field)}
                    onChange={() => toggleField(field)}
                  />
                  <span>{field.replace(/_/g, ' ')}</span>
                </label>
              ))}
            </div>

            {extractedData ? (
              <div className="ai-result extraction-result">
                <h4>Extracted Data</h4>
                <table className="extraction-table">
                  <tbody>
                    {Object.entries(extractedData).map(([key, value]) => (
                      <tr key={key}>
                        <td className="field-name">{key.replace(/_/g, ' ')}</td>
                        <td className="field-value">
                          {Array.isArray(value) ? value.join(', ') : (value || 'Not found')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <button
                className="ai-action-button"
                onClick={extractData}
                disabled={loading || extractFields.length === 0}
              >
                {loading ? 'Extracting...' : 'Extract Data'}
              </button>
            )}
          </div>
        )}

        {activeTab === 'similar' && (
          <div className="ai-section">
            <p className="section-description">
              Find papers with similar content using semantic similarity.
            </p>

            {similarPapers ? (
              <div className="ai-result similar-result">
                <h4>Similar Papers</h4>
                <ul className="similar-papers-list">
                  {similarPapers.map(p => (
                    <li key={p.paper_id}>
                      <div className="similar-paper">
                        <span className="paper-title">{p.title}</span>
                        <span className="similarity-score">
                          {(p.similarity_score * 100).toFixed(1)}% match
                        </span>
                      </div>
                      {p.year && <span className="paper-year">{p.year}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <button
                className="ai-action-button"
                onClick={findSimilar}
                disabled={loading}
              >
                {loading ? 'Finding...' : 'Find Similar Papers'}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AIFeaturesPanel;
