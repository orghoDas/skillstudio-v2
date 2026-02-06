import api from './api';

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

export interface CourseRecommendation {
  course_id: string;
  title: string;
  description: string;
  difficulty_level: string;
  estimated_duration_hours: number;
  skills_taught: string[];
  recommendation_score: number;
  score_breakdown: {
    skill_match: number;
    difficulty_match: number;
    goal_alignment: number;
    popularity: number;
    prerequisite_ready: number;
  };
  reasons: string[];
}

export interface LearningPathCourse {
  sequence: number;
  course_id: string;
  title: string;
  difficulty: string;
  duration_hours: number;
  skills_gained: string[];
  prerequisites?: string[];
}

export interface LearningPath {
  goal: {
    id: string;
    description: string;
    target_role: string;
    target_skills: string[];
  };
  current_skills: string[];
  skills_to_learn: string[];
  learning_path: LearningPathCourse[];
  timeline: {
    total_hours: number;
    estimated_weeks: number;
    study_hours_per_week: number;
  };
  completion_percentage: number;
}

export interface SkillGap {
  skill: string;
  current_level: number;
  target_level: string;
  gap_size: string;
  priority: string;
}

export interface SkillGapAnalysis {
  user_id: string;
  current_skills: { [key: string]: number };
  target_skills: string[];
  skill_gaps: SkillGap[];
  strengths: Array<{ skill: string; level: number }>;
  recommendations: Array<{
    type: string;
    message: string;
    skills?: string[];
  }>;
  overall_readiness: {
    percentage: number;
    status: string;
    acquired_skills: number;
    total_target_skills: number;
  };
}

export interface NextBestAction {
  action: string;
  reason: string;
  details: any;
}

export const aiService = {
  async getRecommendations(limit: number = 10): Promise<CourseRecommendation[]> {
    try {
      const response = await api.get(`/ai/recommendations?limit=${limit}`);
      return response.data.recommendations;
    } catch (error: any) {
      console.error('Failed to get recommendations:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  async getLearningPath(goalId?: string): Promise<LearningPath> {
    try {
      const url = goalId ? `/ai/learning-path?goal_id=${goalId}` : '/ai/learning-path';
      const response = await api.get(url);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get learning path:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  async getSkillGapAnalysis(): Promise<SkillGapAnalysis> {
    try {
      const response = await api.get('/ai/skill-gap-analysis');
      return response.data;
    } catch (error: any) {
      console.error('Failed to get skill gap analysis:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  async getNextBestAction(): Promise<NextBestAction> {
    try {
      const response = await api.get('/ai/next-best-action');
      return response.data;
    } catch (error: any) {
      console.error('Failed to get next best action:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },
};
