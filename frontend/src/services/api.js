/**
 * API Client for Literature Search Backend
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Search API
export const searchAPI = {
  search: (query) => api.post('/search', query),
  getHistory: () => api.get('/search/history'),
};

// Papers API
export const papersAPI = {
  getAll: (page = 1, pageSize = 20) =>
    api.get(`/papers?page=${page}&page_size=${pageSize}`),
  getById: (id) => api.get(`/papers/${id}`),
  delete: (id) => api.delete(`/papers/${id}`),
  search: (query, limit = 20) =>
    api.get(`/papers/search?q=${encodeURIComponent(query)}&limit=${limit}`),
  getPDF: (id) => api.get(`/papers/${id}/pdf`, { responseType: 'blob' }),
  extractText: (id) => api.post(`/papers/${id}/extract-text`),
};

// Collections API
export const collectionsAPI = {
  getAll: () => api.get('/collections'),
  create: (collection) => api.post('/collections', collection),
  addPaper: (collectionId, paperId) =>
    api.post(`/collections/${collectionId}/papers/${paperId}`),
};

// Download API
export const downloadAPI = {
  downloadSingle: (paperId) => api.post(`/download/${paperId}`),
  downloadBatch: (paperIds) => api.post('/download/batch', { paper_ids: paperIds }),
};

// Visualization API
export const visualizationAPI = {
  getTimeline: (collectionId = null) => {
    const url = collectionId
      ? `/visualize/timeline?collection_id=${collectionId}`
      : '/visualize/timeline';
    return api.get(url);
  },
  getNetwork: (collectionId = null) => {
    const url = collectionId
      ? `/visualize/network?collection_id=${collectionId}`
      : '/visualize/network';
    return api.get(url);
  },
  getTopics: (collectionId = null) => {
    const url = collectionId
      ? `/visualize/topics?collection_id=${collectionId}`
      : '/visualize/topics';
    return api.get(url);
  },
};

// Auth API
export const authAPI = {
  getStatus: () => api.get('/auth/status'),
  importCookies: (formData) => api.post('/auth/import-cookies', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  clear: () => api.delete('/auth/clear'),
};

// Stats API
export const statsAPI = {
  get: () => api.get('/stats'),
};

// Discovery API (ResearchRabbit-style features)
export const discoveryAPI = {
  getRecommendations: (paperId, limit = 10) =>
    api.get(`/papers/${paperId}/recommendations?limit=${limit}`),
  getCitations: (paperId, limit = 50) =>
    api.get(`/papers/${paperId}/citations?limit=${limit}`),
  getReferences: (paperId, limit = 50) =>
    api.get(`/papers/${paperId}/references?limit=${limit}`),
  getRelated: (paperId, limit = 10) =>
    api.get(`/papers/${paperId}/related?limit=${limit}`),
  getNetwork: (paperId, depth = 1) =>
    api.get(`/papers/${paperId}/network?depth=${depth}`),
  getSimilar: (paperId, topK = 5) =>
    api.get(`/papers/${paperId}/similar?top_k=${topK}`),
};

// AI-Powered Features API
export const aiAPI = {
  // Generate summaries for papers
  summarize: (paperIds) =>
    api.post('/ai/summarize', paperIds),

  // Extract structured data from a paper
  extract: (paperId, fields) =>
    api.post('/ai/extract', null, {
      params: { paper_id: paperId, fields }
    }),

  // Extract custom column data
  customColumn: (paperIds, columnName, columnDescription) =>
    api.post('/ai/custom-column', null, {
      params: {
        paper_ids: paperIds,
        column_name: columnName,
        column_description: columnDescription
      }
    }),

  // Compare papers
  compare: (paperIds, aspect = 'findings') =>
    api.post('/ai/compare', null, {
      params: { paper_ids: paperIds, aspect }
    }),
};

// Semantic Search API
export const semanticAPI = {
  // Semantic search/reranking
  search: (query, paperIds = null, topK = 20) =>
    api.post('/search/semantic', null, {
      params: { query, paper_ids: paperIds, top_k: topK }
    }),
};

// Network Visualization API
export const networkAPI = {
  // Get D3.js formatted network
  getD3Network: (paperId) =>
    api.get(`/network/d3/${paperId}`),
};

export default api;
