import api from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

export const authService = {
  async login(credentials: LoginCredentials) {
    const response = await api.post('/auth/login', credentials);
    const { access_token, user } = response.data;
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
    }
    
    return { token: access_token, user };
  },

  async register(data: RegisterData) {
    const response = await api.post('/auth/register', data);
    const { access_token, user } = response.data;
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
    }
    
    return { token: access_token, user };
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
