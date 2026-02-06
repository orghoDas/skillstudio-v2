import api from './api';

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
    const response = await api.get(`/ai/recommendations?limit=${limit}`);
    return response.data.recommendations;
  },

  async getLearningPath(goalId?: string): Promise<LearningPath> {
    const url = goalId ? `/ai/learning-path?goal_id=${goalId}` : '/ai/learning-path';
    const response = await api.get(url);
    return response.data;
  },

  async getSkillGapAnalysis(): Promise<SkillGapAnalysis> {
    const response = await api.get('/ai/skill-gap-analysis');
    return response.data;
  },

  async getNextBestAction(): Promise<NextBestAction> {
    const response = await api.get('/ai/next-best-action');
    return response.data;
  },
};
