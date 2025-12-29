/**
 * Form validation utilities for Literature Search Application
 */

// Validation result type
const createResult = (isValid, error = null) => ({ isValid, error });

/**
 * Validate search query
 */
export const validateSearchQuery = (query) => {
  if (!query || typeof query !== 'string') {
    return createResult(false, 'Search query is required');
  }

  const trimmed = query.trim();

  if (trimmed.length === 0) {
    return createResult(false, 'Search query cannot be empty');
  }

  if (trimmed.length < 2) {
    return createResult(false, 'Search query must be at least 2 characters');
  }

  if (trimmed.length > 500) {
    return createResult(false, 'Search query must be less than 500 characters');
  }

  return createResult(true);
};

/**
 * Validate year input
 */
export const validateYear = (year, fieldName = 'Year') => {
  if (!year && year !== 0) {
    return createResult(true); // Empty is valid (optional)
  }

  const numYear = parseInt(year, 10);

  if (isNaN(numYear)) {
    return createResult(false, `${fieldName} must be a number`);
  }

  const currentYear = new Date().getFullYear();

  if (numYear < 1800) {
    return createResult(false, `${fieldName} must be after 1800`);
  }

  if (numYear > currentYear + 1) {
    return createResult(false, `${fieldName} cannot be in the future`);
  }

  return createResult(true);
};

/**
 * Validate year range
 */
export const validateYearRange = (yearStart, yearEnd) => {
  const startResult = validateYear(yearStart, 'Start year');
  if (!startResult.isValid) return startResult;

  const endResult = validateYear(yearEnd, 'End year');
  if (!endResult.isValid) return endResult;

  if (yearStart && yearEnd) {
    const start = parseInt(yearStart, 10);
    const end = parseInt(yearEnd, 10);

    if (start > end) {
      return createResult(false, 'Start year must be before end year');
    }
  }

  return createResult(true);
};

/**
 * Validate sources selection
 */
export const validateSources = (sources) => {
  if (!Array.isArray(sources)) {
    return createResult(false, 'Invalid sources selection');
  }

  if (sources.length === 0) {
    return createResult(false, 'Please select at least one source');
  }

  const validSources = [
    'pubmed', 'arxiv', 'crossref', 'scholar',
    'wos', 'semantic_scholar', 'openalex'
  ];

  const invalidSources = sources.filter(s => !validSources.includes(s));
  if (invalidSources.length > 0) {
    return createResult(false, `Invalid source(s): ${invalidSources.join(', ')}`);
  }

  return createResult(true);
};

/**
 * Validate collection name
 */
export const validateCollectionName = (name) => {
  if (!name || typeof name !== 'string') {
    return createResult(false, 'Collection name is required');
  }

  const trimmed = name.trim();

  if (trimmed.length === 0) {
    return createResult(false, 'Collection name cannot be empty');
  }

  if (trimmed.length > 100) {
    return createResult(false, 'Collection name must be less than 100 characters');
  }

  return createResult(true);
};

/**
 * Validate email format
 */
export const validateEmail = (email) => {
  if (!email || typeof email !== 'string') {
    return createResult(false, 'Email is required');
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailRegex.test(email)) {
    return createResult(false, 'Invalid email format');
  }

  return createResult(true);
};

/**
 * Validate search form data
 */
export const validateSearchForm = (formData) => {
  const errors = {};

  // Validate query
  const queryResult = validateSearchQuery(formData.query);
  if (!queryResult.isValid) {
    errors.query = queryResult.error;
  }

  // Validate sources
  const sourcesResult = validateSources(formData.sources);
  if (!sourcesResult.isValid) {
    errors.sources = sourcesResult.error;
  }

  // Validate year range
  const yearRangeResult = validateYearRange(formData.yearStart, formData.yearEnd);
  if (!yearRangeResult.isValid) {
    errors.yearRange = yearRangeResult.error;
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

export default {
  validateSearchQuery,
  validateYear,
  validateYearRange,
  validateSources,
  validateCollectionName,
  validateEmail,
  validateSearchForm
};
