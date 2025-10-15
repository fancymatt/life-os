/**
 * Axios API Client with JWT Authentication
 *
 * This client automatically:
 * - Adds JWT tokens to all requests
 * - Refreshes expired tokens
 * - Redirects to login on authentication failure
 */

import axios from 'axios';

// API base URL - configurable via environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token storage helpers
const storage = {
  getAccessToken: () => localStorage.getItem('access_token'),
  getRefreshToken: () => localStorage.getItem('refresh_token'),
  setAccessToken: (token) => localStorage.setItem('access_token', token),
  setRefreshToken: (token) => localStorage.setItem('refresh_token', token),
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem('access_token', accessToken);
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
  },
  clearTokens: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// Request interceptor: Add JWT token to all requests
api.interceptors.request.use(
  (config) => {
    const token = storage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle token refresh on 401 errors
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is not 401 or request is already retried, reject immediately
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // If this is the login or refresh endpoint, don't retry
    if (originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/refresh')) {
      storage.clearTokens();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // If we're already refreshing, queue this request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        })
        .catch((err) => {
          return Promise.reject(err);
        });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = storage.getRefreshToken();

    // No refresh token available - redirect to login
    if (!refreshToken) {
      storage.clearTokens();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    try {
      // Attempt to refresh the token
      const response = await axios.post(
        `${API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const { access_token } = response.data;
      storage.setAccessToken(access_token);

      // Update the failed request with new token
      originalRequest.headers.Authorization = `Bearer ${access_token}`;

      // Process all queued requests
      processQueue(null, access_token);

      isRefreshing = false;

      // Retry the original request
      return api(originalRequest);
    } catch (refreshError) {
      // Refresh failed - clear tokens and redirect to login
      processQueue(refreshError, null);
      isRefreshing = false;
      storage.clearTokens();
      window.location.href = '/login';
      return Promise.reject(refreshError);
    }
  }
);

// Authentication API methods
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    const { access_token, refresh_token } = response.data;
    storage.setTokens(access_token, refresh_token);
    return response.data;
  },

  register: async (username, password, email) => {
    const response = await api.post('/auth/register', { username, password, email });
    return response.data;
  },

  logout: () => {
    storage.clearTokens();
    window.location.href = '/login';
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  isAuthenticated: () => {
    return !!storage.getAccessToken();
  },
};

// Export the configured axios instance and storage helpers
export { storage };
export default api;
