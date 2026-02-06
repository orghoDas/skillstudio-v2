'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { authService } from '@/lib/auth';
import { 
  assessmentService, 
  AssessmentAttempt,
  AIFeedback,
  Assessment
} from '@/lib/assessment-service';
import { 
  Award,
  TrendingUp,
  TrendingDown,
  Target,
  Clock,
  CheckCircle,
  XCircle,
  Sparkles,
  ArrowRight,
  Loader2,
  AlertCircle,
  Lightbulb,
  RotateCcw
} from 'lucide-react';

export default function AssessmentResultsPage() {
  const router = useRouter();
  const params = useParams();
  const assessmentId = params.id as string;
  const attemptId = params.attemptId as string;

  const [attempt, setAttempt] = useState<AssessmentAttempt | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [aiFeedback, setAIFeedback] = useState<AIFeedback | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingFeedback, setLoadingFeedback] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadResults();
  }, [router, assessmentId, attemptId]);

  const loadResults = async () => {
    try {
      setError(null);
      setLoading(true);
      
      // For now, we'll need to get the attempt data from a backend endpoint
      // Since we don't have a direct endpoint, we'll simulate it
      // In production, you'd add a GET /assessments/attempts/{id} endpoint
      
      // Placeholder - in reality you'd fetch the actual attempt
      setAttempt({
        id: attemptId,
        user_id: String(authService.getCurrentUser()?.id),
        assessment_id: assessmentId,
        score_percentage: 85,
        points_earned: 85,
        points_possible: 100,
        time_taken_seconds: 1200,
        answers: [],
        skill_scores: {
          'Python': 0.9,
          'JavaScript': 0.8,
          'Web Development': 0.85,
        },
        attempt_number: 1,
        passed: true,
        feedback: 'Great job! You demonstrated strong understanding of the material.',
        attempted_at: new Date().toISOString(),
      } as AssessmentAttempt);

      const assessmentData = await assessmentService.getAssessment(assessmentId);
      setAssessment(assessmentData);

    } catch (error: any) {
      console.error('Failed to load results:', error);
      setError(error.message || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const loadAIFeedback = async () => {
    setLoadingFeedback(true);
    try {
      const feedback = await assessmentService.getAIFeedback(attemptId);
      setAIFeedback(feedback);
    } catch (error: any) {
      console.error('Failed to load AI feedback:', error);
      alert('Failed to load AI feedback: ' + error.message);
    } finally {
      setLoadingFeedback(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-blue-50 border-blue-200';
    if (score >= 40) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error || !attempt || !assessment) {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to Load Results</h3>
              <p className="text-red-700 mb-4">{error || 'Results not found'}</p>
              <button 
                onClick={() => router.push('/dashboard/assessments')}
                className="btn-primary"
              >
                Back to Assessments
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <Award className="w-8 h-8 text-primary-600" />
          Assessment Results
        </h1>
        <p className="text-gray-600">{assessment.title}</p>
      </div>

      {/* Overall Score */}
      <div className={`card mb-8 border-2 ${getScoreBgColor(attempt.score_percentage)}`}>
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-white border-4 border-current mb-4">
            <div className={`text-5xl font-bold ${getScoreColor(attempt.score_percentage)}`}>
              {Math.round(attempt.score_percentage)}%
            </div>
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {attempt.passed ? (
              <span className="flex items-center justify-center gap-2">
                <CheckCircle className="w-6 h-6 text-green-600" />
                Passed!
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <XCircle className="w-6 h-6 text-red-600" />
                Not Passed
              </span>
            )}
          </h2>
          
          <p className="text-gray-600 mb-4">
            {attempt.points_earned} / {attempt.points_possible} points
            {' · '}
            Passing score: {assessment.passing_score}%
          </p>

          {attempt.passed ? (
            <p className="text-green-700 font-medium">
              Great job! You've demonstrated proficiency in this assessment.
            </p>
          ) : (
            <p className="text-red-700 font-medium">
              Keep practicing! Review the material and try again.
            </p>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Time Taken</h3>
            <Clock className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatTime(attempt.time_taken_seconds)}
          </p>
          {assessment.time_limit_minutes && (
            <p className="text-sm text-gray-500 mt-1">
              Limit: {assessment.time_limit_minutes} minutes
            </p>
          )}
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Attempt Number</h3>
            <RotateCcw className="w-5 h-5 text-purple-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            #{attempt.attempt_number}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {attempt.attempt_number === 1 ? 'First attempt' : 'Retake'}
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Result</h3>
            <Target className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {attempt.passed ? 'Pass' : 'Fail'}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {attempt.passed ? 'Excellent work!' : 'Try again'}
          </p>
        </div>
      </div>

      {/* Skill Breakdown */}
      {attempt.skill_scores && Object.keys(attempt.skill_scores).length > 0 && (
        <div className="card mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-primary-600" />
            Skill Breakdown
          </h2>
          
          <div className="space-y-4">
            {Object.entries(attempt.skill_scores).map(([skill, score]) => {
              const percentage = Math.round(score * 100);
              return (
                <div key={skill}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">{skill}</span>
                    <span className={`font-bold ${getScoreColor(percentage)}`}>
                      {percentage}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-500 ${
                        percentage >= 80 ? 'bg-green-500' :
                        percentage >= 60 ? 'bg-blue-500' :
                        percentage >= 40 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Feedback */}
      <div className="card mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Lightbulb className="w-6 h-6 text-yellow-600" />
          Feedback
        </h2>
        <p className="text-gray-700 leading-relaxed">
          {String(attempt.feedback)}
        </p>
      </div>

      {/* AI Feedback Section */}
      {!aiFeedback && (
        <div className="card mb-8 bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200">
          <div className="text-center py-8">
            <Sparkles className="w-12 h-12 text-purple-600 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Get AI-Powered Insights
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Receive comprehensive analysis of your performance, personalized recommendations,
              and detailed guidance on how to improve.
            </p>
            <button
              onClick={loadAIFeedback}
              disabled={loadingFeedback}
              className="btn-primary inline-flex items-center gap-2"
            >
              {loadingFeedback ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating Feedback...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate AI Feedback
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-4">
        <button
          onClick={() => router.push('/dashboard/assessments')}
          className="btn-primary flex items-center gap-2"
        >
          <ArrowRight className="w-4 h-4" />
          View All Assessments
        </button>
        
        {!attempt.passed && (
          <button
            onClick={() => router.push(`/dashboard/assessments/${assessmentId}`)}
            className="px-6 py-2 bg-purple-600 text-white hover:bg-purple-700 rounded-lg transition-colors flex items-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Retake Assessment
          </button>
        )}

        <button
          onClick={() => router.push('/dashboard')}
          className="px-6 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
}
