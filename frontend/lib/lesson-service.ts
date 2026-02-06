import api from './api';

export interface Lesson {
  id: string;
  module_id: string;
  title: string;
  content_type: 'video' | 'article' | 'quiz' | 'interactive' | 'code_exercise';
  content_url?: string;
  content_body?: string;
  content_metadata: any;
  estimated_minutes?: number;
  difficulty_score?: number;
  prerequisites: any[];
  skill_tags: string[];
  learning_objectives: string[];
  sequence_order: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface LessonProgress {
  id: string;
  user_id: string;
  lesson_id: string;
  enrollment_id?: string;
  completion_percentage: number;
  time_spent_seconds: number;
  first_accessed: string;
  last_accessed: string;
  completed_at?: string;
}

export interface LessonProgressUpdate {
  completion_percentage?: number;
  time_spent_seconds?: number;
}

export const lessonService = {
  async getLesson(lessonId: string): Promise<Lesson> {
    const response = await api.get(`/courses/lessons/${lessonId}`);
    return response.data;
  },

  async getModuleLessons(moduleId: string): Promise<Lesson[]> {
    const response = await api.get(`/courses/modules/${moduleId}/lessons`);
    return response.data;
  },

  async getLessonProgress(lessonId: string): Promise<LessonProgress | null> {
    try {
      const response = await api.get(`/learning/progress/lessons/${lessonId}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  async updateProgress(
    lessonId: string,
    data: LessonProgressUpdate
  ): Promise<LessonProgress> {
    const response = await api.put(`/learning/progress/lessons/${lessonId}`, data);
    return response.data;
  },

  async markComplete(lessonId: string, timeSpent: number = 0): Promise<LessonProgress> {
    const response = await api.put(`/learning/progress/lessons/${lessonId}`, {
      completion_percentage: 100,
      time_spent_seconds: timeSpent,
    });
    return response.data;
  },
};
