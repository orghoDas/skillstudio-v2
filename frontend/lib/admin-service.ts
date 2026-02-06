import api from './api';

export interface PlatformStats {
  users: {
    total: number;
    learners: number;
    instructors: number;
  };
  courses: {
    total: number;
    published: number;
    draft: number;
  };
  enrollments: {
    total: number;
  };
  revenue: {
    total: number;
    this_month: number;
    pending_payouts: number;
  };
}

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: 'LEARNER' | 'INSTRUCTOR' | 'ADMIN';
  is_active: boolean;
  email_verified: boolean;
  created_at: string | null;
  last_login: string | null;
}

export interface UsersResponse {
  users: AdminUser[];
  total: number;
  limit: number;
  offset: number;
}

export interface AdminCourse {
  id: string;
  title: string;
  instructor_id: string;
  is_published: boolean;
  is_certified: boolean;
  enrollment_count: number;
  average_rating: number | null;
  created_at: string | null;
}

export interface CoursesResponse {
  courses: AdminCourse[];
  total: number;
  limit: number;
  offset: number;
}

export interface AdminPayout {
  id: string;
  instructor_id: string;
  amount: number;
  currency: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'CANCELLED';
  payout_method: string;
  requested_at: string | null;
  completed_at: string | null;
}

export interface PayoutsResponse {
  payouts: AdminPayout[];
  total: number;
  limit: number;
  offset: number;
}

export interface AdminReview {
  id: string;
  course_id: string;
  user_id: string;
  rating: number;
  comment: string;
  created_at: string | null;
}

export interface ReviewsResponse {
  reviews: AdminReview[];
  total: number;
  limit: number;
  offset: number;
}

export const adminService = {
  // Get platform statistics
  async getStats(): Promise<PlatformStats> {
    const response = await api.get('/admin/stats');
    return response.data;
  },

  // User management
  async getUsers(params?: {
    role?: 'LEARNER' | 'INSTRUCTOR' | 'ADMIN';
    is_active?: boolean;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<UsersResponse> {
    const queryParams = new URLSearchParams();
    if (params?.role) queryParams.append('role', params.role);
    if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    
    const response = await api.get(`/admin/users?${queryParams.toString()}`);
    return response.data;
  },

  async updateUserRole(userId: string, role: 'LEARNER' | 'INSTRUCTOR' | 'ADMIN'): Promise<void> {
    await api.put(`/admin/users/${userId}/role`, null, {
      params: { role }
    });
  },

  async activateUser(userId: string): Promise<void> {
    await api.put(`/admin/users/${userId}/activate`);
  },

  async deactivateUser(userId: string): Promise<void> {
    await api.put(`/admin/users/${userId}/deactivate`);
  },

  // Course management
  async getCourses(params?: {
    is_published?: boolean;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<CoursesResponse> {
    const queryParams = new URLSearchParams();
    if (params?.is_published !== undefined) queryParams.append('is_published', params.is_published.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    
    const response = await api.get(`/admin/courses?${queryParams.toString()}`);
    return response.data;
  },

  async deleteCourse(courseId: string): Promise<void> {
    await api.delete(`/admin/courses/${courseId}`);
  },

  // Payout management
  async getPayouts(params?: {
    status?: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'CANCELLED';
    limit?: number;
    offset?: number;
  }): Promise<PayoutsResponse> {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    
    const response = await api.get(`/admin/payouts?${queryParams.toString()}`);
    return response.data;
  },

  async approvePayout(payoutId: string): Promise<void> {
    await api.put(`/admin/payouts/${payoutId}/approve`);
  },

  async completePayout(payoutId: string, transactionReference: string): Promise<void> {
    await api.put(`/admin/payouts/${payoutId}/complete`, null, {
      params: { transaction_reference: transactionReference }
    });
  },

  async rejectPayout(payoutId: string, reason: string): Promise<void> {
    await api.put(`/admin/payouts/${payoutId}/reject`, null, {
      params: { reason }
    });
  },

  // Review moderation
  async getReportedReviews(params?: {
    limit?: number;
    offset?: number;
  }): Promise<ReviewsResponse> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    
    const response = await api.get(`/admin/reviews/reported?${queryParams.toString()}`);
    return response.data;
  },
};
