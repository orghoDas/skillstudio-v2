'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import { courseService, Course } from '@/lib/course-service';
import { 
  BookOpen, 
  Clock, 
  TrendingUp, 
  Search,
  Users,
  Award,
  Filter,
  Loader2,
  AlertCircle,
  ArrowRight
} from 'lucide-react';

export default function CoursesPage() {
  const router = useRouter();
  const [courses, setCourses] = useState<Course[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadCourses();
  }, [router]);

  useEffect(() => {
    filterCourses();
  }, [searchTerm, difficultyFilter, courses]);

  const loadCourses = async () => {
    try {
      setError(null);
      setLoading(true);
      const data = await courseService.listCourses({ published_only: true, limit: 100 });
      setCourses(data);
      setFilteredCourses(data);
    } catch (error: any) {
      console.error('Failed to load courses:', error);
      setError(error.message || 'Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const filterCourses = () => {
    let filtered = [...courses];

    // Filter by difficulty
    if (difficultyFilter !== 'all') {
      filtered = filtered.filter(c => c.difficulty_level === difficultyFilter);
    }

    // Filter by search term
    if (searchTerm) {
      const query = searchTerm.toLowerCase();
      filtered = filtered.filter(c =>
        c.title.toLowerCase().includes(query) ||
        c.description?.toLowerCase().includes(query) ||
        c.skills_taught.some(s => s.toLowerCase().includes(query))
      );
    }

    setFilteredCourses(filtered);
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

  if (error) {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to Load Courses</h3>
              <p className="text-red-700 mb-4">{error}</p>
              <button onClick={loadCourses} className="btn-primary">
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
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-xl">
              <BookOpen className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Course Catalog</h1>
              <p className="text-gray-600">{filteredCourses.length} courses available</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-8 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search courses by title, description, or skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-12"
          />
        </div>

        {/* Difficulty Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Difficulty:</span>
          <div className="flex gap-2">
            {['all', 'beginner', 'intermediate', 'advanced'].map((level) => (
              <button
                key={level}
                onClick={() => setDifficultyFilter(level)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  difficultyFilter === level
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Course Grid */}
      {filteredCourses.length === 0 ? (
        <div className="text-center py-16">
          <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Courses Found</h3>
          <p className="text-gray-600 mb-6">
            {searchTerm || difficultyFilter !== 'all'
              ? 'Try adjusting your search or filters'
              : 'No courses available at the moment'}
          </p>
          {(searchTerm || difficultyFilter !== 'all') && (
            <button
              onClick={() => {
                setSearchTerm('');
                setDifficultyFilter('all');
              }}
              className="btn-primary"
            >
              Clear Filters
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <div
              key={course.id}
              className="card hover:shadow-lg transition-all duration-300 cursor-pointer"
              onClick={() => router.push(`/dashboard/courses/${course.id}`)}
            >
              {/* Thumbnail */}
              {course.thumbnail_url ? (
                <div className="h-48 bg-gray-200 rounded-lg mb-4 overflow-hidden">
                  <img
                    src={course.thumbnail_url}
                    alt={course.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              ) : (
                <div className="h-48 bg-gradient-to-br from-primary-100 to-purple-100 rounded-lg mb-4 flex items-center justify-center">
                  <BookOpen className="w-16 h-16 text-primary-600 opacity-50" />
                </div>
              )}

              {/* Difficulty Badge */}
              <span className={`inline-block px-3 py-1 rounded-lg text-xs font-medium border mb-3 ${getDifficultyColor(course.difficulty_level)}`}>
                {course.difficulty_level.charAt(0).toUpperCase() + course.difficulty_level.slice(1)}
              </span>

              {/* Title */}
              <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2">
                {String(course.title)}
              </h3>

              {/* Description */}
              <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                {String(course.short_description || course.description || '')}
              </p>

              {/* Stats */}
              <div className="flex items-center gap-4 mb-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{course.estimated_duration_hours}h</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  <span>{course.total_enrollments}</span>
                </div>
              </div>

              {/* Skills */}
              {course.skills_taught && course.skills_taught.length > 0 && (
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {course.skills_taught.slice(0, 3).map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded"
                      >
                        {typeof skill === 'string' ? skill : String(skill)}
                      </span>
                    ))}
                    {course.skills_taught.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        +{course.skills_taught.length - 3}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Action Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  router.push(`/dashboard/courses/${course.id}`);
                }}
                className="btn-primary w-full text-sm flex items-center justify-center gap-2"
              >
                View Course
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
