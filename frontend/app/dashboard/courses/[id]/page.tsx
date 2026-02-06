'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { authService } from '@/lib/auth';
import { courseService, Course, Module, Enrollment } from '@/lib/course-service';
import { 
  BookOpen,
  Clock,
  Users,
  Award,
  CheckCircle,
  Play,
  Loader2,
  AlertCircle,
  ArrowLeft,
  Target,
  ChevronDown,
  ChevronRight,
  Lock
} from 'lucide-react';

export default function CourseDetailPage() {
  const router = useRouter();
  const params = useParams();
  const courseId = params.id as string;

  const [course, setCourse] = useState<Course | null>(null);
  const [modules, setModules] = useState<Module[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadCourseData();
  }, [router, courseId]);

  const loadCourseData = async () => {
    try {
      setError(null);
      setLoading(true);
      
      const [courseData, modulesData, enrollmentsData] = await Promise.all([
        courseService.getCourse(courseId),
        courseService.getModules(courseId),
        courseService.getMyEnrollments(),
      ]);

      setCourse(courseData);
      setModules(modulesData);
      setEnrollments(enrollmentsData);
      
      // Check if already enrolled
      const enrolled = enrollmentsData.some(e => e.course_id === courseId);
      setIsEnrolled(enrolled);
      
    } catch (error: any) {
      console.error('Failed to load course:', error);
      setError(error.message || 'Failed to load course');
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async () => {
    setEnrolling(true);
    try {
      await courseService.enrollInCourse(courseId);
      setIsEnrolled(true);
      alert('Successfully enrolled! Start learning now.');
      // Reload to get updated enrollment
      loadCourseData();
    } catch (error: any) {
      console.error('Failed to enroll:', error);
      alert('Failed to enroll: ' + error.message);
    } finally {
      setEnrolling(false);
    }
  };

  const toggleModule = (moduleId: string) => {
    const newExpanded = new Set(expandedModules);
    if (newExpanded.has(moduleId)) {
      newExpanded.delete(moduleId);
    } else {
      newExpanded.add(moduleId);
    }
    setExpandedModules(newExpanded);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-700 border-green-200';
      case 'intermediate': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'advanced': return 'bg-purple-100 text-purple-700 border-purple-200';
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

  if (error || !course) {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to Load Course</h3>
              <p className="text-red-700 mb-4">{error || 'Course not found'}</p>
              <button onClick={() => router.push('/dashboard/courses')} className="btn-primary">
                Back to Courses
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-8 py-6">
          <button
            onClick={() => router.push('/dashboard/courses')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Courses
          </button>

          <div className="flex items-start justify-between gap-8">
            <div className="flex-1">
              <span className={`inline-block px-3 py-1 rounded-lg text-xs font-medium border mb-3 ${getDifficultyColor(course.difficulty_level)}`}>
                {course.difficulty_level.charAt(0).toUpperCase() + course.difficulty_level.slice(1)}
              </span>
              
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                {String(course.title)}
              </h1>
              
              <p className="text-lg text-gray-600 mb-6">
                {String(course.short_description || course.description)}
              </p>

              {/* Stats */}
              <div className="flex items-center gap-6 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  <span>{course.estimated_duration_hours} hours</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  <span>{course.total_enrollments} enrolled</span>
                </div>
                <div className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  <span>{modules.length} modules</span>
                </div>
              </div>
            </div>

            {/* Enroll Card */}
            <div className="card w-80 sticky top-24">
              {isEnrolled ? (
                <>
                  <div className="text-center mb-4">
                    <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-2" />
                    <p className="font-semibold text-gray-900">You're Enrolled!</p>
                  </div>
                  <button
                    onClick={() => router.push(`/dashboard/courses/${courseId}/learn`)}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    <Play className="w-5 h-5" />
                    Continue Learning
                  </button>
                </>
              ) : (
                <>
                  <div className="text-center mb-4">
                    <p className="text-3xl font-bold text-gray-900 mb-2">Free</p>
                    <p className="text-sm text-gray-600">Lifetime access</p>
                  </div>
                  <button
                    onClick={handleEnroll}
                    disabled={enrolling}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    {enrolling ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Enrolling...
                      </>
                    ) : (
                      'Enroll Now'
                    )}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Description */}
            <div className="card">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">About This Course</h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                {String(course.description)}
              </p>
            </div>

            {/* Skills */}
            {course.skills_taught && course.skills_taught.length > 0 && (
              <div className="card">
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Target className="w-6 h-6 text-primary-600" />
                  Skills You'll Learn
                </h2>
                <div className="flex flex-wrap gap-2">
                  {course.skills_taught.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-4 py-2 bg-primary-50 text-primary-700 rounded-lg font-medium"
                    >
                      {typeof skill === 'string' ? skill : String(skill)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Prerequisites */}
            {course.prerequisites && course.prerequisites.length > 0 && (
              <div className="card">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Prerequisites</h2>
                <ul className="space-y-2">
                  {course.prerequisites.map((prereq, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-gray-700">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                      <span>{typeof prereq === 'string' ? prereq : String(prereq)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Course Content */}
            <div className="card">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Course Content</h2>
              <div className="space-y-3">
                {modules.map((module, idx) => (
                  <div key={module.id} className="border border-gray-200 rounded-lg overflow-hidden">
                    <button
                      onClick={() => toggleModule(module.id)}
                      className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        {expandedModules.has(module.id) ? (
                          <ChevronDown className="w-5 h-5 text-gray-600" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-gray-600" />
                        )}
                        <div className="text-left">
                          <h3 className="font-semibold text-gray-900">
                            Module {idx + 1}: {String(module.title)}
                          </h3>
                          <p className="text-sm text-gray-600">{module.est_duration_minutes} minutes</p>
                        </div>
                      </div>
                      {!isEnrolled && <Lock className="w-5 h-5 text-gray-400" />}
                    </button>
                    
                    {expandedModules.has(module.id) && (
                      <div className="border-t border-gray-200 bg-gray-50 p-4">
                        <p className="text-gray-700 mb-3">{String(module.description)}</p>
                        {!isEnrolled && (
                          <p className="text-sm text-gray-500 italic">
                            Enroll to view lessons
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                ))}

                {modules.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                    <p>Course content coming soon</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Sticky Sidebar */}
          <div className="space-y-6">
            <div className="card sticky top-24">
              <h3 className="font-bold text-gray-900 mb-4">Course Includes</h3>
              <ul className="space-y-3">
                <li className="flex items-center gap-3 text-sm text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span>{course.estimated_duration_hours} hours of content</span>
                </li>
                <li className="flex items-center gap-3 text-sm text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span>Lifetime access</span>
                </li>
                <li className="flex items-center gap-3 text-sm text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span>Progress tracking</span>
                </li>
                <li className="flex items-center gap-3 text-sm text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span>Certificate of completion</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
