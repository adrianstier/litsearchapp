/**
 * API Client for Literature Search Backend
 */

import axios from 'axios';

// Use environment variable or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout for long searches
});

// Request interceptor for logging and request handling
api.interceptors.request.use(
  (config) => {
    // Add timestamp for request tracking
    config.metadata = { startTime: new Date() };
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    // Log response time in development
    if (import.meta.env.DEV && response.config.metadata) {
      const duration = new Date() - response.config.metadata.startTime;
      console.debug(`API ${response.config.method?.toUpperCase()} ${response.config.url}: ${duration}ms`);
    }
    return response;
  },
  (error) => {
    // Handle different error types
    const errorResponse = {
      message: 'An unexpected error occurred',
      status: null,
      data: null,
    };

    if (error.response) {
      // Server responded with error status
      errorResponse.status = error.response.status;
      errorResponse.data = error.response.data;

      switch (error.response.status) {
        case 400:
          errorResponse.message = error.response.data?.detail || 'Invalid request';
          break;
        case 401:
          errorResponse.message = 'Authentication required';
          break;
        case 403:
          errorResponse.message = 'Access denied';
          break;
        case 404:
          errorResponse.message = error.response.data?.detail || 'Resource not found';
          break;
        case 422:
          errorResponse.message = error.response.data?.detail || 'Validation error';
          break;
        case 429:
          errorResponse.message = 'Too many requests. Please slow down.';
          break;
        case 500:
          errorResponse.message = error.response.data?.detail || 'Server error. Please try again later.';
          break;
        case 502:
        case 503:
        case 504:
          errorResponse.message = 'Service temporarily unavailable. Please try again later.';
          break;
        default:
          errorResponse.message = error.response.data?.detail || `Error: ${error.response.status}`;
      }
    } else if (error.request) {
      // Request was made but no response received
      if (error.code === 'ECONNABORTED') {
        errorResponse.message = 'Request timed out. Please try again.';
      } else {
        errorResponse.message = 'Unable to connect to server. Please check your connection.';
      }
    } else {
      // Error in request configuration
      errorResponse.message = error.message || 'Request configuration error';
    }

    // Log error in development
    if (import.meta.env.DEV) {
      console.error('API Error:', errorResponse);
    }

    // Attach our custom error response to the error object
    error.errorResponse = errorResponse;
    return Promise.reject(error);
  }
);

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
