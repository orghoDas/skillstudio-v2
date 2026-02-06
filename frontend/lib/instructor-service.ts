import api from './api';

export interface InstructorStats {
  total_courses: number;
  total_students: number;
  total_enrollments: number;
  published_courses: number;
  draft_courses: number;
  average_course_rating: number;
}

export interface CourseStats {
  course_id: string;
  course_title: string;
  total_enrollments: number;
  active_students: number;
  completion_rate: number;
  average_rating: number;
}

export interface StudentEnrollment {
  student_id: string;
  student_name: string;
  student_email: string;
  course_id: string;
  course_title: string;
  enrolled_at: string;
  progress_percentage: number;
  completed: boolean;
  last_accessed: string | null;
}

export interface CourseAnalytics {
  course_id: string;
  course_title: string;
  enrollment_trend: Array<{ date: string; count: number }>;
  progress_distribution: {
    '0-25': number;
    '25-50': number;
    '50-75': number;
    '75-100': number;
  };
  total_enrollments: number;
  average_progress: number;
}

export const instructorService = {
  async getStats(): Promise<InstructorStats> {
    const response = await api.get('/instructor/stats');
    return response.data;
  },

  async getCoursesStats(): Promise<CourseStats[]> {
    const response = await api.get('/instructor/courses/stats');
    return response.data;
  },

  async getStudents(courseId?: string): Promise<StudentEnrollment[]> {
    const url = courseId
      ? `/instructor/students?course_id=${courseId}`
      : '/instructor/students';
    const response = await api.get(url);
    return response.data;
  },

  async getCourseAnalytics(courseId: string): Promise<CourseAnalytics> {
    const response = await api.get(`/instructor/courses/${courseId}/analytics`);
    return response.data;
  },
};
