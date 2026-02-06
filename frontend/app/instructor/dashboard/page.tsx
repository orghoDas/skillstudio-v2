'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { BookOpen, Users, TrendingUp, DollarSign, Eye, Clock, Star } from 'lucide-react';
import { instructorService, InstructorStats, CourseStats } from '@/lib/instructor-service';

export default function InstructorDashboard() {
  const [stats, setStats] = useState<InstructorStats | null>(null);
  const [courseStats, setCourseStats] = useState<CourseStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, coursesData] = await Promise.all([
        instructorService.getStats(),
        instructorService.getCoursesStats(),
      ]);
      setStats(statsData);
      setCourseStats(coursesData);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const statCards = [
    {
      name: 'Total Courses',
      value: stats?.total_courses || 0,
      icon: BookOpen,
      color: 'bg-blue-500',
      subtitle: `${stats?.published_courses || 0} published`,
    },
    {
      name: 'Total Students',
      value: stats?.total_students || 0,
      icon: Users,
      color: 'bg-green-500',
      subtitle: `${stats?.total_enrollments || 0} enrollments`,
    },
    {
      name: 'Avg Rating',
      value: stats?.average_course_rating ? stats.average_course_rating.toFixed(1) : '0.0',
      icon: Star,
      color: 'bg-yellow-500',
      subtitle: 'across all courses',
    },
    {
      name: 'Revenue',
      value: '$0',
      icon: DollarSign,
      color: 'bg-purple-500',
      subtitle: 'Coming soon',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Welcome back!</h2>
        <p className="text-gray-600 mt-1">
          Here's what's happening with your courses today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stat.value}
                </p>
                <p className="text-xs text-gray-500 mt-1">{stat.subtitle}</p>
              </div>
              <div className={`p-3 ${stat.color} rounded-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/instructor/courses/create"
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
          >
            <BookOpen className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="font-medium text-gray-700">Create New Course</p>
          </Link>
          <Link
            href="/instructor/courses"
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
          >
            <Clock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="font-medium text-gray-700">Manage Courses</p>
          </Link>
          <Link
            href="/instructor/students"
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
          >
            <Users className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="font-medium text-gray-700">View Students</p>
          </Link>
        </div>
      </div>

      {/* Course Performance */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Course Performance</h3>
          <Link
            href="/instructor/courses"
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View all
          </Link>
        </div>

        {courseStats.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              No courses yet
            </h4>
            <p className="text-gray-600 mb-6">
              Get started by creating your first course
            </p>
            <Link
              href="/instructor/courses/create"
              className="btn-primary inline-flex items-center gap-2"
            >
              <BookOpen className="w-5 h-5" />
              Create Your First Course
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Course
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Enrollments
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Active Students
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Completion
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Rating
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {courseStats.slice(0, 5).map((course) => (
                  <tr key={course.course_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <Link
                        href={`/instructor/courses/${course.course_id}/edit`}
                        className="font-medium text-gray-900 hover:text-primary-600"
                      >
                        {course.course_title}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {course.total_enrollments}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {course.active_students}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${course.completion_rate}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600">
                          {course.completion_rate.toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1 text-gray-600">
                        <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                        {course.average_rating.toFixed(1)}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
