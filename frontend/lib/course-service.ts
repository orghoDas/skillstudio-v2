import api from './api';

// Helper to extract error message from API response
function getErrorMessage(error: any): string {
  // Network errors (server not reachable)
  if (!error.response && error.request) {
    return 'Cannot connect to server. Please check if the backend is running on http://localhost:8000';
  }
  
  // FastAPI validation errors
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (Array.isArray(detail)) {
      return detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
    }
    if (typeof detail === 'string') {
      return detail;
    }
    return JSON.stringify(detail);
  }
  
  // HTTP errors
  if (error.response?.status) {
    return `Server error: ${error.response.status} - ${error.response.statusText}`;
  }
  
  return error.message || 'An unexpected error occurred';
}

// Interfaces
export interface Course {
  id: string;
  title: string;
  description: string;
  short_description: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  estimated_duration_hours: number;
  skills_taught: string[];
  prerequisites: string[];
  thumbnail_url?: string;
  created_by: string;
  is_published: boolean;
  total_enrollments: number;
  average_rating?: number;
  created_at: string;
  updated_at: string;
}

export interface Module {
  id: string;
  course_id: string;
  title: string;
  description: string;
  sequence_order: number;
  est_duration_minutes: number;
  created_at: string;
}

export interface Lesson {
  id: string;
  module_id: string;
  title: string;
  content_type: 'video' | 'text' | 'code' | 'quiz' | 'interactive';
  content_url?: string;
  content_body?: string;
  content_metadata?: any;
  estimated_minutes: number;
  difficulty_score?: number;
  prerequisites?: string[];
  skill_tags: string[];
  learning_objectives: string[];
  sequence_order: number;
  created_at: string;
}

export interface Enrollment {
  id: string;
  user_id: string;
  course_id: string;
  learning_goal_id?: string;
  enrolled_at: string;
  progress_percentage: number;
  last_accessed?: string;
  completed_at?: string;
}

export interface LessonProgress {
  id: string;
  user_id: string;
  lesson_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  completion_percentage: number;
  time_spent_seconds: number;
  video_watch_percentage?: number;
  interactions?: any;
  first_accessed?: string;
  last_accessed?: string;
  completed_at?: string;
}

export const courseService = {
  // List all courses
  async listCourses(params?: {
    skip?: number;
    limit?: number;
    difficulty?: string;
    published_only?: boolean;
  }): Promise<Course[]> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.skip) queryParams.append('skip', params.skip.toString());
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.difficulty) queryParams.append('difficulty', params.difficulty);
      if (params?.published_only !== undefined) {
        queryParams.append('published_only', params.published_only.toString());
      }

      const url = `/courses?${queryParams.toString()}`;
      const response = await api.get(url);
      return response.data;
    } catch (error: any) {
      console.error('Failed to list courses:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Get course details
  async getCourse(courseId: string): Promise<Course> {
    try {
      const response = await api.get(`/courses/${courseId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get course:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Get modules for a course
  async getModules(courseId: string): Promise<Module[]> {
    try {
      const response = await api.get(`/courses/${courseId}/modules`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get modules:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Get lessons for a module
  async getLessons(moduleId: string): Promise<Lesson[]> {
    try {
      const response = await api.get(`/courses/modules/${moduleId}/lessons`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get lessons:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Get lesson details
  async getLesson(lessonId: string): Promise<Lesson> {
    try {
      const response = await api.get(`/courses/lessons/${lessonId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get lesson:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Enroll in a course
  async enrollInCourse(courseId: string, learningGoalId?: string): Promise<Enrollment> {
    try {
      const response = await api.post('/learning/enrollments', {
        course_id: courseId,
        learning_goal_id: learningGoalId,
      });
      return response.data;
    } catch (error: any) {
      console.error('Failed to enroll:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Get my enrollments
  async getMyEnrollments(): Promise<Enrollment[]> {
    try {
      const response = await api.get('/learning/enrollments');
      return response.data;
    } catch (error: any) {
      console.error('Failed to get enrollments:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Update lesson progress
  async updateLessonProgress(
    lessonId: string,
    data: {
      status?: 'not_started' | 'in_progress' | 'completed';
      completion_percentage?: number;
      time_spent_seconds?: number;
    }
  ): Promise<LessonProgress> {
    try {
      const response = await api.put(`/learning/progress/lessons/${lessonId}`, data);
      return response.data;
    } catch (error: any) {
      console.error('Failed to update progress:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Search courses
  async searchCourses(query: string): Promise<Course[]> {
    try {
      const courses = await this.listCourses({ published_only: true });
      const lowerQuery = query.toLowerCase();
      
      return courses.filter(course => 
        course.title.toLowerCase().includes(lowerQuery) ||
        course.description?.toLowerCase().includes(lowerQuery) ||
        course.skills_taught.some(skill => skill.toLowerCase().includes(lowerQuery))
      );
    } catch (error: any) {
      console.error('Failed to search courses:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },
};
