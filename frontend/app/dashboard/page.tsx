'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import { aiService, CourseRecommendation, NextBestAction } from '@/lib/ai-service';
import { 
  Sparkles, 
  TrendingUp, 
  Clock, 
  Award,
  ArrowRight,
  Target,
  Loader2
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [recommendations, setRecommendations] = useState<CourseRecommendation[]>([]);
  const [nextAction, setNextAction] = useState<NextBestAction | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadDashboardData();
  }, [router]);

  const loadDashboardData = async () => {
    try {
      const [recs, action] = await Promise.all([
        aiService.getRecommendations(6),
        aiService.getNextBestAction(),
      ]);
      setRecommendations(recs);
      setNextAction(action);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-700';
      case 'intermediate': return 'bg-blue-100 text-blue-700';
      case 'advanced': return 'bg-purple-100 text-purple-700';
      case 'expert': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-blue-600';
    if (score >= 30) return 'text-yellow-600';
    return 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {authService.getCurrentUser()?.full_name?.split(' ')[0]}! 👋
        </h1>
        <p className="text-gray-600">Here's your personalized learning journey</p>
      </div>

      {/* Next Best Action */}
      {nextAction && (
        <div className="mb-8 bg-gradient-to-r from-primary-500 to-purple-600 rounded-xl p-6 text-white">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5" />
                <span className="text-sm font-medium opacity-90">AI Recommendation</span>
              </div>
              <h2 className="text-2xl font-bold mb-2">
                {nextAction.action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </h2>
              <p className="text-white/90 mb-4">{nextAction.reason}</p>
              <button className="bg-white text-primary-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center gap-2">
                Take Action
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
            <Target className="w-16 h-16 opacity-20" />
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Recommended Courses</h3>
            <TrendingUp className="w-5 h-5 text-primary-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{recommendations.length}</p>
          <p className="text-sm text-gray-500 mt-1">Personalized for you</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Estimated Hours</h3>
            <Clock className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {recommendations.reduce((sum, r) => sum + r.estimated_duration_hours, 0)}h
          </p>
          <p className="text-sm text-gray-500 mt-1">Learning time ahead</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Match Score</h3>
            <Award className="w-5 h-5 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {recommendations.length > 0 
              ? Math.round(recommendations.reduce((sum, r) => sum + r.recommendation_score, 0) / recommendations.length)
              : 0}%
          </p>
          <p className="text-sm text-gray-500 mt-1">Avg recommendation score</p>
        </div>
      </div>

      {/* Course Recommendations */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary-600" />
            Recommended for You
          </h2>
          <button 
            onClick={() => router.push('/dashboard/courses')}
            className="text-primary-600 hover:text-primary-700 font-medium text-sm flex items-center gap-1"
          >
            View All Courses
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendations.map((course) => (
            <div key={course.course_id} className="card hover:shadow-md transition-shadow">
              {/* Score Badge */}
              <div className="flex items-start justify-between mb-3">
                <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(course.difficulty_level)}`}>
                  {course.difficulty_level}
                </span>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${getScoreColor(course.recommendation_score)}`}>
                    {Math.round(course.recommendation_score)}
                  </div>
                  <div className="text-xs text-gray-500">Match Score</div>
                </div>
              </div>

              {/* Title */}
              <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">
                {course.title}
              </h3>

              {/* Description */}
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {course.description}
              </p>

              {/* Duration */}
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
                <Clock className="w-4 h-4" />
                {course.estimated_duration_hours} hours
              </div>

              {/* Skills */}
              <div className="flex flex-wrap gap-1 mb-3">
                {course.skills_taught.slice(0, 3).map((skill, idx) => (
                  <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                    {skill}
                  </span>
                ))}
              </div>

              {/* Reasons */}
              <div className="mb-4">
                {course.reasons.slice(0, 2).map((reason, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-gray-600 mb-1">
                    <Sparkles className="w-3 h-3 text-primary-500 mt-0.5 flex-shrink-0" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>

              {/* Action Button */}
              <button className="btn-primary w-full text-sm">
                View Course
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
