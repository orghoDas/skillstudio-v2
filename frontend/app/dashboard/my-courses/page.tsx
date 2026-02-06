'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import { courseService, Enrollment, Course } from '@/lib/course-service';
import { 
  BookOpen,
  Clock,
  Award,
  Play,
  Loader2,
  AlertCircle,
  TrendingUp,
  CheckCircle,
  RefreshCw
} from 'lucide-react';

interface EnrollmentWithCourse extends Enrollment {
  course?: Course;
}

export default function MyCoursesPage() {
  const router = useRouter();
  const [enrollments, setEnrollments] = useState<EnrollmentWithCourse[]>([]);
  const [filteredEnrollments, setFilteredEnrollments] = useState<EnrollmentWithCourse[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadEnrollments();
  }, [router]);

  useEffect(() => {
    filterEnrollments();
  }, [statusFilter, enrollments]);

  const loadEnrollments = async () => {
    try {
      setError(null);
      setLoading(true);
      
      const enrollmentsData = await courseService.getMyEnrollments();
      
      // Load course details for each enrollment
      const enrollmentsWithCourses = await Promise.all(
        enrollmentsData.map(async (enrollment) => {
          try {
            const course = await courseService.getCourse(enrollment.course_id);
            return { ...enrollment, course };
          } catch (err) {
            console.error(`Failed to load course ${enrollment.course_id}:`, err);
            return enrollment;
          }
        })
      );
      
      setEnrollments(enrollmentsWithCourses);
    } catch (error: any) {
      console.error('Failed to load enrollments:', error);
      setError(error.message || 'Failed to load your courses');
    } finally {
      setLoading(false);
    }
  };

  const filterEnrollments = () => {
    let filtered = [...enrollments];

    if (statusFilter === 'in-progress') {
      filtered = filtered.filter(e => e.progress_percentage > 0 && e.progress_percentage < 100);
    } else if (statusFilter === 'completed') {
      filtered = filtered.filter(e => e.progress_percentage >= 100);
    } else if (statusFilter === 'not-started') {
      filtered = filtered.filter(e => e.progress_percentage === 0);
    }

    setFilteredEnrollments(filtered);
  };

  const getStatusBadge = (percentage: number) => {
    if (percentage === 0) {
      return (
        <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-xs font-medium">
          Not Started
        </span>
      );
    } else if (percentage >= 100) {
      return (
        <span className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-medium flex items-center gap-1">
          <CheckCircle className="w-3 h-3" />
          Completed
        </span>
      );
    } else {
      return (
        <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-xs font-medium flex items-center gap-1">
          <TrendingUp className="w-3 h-3" />
          In Progress
        </span>
      );
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage === 0) return 'bg-gray-300';
    if (percentage < 30) return 'bg-red-500';
    if (percentage < 70) return 'bg-yellow-500';
    if (percentage < 100) return 'bg-blue-500';
    return 'bg-green-500';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const calculateStats = () => {
    const total = enrollments.length;
    const completed = enrollments.filter(e => e.progress_percentage >= 100).length;
    const inProgress = enrollments.filter(e => e.progress_percentage > 0 && e.progress_percentage < 100).length;
    const totalHours = enrollments.reduce((sum, e) => sum + (e.course?.estimated_duration_hours || 0), 0);
    
    return { total, completed, inProgress, totalHours };
  };

  const stats = calculateStats();

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
              <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to Load Courses</h3>
              <p className="text-red-700 mb-4">{error}</p>
              <button onClick={loadEnrollments} className="btn-primary flex items-center gap-2">
                <RefreshCw className="w-4 h-4" />
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
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">My Courses</h1>
          <p className="text-gray-600">Track your learning progress and continue where you left off</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-primary-100 rounded-lg">
                <BookOpen className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                <p className="text-sm text-gray-600">Total Courses</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
                <p className="text-sm text-gray-600">Completed</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-blue-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.inProgress}</p>
                <p className="text-sm text-gray-600">In Progress</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Clock className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.totalHours}</p>
                <p className="text-sm text-gray-600">Total Hours</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={() => setStatusFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              statusFilter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All ({enrollments.length})
          </button>
          <button
            onClick={() => setStatusFilter('in-progress')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              statusFilter === 'in-progress'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            In Progress ({stats.inProgress})
          </button>
          <button
            onClick={() => setStatusFilter('completed')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              statusFilter === 'completed'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Completed ({stats.completed})
          </button>
          <button
            onClick={() => setStatusFilter('not-started')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              statusFilter === 'not-started'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Not Started ({enrollments.filter(e => e.progress_percentage === 0).length})
          </button>
        </div>

        {/* Course List */}
        {filteredEnrollments.length === 0 ? (
          <div className="card text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {statusFilter === 'all' ? 'No Courses Yet' : `No ${statusFilter.replace('-', ' ')} Courses`}
            </h3>
            <p className="text-gray-600 mb-6">
              {statusFilter === 'all' 
                ? 'Browse the course catalog to get started with your learning journey'
                : `You don't have any ${statusFilter.replace('-', ' ')} courses`}
            </p>
            <button
              onClick={() => router.push('/dashboard/courses')}
              className="btn-primary"
            >
              Browse Courses
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredEnrollments.map((enrollment) => (
              <div
                key={enrollment.id}
                className="card hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => router.push(`/dashboard/courses/${enrollment.course_id}/learn`)}
              >
                <div className="flex items-start gap-6">
                  {/* Thumbnail */}
                  <div className="w-48 h-32 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex-shrink-0 flex items-center justify-center">
                    {enrollment.course?.thumbnail_url ? (
                      <img
                        src={enrollment.course.thumbnail_url}
                        alt={String(enrollment.course?.title || '')}
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <BookOpen className="w-12 h-12 text-white" />
                    )}
                  </div>

                  {/* Course Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 mb-1">
                          {String(enrollment.course?.title || 'Loading...')}
                        </h3>
                        <p className="text-gray-600 line-clamp-2">
                          {String(enrollment.course?.short_description || enrollment.course?.description || '')}
                        </p>
                      </div>
                      {getStatusBadge(enrollment.progress_percentage)}
                    </div>

                    {/* Progress Bar */}
                    <div className="mb-4">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-gray-600">Progress</span>
                        <span className="font-semibold text-gray-900">
                          {enrollment.progress_percentage}% Complete
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(enrollment.progress_percentage)}`}
                          style={{ width: `${enrollment.progress_percentage}%` }}
                        />
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          <span>{enrollment.course?.estimated_duration_hours || 0} hours</span>
                        </div>
                        {enrollment.last_accessed && (
                          <div>
                            Last accessed: {formatDate(enrollment.last_accessed)}
                          </div>
                        )}
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/dashboard/courses/${enrollment.course_id}/learn`);
                        }}
                        className="btn-primary flex items-center gap-2"
                      >
                        <Play className="w-4 h-4" />
                        {enrollment.progress_percentage === 0 ? 'Start Learning' : 'Continue Learning'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
