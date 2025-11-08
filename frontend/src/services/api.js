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

export default api;
