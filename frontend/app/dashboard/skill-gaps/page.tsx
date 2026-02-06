'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import { aiService, SkillGapAnalysis } from '@/lib/ai-service';
import { 
  Target, 
  TrendingUp, 
  AlertCircle,
  Award,
  Lightbulb,
  Loader2,
  Sparkles,
  ArrowRight,
  CheckCircle2
} from 'lucide-react';

export default function SkillGapsPage() {
  const router = useRouter();
  const [analysis, setAnalysis] = useState<SkillGapAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadSkillGapAnalysis();
  }, [router]);

  const loadSkillGapAnalysis = async () => {
    try {
      const data = await aiService.getSkillGapAnalysis();
      setAnalysis(data);
    } catch (err: any) {
      setError('Failed to load skill gap analysis');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-700 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getGapSizeColor = (size: string) => {
    switch (size.toLowerCase()) {
      case 'large': return 'w-full bg-red-500';
      case 'medium': return 'w-2/3 bg-yellow-500';
      case 'small': return 'w-1/3 bg-green-500';
      default: return 'w-0 bg-gray-500';
    }
  };

  const getReadinessColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 50) return 'text-yellow-600';
    if (percentage >= 25) return 'text-orange-600';
    return 'text-red-600';
  };

  const getReadinessStatus = (status: string) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto text-center py-16">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Unavailable</h2>
          <p className="text-gray-600 mb-6">{error || 'Unable to load skill gap analysis'}</p>
          <button onClick={() => router.push('/dashboard')} className="btn-primary">
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
          <div className="p-3 bg-purple-100 rounded-xl">
            <Target className="w-8 h-8 text-purple-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Skill Gap Analysis</h1>
            <p className="text-gray-600">AI-powered assessment of your learning progress</p>
          </div>
        </div>
      </div>

      {/* Overall Readiness */}
      <div className="mb-8 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl p-8 text-white">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-5 h-5" />
              <span className="text-sm font-medium opacity-90">Overall Readiness</span>
            </div>
            <h2 className="text-3xl font-bold mb-2">
              {getReadinessStatus(analysis.overall_readiness.status)}
            </h2>
            <p className="text-xl opacity-90 mb-6">
              {analysis.overall_readiness.acquired_skills} of {analysis.overall_readiness.total_target_skills} target skills acquired
            </p>
            
            {/* Progress Bar */}
            <div className="bg-white/20 rounded-full h-4 overflow-hidden mb-2">
              <div 
                className="bg-white h-full transition-all duration-500"
                style={{ width: `${analysis.overall_readiness.percentage}%` }}
              ></div>
            </div>
            <p className="text-sm opacity-90">
              {analysis.overall_readiness.percentage}% Ready
            </p>
          </div>
          <div className="text-right">
            <div className={`text-6xl font-bold mb-2 ${getReadinessColor(analysis.overall_readiness.percentage)}`}>
              {analysis.overall_readiness.percentage}%
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Strengths */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Award className="w-6 h-6 text-green-600" />
            Your Strengths
          </h2>
          
          {analysis.strengths.length > 0 ? (
            <div className="space-y-3">
              {Array.isArray(analysis.strengths) && analysis.strengths.map((strength, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-gray-900">{String(strength.skill || '')}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">{strength.level}</div>
                    <div className="text-xs text-gray-500">Level</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Award className="w-12 h-12 text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500">Building your foundation</p>
              <p className="text-sm text-gray-400">Complete courses to build strengths</p>
            </div>
          )}
        </div>

        {/* AI Recommendations */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Lightbulb className="w-6 h-6 text-yellow-600" />
            AI Recommendations
          </h2>
          
          <div className="space-y-3">
            {Array.isArray(analysis.recommendations) && analysis.recommendations.map((rec, idx) => (
              <div key={idx} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-gray-900 font-medium mb-1">
                      {typeof rec.message === 'string' ? rec.message : String(rec.message)}
                    </p>
                    {Array.isArray(rec.skills) && rec.skills.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {rec.skills.map((skill, sidx) => (
                          <span key={sidx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                            {typeof skill === 'string' ? skill : String(skill)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Skill Gaps */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-primary-600" />
          Skills to Develop ({analysis.skill_gaps.length})
        </h2>

        <div className="space-y-4">
          {Array.isArray(analysis.skill_gaps) && analysis.skill_gaps.map((gap, idx) => (
            <div key={idx} className="p-4 bg-gray-50 rounded-lg hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-bold text-gray-900">{String(gap.skill || '')}</h3>
                    <span className={`px-3 py-1 rounded-lg text-xs font-medium border ${getPriorityColor(gap.priority)}`}>
                      {String(gap.priority || 'medium').toUpperCase()} Priority
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                    <div>
                      Current Level: <span className="font-medium text-gray-900">{gap.current_level}</span>
                    </div>
                    <div>
                      Target: <span className="font-medium text-gray-900">{gap.target_level}</span>
                    </div>
                    <div>
                      Gap Size: <span className="font-medium capitalize">{gap.gap_size}</span>
                    </div>
                  </div>

                  {/* Gap Visualization */}
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div className={`h-full ${getGapSizeColor(gap.gap_size)} transition-all duration-500`}></div>
                    </div>
                  </div>
                </div>
              </div>

              <button 
                onClick={() => router.push('/dashboard/courses')}
                className="btn-primary text-sm flex items-center gap-2"
              >
                Find Courses
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        {analysis.skill_gaps.length === 0 && (
          <div className="text-center py-12">
            <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No Skill Gaps!</h3>
            <p className="text-gray-600">You've acquired all your target skills. Time to set new goals!</p>
          </div>
        )}
      </div>
    </div>
  );
}
