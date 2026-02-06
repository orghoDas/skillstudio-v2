'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import { assessmentService, Assessment } from '@/lib/assessment-service';
import { 
  ClipboardList,
  Clock,
  Target,
  TrendingUp,
  Award,
  ArrowRight,
  Loader2,
  AlertCircle,
  CheckCircle,
  BookOpen
} from 'lucide-react';

export default function AssessmentsPage() {
  const router = useRouter();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'diagnostic'>('all');

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadAssessments();
  }, [router, filter]);

  const loadAssessments = async () => {
    try {
      setError(null);
      setLoading(true);
      const data = await assessmentService.listAssessments(filter === 'diagnostic');
      setAssessments(data);
    } catch (error: any) {
      console.error('Failed to load assessments:', error);
      setError(error.message || 'Failed to load assessments');
    } finally {
      setLoading(false);
    }
  };

  const handleStartAssessment = (assessmentId: string) => {
    router.push(`/dashboard/assessments/${assessmentId}`);
  };

  const getDifficultyColor = (skillCount: number) => {
    if (skillCount >= 5) return 'text-red-600';
    if (skillCount >= 3) return 'text-purple-600';
    return 'text-blue-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to Load Assessments</h3>
              <p className="text-red-700 mb-4">{error}</p>
              <button 
                onClick={loadAssessments}
                className="btn-primary"
              >
                Try Again
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
          <ClipboardList className="w-8 h-8 text-primary-600" />
          Assessments
        </h1>
        <p className="text-gray-600">Test your skills and track your progress</p>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'all'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Assessments
        </button>
        <button
          onClick={() => setFilter('diagnostic')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'diagnostic'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Diagnostic Tests
        </button>
      </div>

      {/* Assessments Grid */}
      {assessments.length === 0 ? (
        <div className="text-center py-16">
          <ClipboardList className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Assessments Available</h3>
          <p className="text-gray-600 mb-6">
            {filter === 'diagnostic' 
              ? 'No diagnostic assessments found. Try viewing all assessments.'
              : 'Check back later for new assessments.'}
          </p>
          {filter === 'diagnostic' && (
            <button
              onClick={() => setFilter('all')}
              className="btn-primary"
            >
              View All Assessments
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assessments.map((assessment) => (
            <div
              key={assessment.id}
              className="card hover:shadow-lg transition-all duration-300"
            >
              {/* Badge */}
              {assessment.is_diagnostic && (
                <div className="mb-4">
                  <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                    <TrendingUp className="w-3 h-3" />
                    Diagnostic
                  </span>
                </div>
              )}

              {/* Title */}
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {String(assessment.title)}
              </h3>

              {/* Description */}
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {String(assessment.description)}
              </p>

              {/* Stats */}
              <div className="space-y-2 mb-4">
                {assessment.time_limit_minutes && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Clock className="w-4 h-4" />
                    <span>{assessment.time_limit_minutes} minutes</span>
                  </div>
                )}
                
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Target className="w-4 h-4" />
                  <span>{assessment.passing_score}% to pass</span>
                </div>

                {assessment.question_count && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <BookOpen className="w-4 h-4" />
                    <span>{assessment.question_count} questions</span>
                  </div>
                )}
              </div>

              {/* Skills Assessed */}
              {assessment.skills_assessed && assessment.skills_assessed.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-xs font-medium text-gray-700 mb-2">Skills Assessed</h4>
                  <div className="flex flex-wrap gap-1">
                    {assessment.skills_assessed.slice(0, 3).map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded"
                      >
                        {typeof skill === 'string' ? skill : String(skill)}
                      </span>
                    ))}
                    {assessment.skills_assessed.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        +{assessment.skills_assessed.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Action Button */}
              <button
                onClick={() => handleStartAssessment(assessment.id)}
                className="btn-primary w-full text-sm flex items-center justify-center gap-2"
              >
                Start Assessment
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Info Card */}
      {assessments.length > 0 && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Award className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Assessment Tips</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <span>Read each question carefully before answering</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <span>Diagnostic tests help us personalize your learning path</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <span>You'll get detailed AI feedback after completion</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
