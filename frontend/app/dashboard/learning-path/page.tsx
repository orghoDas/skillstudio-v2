'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import { aiService, LearningPath } from '@/lib/ai-service';
import { 
  Map, 
  Target, 
  Clock, 
  TrendingUp, 
  Award,
  Check,
  Loader2,
  Sparkles,
  ArrowRight,
  Calendar
} from 'lucide-react';

export default function LearningPathPage() {
  const router = useRouter();
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadLearningPath();
  }, [router]);

  const loadLearningPath = async () => {
    try {
      const path = await aiService.getLearningPath();
      setLearningPath(path);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('No active learning goal found. Set a goal to get your personalized path!');
      } else {
        setError('Failed to load learning path');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-700 border-green-200';
      case 'intermediate': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'advanced': return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'expert': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error || !learningPath) {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto text-center py-16">
          <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Learning Path Yet</h2>
          <p className="text-gray-600 mb-6">
            {error || 'Set a learning goal to get your personalized course roadmap'}
          </p>
          <button 
            onClick={() => router.push('/dashboard')}
            className="btn-primary"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-primary-100 rounded-xl">
            <Map className="w-8 h-8 text-primary-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Your Learning Path</h1>
            <p className="text-gray-600">AI-generated roadmap to achieve your goals</p>
          </div>
        </div>
      </div>

      {/* Goal Card */}
      <div className="mb-8 bg-gradient-to-r from-primary-500 to-purple-600 rounded-xl p-8 text-white">
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5" />
              <span className="text-sm font-medium opacity-90">Learning Goal</span>
            </div>
            <h2 className="text-3xl font-bold mb-2">{learningPath.goal.description}</h2>
            <p className="text-xl opacity-90">{learningPath.goal.target_role}</p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold mb-2">{learningPath.completion_percentage}%</div>
            <div className="text-sm opacity-90">Complete</div>
          </div>
        </div>

        {/* Skills */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-medium opacity-90 mb-2">Target Skills</h3>
            <div className="flex flex-wrap gap-2">
              {Array.isArray(learningPath.goal.target_skills) && learningPath.goal.target_skills.map((skill, idx) => (
                <span key={idx} className="px-3 py-1 bg-white/20 backdrop-blur rounded-lg text-sm">
                  {typeof skill === 'string' ? skill : String(skill)}
                </span>
              ))}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-medium opacity-90 mb-2">Skills to Learn</h3>
            <div className="flex flex-wrap gap-2">
              {Array.isArray(learningPath.skills_to_learn) && learningPath.skills_to_learn.slice(0, 4).map((skill, idx) => (
                <span key={idx} className="px-3 py-1 bg-white/20 backdrop-blur rounded-lg text-sm">
                  {typeof skill === 'string' ? skill : String(skill)}
                </span>
              ))}
              {learningPath.skills_to_learn.length > 4 && (
                <span className="px-3 py-1 bg-white/20 backdrop-blur rounded-lg text-sm">
                  +{learningPath.skills_to_learn.length - 4} more
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Timeline Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Total Courses</h3>
            <Award className="w-5 h-5 text-primary-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{learningPath.learning_path.length}</p>
          <p className="text-sm text-gray-500 mt-1">In your path</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Total Hours</h3>
            <Clock className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{learningPath.timeline.total_hours}h</p>
          <p className="text-sm text-gray-500 mt-1">Learning time</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Estimated Timeline</h3>
            <Calendar className="w-5 h-5 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{learningPath.timeline.estimated_weeks}</p>
          <p className="text-sm text-gray-500 mt-1">Weeks ({learningPath.timeline.study_hours_per_week}h/week)</p>
        </div>
      </div>

      {/* Learning Path Timeline */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary-600" />
          Sequential Learning Roadmap
        </h2>

        <div className="space-y-4">
          {learningPath.learning_path.map((course, idx) => (
            <div key={course.course_id} className="relative">
              {/* Connection Line */}
              {idx < learningPath.learning_path.length - 1 && (
                <div className="absolute left-7 top-20 bottom-0 w-0.5 bg-gray-200 -mb-4"></div>
              )}

              <div className="flex gap-4">
                {/* Step Number */}
                <div className="flex-shrink-0">
                  <div className="w-14 h-14 bg-primary-100 rounded-full flex items-center justify-center border-4 border-white shadow-sm">
                    <span className="text-primary-700 font-bold text-lg">{course.sequence}</span>
                  </div>
                </div>

                {/* Course Card */}
                <div className="flex-1 bg-gray-50 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{String(course.title || 'Untitled Course')}</h3>
                      <div className="flex flex-wrap gap-2 mb-3">
                        <span className={`px-3 py-1 rounded-lg text-sm font-medium border ${getDifficultyColor(course.difficulty)}`}>
                          {course.difficulty}
                        </span>
                        <span className="px-3 py-1 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {course.duration_hours} hours
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Skills Gained */}
                  {Array.isArray(course.skills_gained) && course.skills_gained.length > 0 && (
                    <div className="mb-3">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <TrendingUp className="w-4 h-4" />
                        Skills You'll Gain
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {course.skills_gained.map((skill, idx) => (
                          <span key={idx} className="px-3 py-1 bg-green-50 text-green-700 rounded-lg text-sm font-medium flex items-center gap-1">
                            <Check className="w-3 h-3" />
                            {typeof skill === 'string' ? skill : String(skill)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Prerequisites */}
                  {Array.isArray(course.prerequisites) && course.prerequisites.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Prerequisites</h4>
                      <div className="flex flex-wrap gap-2">
                        {course.prerequisites.map((prereq, idx) => (
                          <span key={idx} className="px-3 py-1 bg-yellow-50 text-yellow-700 rounded-lg text-sm">
                            {typeof prereq === 'string' ? prereq : String(prereq)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action Button */}
                  <button 
                    onClick={() => alert(`Course enrollment coming soon!\nCourse: ${course.title}`)}
                    className="btn-primary text-sm flex items-center gap-2"
                  >
                    Start Learning
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Completion Message */}
        <div className="mt-8 p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Award className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-1">
                Complete this path to become a {learningPath.goal.target_role}!
              </h3>
              <p className="text-gray-600">
                Follow this AI-optimized sequence to efficiently build the skills you need for your dream role.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
