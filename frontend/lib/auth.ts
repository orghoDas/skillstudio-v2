import api from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  role?: 'learner' | 'instructor' | 'admin';
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

// Helper to extract error message from API response
function getErrorMessage(error: any): string {
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    // Handle validation errors (array of objects)
    if (Array.isArray(detail)) {
      return detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
    }
    // Handle simple string errors
    if (typeof detail === 'string') {
      return detail;
    }
    // Handle object errors
    return JSON.stringify(detail);
  }
  return error.message || 'An unexpected error occurred';
}

export const authService = {
  async login(credentials: LoginCredentials) {
    try {
      const response = await api.post('/auth/login', credentials);
      const { access_token, user } = response.data;
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
      }
      
      return { token: access_token, user };
    } catch (error: any) {
      throw new Error(getErrorMessage(error));
    }
  },

  async register(data: RegisterData) {
    try {
      const response = await api.post('/auth/register', data);
      const { access_token, user } = response.data;
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
      }
      
      return { token: access_token, user };
    } catch (error: any) {
      throw new Error(getErrorMessage(error));
    }
  },

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
  },

  getCurrentUser(): User | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  },

  isAuthenticated(): boolean {
    if (typeof window !== 'undefined') {
      return !!localStorage.getItem('token');
    }
    return false;
  },
};
