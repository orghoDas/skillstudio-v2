import axios from 'axios';

// Use relative URL to leverage Next.js proxy in next.config.js
// This avoids CORS issues by proxying through the Next.js server
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Log API URL for debugging
if (typeof window !== 'undefined') {
  console.log('🔧 API Base URL:', API_URL);
}

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('📡 API Request:', config.method?.toUpperCase(), config.url);
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => {
    if (typeof window !== 'undefined') {
      console.log('✅ API Response:', response.config.method?.toUpperCase(), response.config.url, response.status);
    }
    return response;
  },
  (error) => {
    if (typeof window !== 'undefined') {
      console.error('❌ API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        hasResponse: !!error.response,
        hasRequest: !!error.request,
        message: error.message
      });
    }
    
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
