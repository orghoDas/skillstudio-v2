import api from './api';

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

export interface CourseCreate {
  title: string;
  description?: string;
  short_description?: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  estimated_duration_hours?: number;
  skills_taught: string[];
  prerequisites: string[];
  thumbnail_url?: string;
}

export interface CourseUpdate extends Partial<CourseCreate> {
  is_published?: boolean;
}

export interface Module {
  id: string;
  course_id: string;
  title: string;
  description?: string;
  sequence_order: number;
  est_duration_minutes?: number;
  created_at: string;
}

export interface ModuleCreate {
  title: string;
  description?: string;
  sequence_order: number;
  est_duration_minutes?: number;
}

export interface Lesson {
  id: string;
  module_id: string;
  title: string;
  content_type: 'video' | 'article' | 'quiz' | 'interactive' | 'code_exercise';
  content_url?: string;
  content_body?: string;
  content_metadata?: Record<string, any>;
  estimated_minutes?: number;
  difficulty_score?: number;
  prerequisites?: any[];
  skill_tags?: string[];
  learning_objectives?: string[];
  sequence_order: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface LessonCreate {
  title: string;
  content_type: 'video' | 'article' | 'quiz' | 'interactive' | 'code_exercise';
  content_url?: string;
  content_body?: string;
  content_metadata?: Record<string, any>;
  estimated_minutes?: number;
  difficulty_score?: number;
  prerequisites?: any[];
  skill_tags?: string[];
  learning_objectives?: string[];
  sequence_order: number;
}

export const instructorCourseService = {
  // Course management
  async getCourses(): Promise<Course[]> {
    const response = await api.get('/courses/');
    return response.data;
  },

  async getMyCourses(): Promise<Course[]> {
    // TODO: Backend endpoint to filter by current instructor
    const response = await api.get('/courses/');
    return response.data;
  },

  async getCourse(courseId: string): Promise<Course> {
    const response = await api.get(`/courses/${courseId}`);
    return response.data;
  },

  async createCourse(data: CourseCreate): Promise<Course> {
    const response = await api.post('/courses/', data);
    return response.data;
  },

  async updateCourse(courseId: string, data: CourseUpdate): Promise<Course> {
    const response = await api.put(`/courses/${courseId}`, data);
    return response.data;
  },

  async deleteCourse(courseId: string): Promise<void> {
    await api.delete(`/courses/${courseId}`);
  },

  async publishCourse(courseId: string): Promise<Course> {
    const response = await api.put(`/courses/${courseId}`, { is_published: true });
    return response.data;
  },

  async unpublishCourse(courseId: string): Promise<Course> {
    const response = await api.put(`/courses/${courseId}`, { is_published: false });
    return response.data;
  },

  // Module management
  async getModules(courseId: string): Promise<Module[]> {
    const response = await api.get(`/courses/${courseId}/modules`);
    return response.data;
  },

  async createModule(courseId: string, data: ModuleCreate): Promise<Module> {
    const response = await api.post(`/courses/${courseId}/modules`, data);
    return response.data;
  },

  async updateModule(moduleId: string, data: Partial<ModuleCreate>): Promise<Module> {
    const response = await api.put(`/courses/modules/${moduleId}`, data);
    return response.data;
  },

  async deleteModule(moduleId: string): Promise<void> {
    await api.delete(`/courses/modules/${moduleId}`);
  },

  // Lesson management
  async getLessons(moduleId: string): Promise<Lesson[]> {
    const response = await api.get(`/courses/modules/${moduleId}/lessons`);
    return response.data;
  },

  async createLesson(moduleId: string, data: LessonCreate): Promise<Lesson> {
    const response = await api.post(`/courses/modules/${moduleId}/lessons`, data);
    return response.data;
  },

  async updateLesson(lessonId: string, data: Partial<LessonCreate>): Promise<Lesson> {
    const response = await api.put(`/courses/lessons/${lessonId}`, data);
    return response.data;
  },

  async deleteLesson(lessonId: string): Promise<void> {
    await api.delete(`/courses/lessons/${lessonId}`);
  },
};
