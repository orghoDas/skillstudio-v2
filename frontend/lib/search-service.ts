import api from './api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface SearchFilters {
  query?: string;
  category?: string;
  level?: 'beginner' | 'intermediate' | 'advanced';
  min_price?: number;
  max_price?: number;
  min_rating?: number;
  min_duration?: number;
  max_duration?: number;
  is_free?: boolean;
  is_certified?: boolean;
  instructor_id?: string;
  sort_by?: 'relevance' | 'popular' | 'rating' | 'newest' | 'price_low' | 'price_high';
  limit?: number;
  offset?: number;
}

export interface SearchResult<T> {
  courses?: T[];
  instructors?: T[];
  suggestions?: T[];
  categories?: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface SearchSuggestion {
  type: string;
  title: string;
  id: string;
}

export interface CategoryCount {
  name: string;
  course_count: number;
}

// API Functions

export async function searchCourses(filters: SearchFilters): Promise<SearchResult<any>> {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value.toString());
    }
  });
  
  const response = await fetch(`${API_BASE_URL}/api/search/courses?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to search courses');
  }
  return response.json();
}

export async function searchInstructors(query?: string, minRating?: number, limit: number = 20, offset: number = 0): Promise<SearchResult<any>> {
  const params = new URLSearchParams();
  
  if (query) params.append('query', query);
  if (minRating !== undefined) params.append('min_rating', minRating.toString());
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());
  
  const response = await fetch(`${API_BASE_URL}/api/search/instructors?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to search instructors');
  }
  return response.json();
}

export async function getSearchSuggestions(query: string, limit: number = 5): Promise<{ suggestions: SearchSuggestion[] }> {
  const params = new URLSearchParams();
  params.append('query', query);
  params.append('limit', limit.toString());
  
  const response = await fetch(`${API_BASE_URL}/api/search/suggestions?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to get search suggestions');
  }
  return response.json();
}

export async function getPopularCategories(limit: number = 10): Promise<{ categories: CategoryCount[] }> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  
  const response = await fetch(`${API_BASE_URL}/api/search/categories?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to get categories');
  }
  return response.json();
}
