import api from './api';

// ==================== REVIEWS ====================

export interface CourseReview {
  id: string;
  course_id: string;
  user_id: string;
  rating: number;
  title?: string;
  review_text?: string;
  helpful_count: number;
  not_helpful_count: number;
  is_verified_purchase: boolean;
  instructor_response?: string;
  instructor_response_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ReviewCreate {
  rating: number;
  title?: string;
  review_text?: string;
}

export interface ReviewUpdate {
  rating?: number;
  title?: string;
  review_text?: string;
}

// ==================== CERTIFICATES ====================

export interface Certificate {
  id: string;
  user_id: string;
  course_id: string;
  certificate_number: string;
  issued_date: string;
  completion_percentage: number;
  final_grade?: number;
  total_hours_spent?: number;
  skills_achieved: string[];
  certificate_url?: string;
  verification_url?: string;
  is_revoked: boolean;
  created_at: string;
}

export interface CertificateVerification {
  certificate_number: string;
  user_name: string;
  course_title: string;
  issued_date: string;
  is_valid: boolean;
  completion_percentage: number;
  skills_achieved: string[];
}

// ==================== DISCUSSIONS ====================

export interface Discussion {
  id: string;
  course_id: string;
  lesson_id?: string;
  user_id: string;
  title: string;
  content: string;
  category: 'general' | 'lesson_specific' | 'technical' | 'career' | 'projects' | 'announcements';
  is_pinned: boolean;
  is_resolved: boolean;
  is_locked: boolean;
  views_count: number;
  reply_count: number;
  upvotes: number;
  tags: string[];
  created_at: string;
  updated_at: string;
  last_activity_at: string;
}

export interface DiscussionCreate {
  title: string;
  content: string;
  category?: 'general' | 'lesson_specific' | 'technical' | 'career' | 'projects' | 'announcements';
  lesson_id?: string;
  tags?: string[];
}

export interface DiscussionReply {
  id: string;
  discussion_id: string;
  user_id: string;
  parent_reply_id?: string;
  content: string;
  is_instructor_response: boolean;
  is_accepted_answer: boolean;
  upvotes: number;
  is_edited: boolean;
  edited_at?: string;
  created_at: string;
}

export interface ReplyCreate {
  content: string;
  parent_reply_id?: string;
}

export const socialService = {
  // ==================== REVIEWS ====================
  
  async createReview(courseId: string, data: ReviewCreate): Promise<CourseReview> {
    const response = await api.post(`/social/courses/${courseId}/reviews`, data);
    return response.data;
  },

  async getCourseReviews(
    courseId: string,
    sortBy: 'recent' | 'helpful' | 'rating' = 'recent',
    skip = 0,
    limit = 20
  ): Promise<CourseReview[]> {
    const response = await api.get(`/social/courses/${courseId}/reviews`, {
      params: { sort_by: sortBy, skip, limit },
    });
    return response.data;
  },

  async updateReview(reviewId: string, data: ReviewUpdate): Promise<CourseReview> {
    const response = await api.put(`/social/reviews/${reviewId}`, data);
    return response.data;
  },

  async deleteReview(reviewId: string): Promise<void> {
    await api.delete(`/social/reviews/${reviewId}`);
  },

  async respondToReview(reviewId: string, response_text: string): Promise<CourseReview> {
    const response = await api.post(`/social/reviews/${reviewId}/instructor-response`, {
      instructor_response: response_text,
    });
    return response.data;
  },

  async markReviewHelpful(reviewId: string, helpful: boolean): Promise<CourseReview> {
    const response = await api.post(`/social/reviews/${reviewId}/helpful`, null, {
      params: { helpful },
    });
    return response.data;
  },

  // ==================== CERTIFICATES ====================

  async generateCertificate(courseId: string): Promise<Certificate> {
    const response = await api.post(`/social/certificates/generate/${courseId}`);
    return response.data;
  },

  async getMyCertificates(): Promise<Certificate[]> {
    const response = await api.get('/social/certificates/my');
    return response.data;
  },

  async verifyCertificate(certificateNumber: string): Promise<CertificateVerification> {
    const response = await api.get(`/social/certificates/verify/${certificateNumber}`);
    return response.data;
  },

  // ==================== DISCUSSIONS ====================

  async createDiscussion(courseId: string, data: DiscussionCreate): Promise<Discussion> {
    const response = await api.post(`/social/courses/${courseId}/discussions`, data);
    return response.data;
  },

  async getCourseDiscussions(
    courseId: string,
    category?: string,
    isResolved?: boolean,
    skip = 0,
    limit = 20
  ): Promise<Discussion[]> {
    const response = await api.get(`/social/courses/${courseId}/discussions`, {
      params: { category, is_resolved: isResolved, skip, limit },
    });
    return response.data;
  },

  async getDiscussion(discussionId: string): Promise<Discussion> {
    const response = await api.get(`/social/discussions/${discussionId}`);
    return response.data;
  },

  async updateDiscussion(
    discussionId: string,
    data: Partial<DiscussionCreate & { is_resolved?: boolean; is_pinned?: boolean }>
  ): Promise<Discussion> {
    const response = await api.put(`/social/discussions/${discussionId}`, data);
    return response.data;
  },

  async createReply(discussionId: string, data: ReplyCreate): Promise<DiscussionReply> {
    const response = await api.post(`/social/discussions/${discussionId}/replies`, data);
    return response.data;
  },

  async getReplies(discussionId: string): Promise<DiscussionReply[]> {
    const response = await api.get(`/social/discussions/${discussionId}/replies`);
    return response.data;
  },

  async upvoteDiscussion(discussionId: string): Promise<Discussion> {
    const response = await api.post(`/social/discussions/${discussionId}/upvote`);
    return response.data;
  },
};
