import api from './api';

// Helper to extract error message from API response
function getErrorMessage(error: any): string {
  // Network errors (server not reachable)
  if (!error.response && error.request) {
    return 'Cannot connect to server. Please check if the backend is running on http://localhost:8000';
  }
  
  // Authentication errors
  if (error.response?.status === 401) {
    return 'Not authenticated. Please log in to continue.';
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
export interface Assessment {
  id: string;
  title: string;
  description: string;
  is_diagnostic: boolean;
  skills_assessed: string[];
  time_limit_minutes?: number;
  passing_score: number;
  created_at: string;
  question_count?: number;
}

export interface AssessmentQuestion {
  id: string;
  assessment_id: string;
  question_text: string;
  question_type: 'mcq' | 'true_false' | 'short_answer' | 'code';
  options?: string[];
  difficulty_level: 'EASY' | 'MEDIUM' | 'HARD';
  points: number;
  skill_tags: string[];
  sequence_order: number;
}

export interface QuestionWithAnswer extends AssessmentQuestion {
  correct_answer: any;
  explanation: string;
}

export interface AssessmentAttempt {
  id: string;
  user_id: string;
  assessment_id: string;
  score_percentage: number;
  points_earned: number;
  points_possible: number;
  time_taken_seconds: number;
  answers: any[];
  skill_scores: { [key: string]: number };
  attempt_number: number;
  passed: boolean;
  feedback: string;
  attempted_at: string;
}

export interface SubmitAnswerRequest {
  answers: Array<{
    question_id: string;
    answer: any;
  }>;
  time_taken_seconds: number;
}

export interface AIFeedback {
  performance_summary: {
    overall_score: number;
    percentile: number;
    skill_breakdown: { [key: string]: number };
  };
  strengths: string[];
  areas_for_improvement: string[];
  personalized_recommendations: Array<{
    type: string;
    message: string;
    priority: string;
  }>;
  progress_comparison?: {
    previous_score: number;
    current_score: number;
    improvement: number;
  };
  next_steps: string[];
}

export interface AdaptiveQuestion {
  question: AssessmentQuestion;
  total_answered: number;
  total_questions: number;
  current_difficulty: string;
  estimated_score?: number;
}

export const assessmentService = {
  // List all assessments
  async listAssessments(diagnosticOnly: boolean = false): Promise<Assessment[]> {
    try {
      const url = diagnosticOnly ? '/assessments?diagnostic_only=true' : '/assessments';
      console.log('🔍 Fetching assessments from:', url);
      const response = await api.get(url);
      console.log('✅ Assessments loaded:', response.data.length, 'items');
      return response.data;
    } catch (error: any) {
      console.error('❌ Failed to list assessments:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        hasResponse: !!error.response,
        hasRequest: !!error.request,
        message: error.message,
        fullError: error
      });
      throw new Error(getErrorMessage(error));
    }
  },

  // Get assessment details
  async getAssessment(assessmentId: string): Promise<Assessment> {
    try {
      console.log('🔍 Fetching assessment details:', assessmentId);
      const response = await api.get(`/assessments/${assessmentId}`);
      console.log('✅ Assessment details loaded');
      return response.data;
    } catch (error: any) {
      console.error('❌ Failed to get assessment:', {
        assessmentId,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message
      });
      throw new Error(getErrorMessage(error));
    }
  },

  // Get questions for assessment (without answers for learners)
  async getQuestions(assessmentId: string): Promise<AssessmentQuestion[]> {
    try {
      console.log('🔍 Fetching questions for assessment:', assessmentId);
      const hasToken = typeof window !== 'undefined' && localStorage.getItem('token');
      console.log('🔑 Auth token present:', !!hasToken);
      const response = await api.get(`/assessments/${assessmentId}/questions`);
      console.log('✅ Questions loaded:', response.data.length, 'questions');
      return response.data;
    } catch (error: any) {
      console.error('❌ Failed to get questions:', {
        assessmentId,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        isAuthError: error.response?.status === 401
      });
      
      // Provide clearer error message for auth failures
      if (error.response?.status === 401) {
        throw new Error('Authentication required. Please log in to view questions.');
      }
      
      throw new Error(getErrorMessage(error));
    }
  },

  // Submit assessment answers
  async submitAssessment(
    assessmentId: string,
    submission: SubmitAnswerRequest
  ): Promise<AssessmentAttempt> {
    try {
      const response = await api.post(`/assessments/${assessmentId}/submit`, submission);
      return response.data;
    } catch (error: any) {
      console.error('Failed to submit assessment:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Get specific attempt
  async getAttempt(attemptId: string): Promise<AssessmentAttempt> {
    try {
      const response = await api.get(`/assessments/attempts/${attemptId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get attempt:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Get AI-generated feedback for an attempt
  async getAIFeedback(attemptId: string): Promise<AIFeedback> {
    try {
      const response = await api.post(`/assessments/attempts/${attemptId}/ai-feedback`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get AI feedback:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Adaptive assessment: Get next question
  async getNextAdaptiveQuestion(
    assessmentId: string,
    previousAnswers: Array<{ question_id: string; answer: any }> = []
  ): Promise<AdaptiveQuestion | null> {
    try {
      const response = await api.post(`/assessments/adaptive/${assessmentId}/next-question`, {
        previous_answers: previousAnswers,
      });
      
      if (response.data.completed) {
        return null;
      }
      
      return response.data;
    } catch (error: any) {
      console.error('Failed to get next question:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Calculate adaptive score
  async calculateAdaptiveScore(
    assessmentId: string,
    answers: Array<{ question_id: string; answer: any; difficulty_level: string }>
  ): Promise<any> {
    try {
      const response = await api.post(`/assessments/adaptive/${assessmentId}/calculate-score`, {
        answers,
      });
      return response.data;
    } catch (error: any) {
      console.error('Failed to calculate score:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },

  // Get user's attempt history for an assessment
  async getUserAttempts(assessmentId: string): Promise<AssessmentAttempt[]> {
    try {
      // This would require a new backend endpoint
      // For now, return empty array
      return [];
    } catch (error: any) {
      console.error('Failed to get attempts:', getErrorMessage(error));
      throw new Error(getErrorMessage(error));
    }
  },
};
