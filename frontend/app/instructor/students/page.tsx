'use client';

import { useEffect, useState } from 'react';
import { Users, Search, Filter, Mail, BookOpen, Calendar, TrendingUp } from 'lucide-react';
import { instructorService, StudentEnrollment, CourseStats } from '@/lib/instructor-service';

export default function InstructorStudentsPage() {
  const [students, setStudents] = useState<StudentEnrollment[]>([]);
  const [courses, setCourses] = useState<CourseStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCourse, setSelectedCourse] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedCourse && selectedCourse !== 'all') {
      fetchStudents(selectedCourse);
    } else {
      fetchStudents();
    }
  }, [selectedCourse]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [studentsData, coursesData] = await Promise.all([
        instructorService.getStudents(),
        instructorService.getCoursesStats(),
      ]);
      setStudents(studentsData);
      setCourses(coursesData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async (courseId?: string) => {
    try {
      const studentsData = await instructorService.getStudents(courseId);
      setStudents(studentsData);
    } catch (error) {
      console.error('Failed to fetch students:', error);
    }
  };

  const filteredStudents = students.filter((student) => {
    const matchesSearch =
      student.student_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student.student_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student.course_title.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesSearch;
  });

  const uniqueStudents = Array.from(
    new Map(filteredStudents.map((s) => [s.student_id, s])).values()
  );

  const totalStudents = uniqueStudents.length;
  const totalEnrollments = filteredStudents.length;
  const averageProgress =
    filteredStudents.length > 0
      ? filteredStudents.reduce((sum, s) => sum + s.progress_percentage, 0) /
        filteredStudents.length
      : 0;
  const completedEnrollments = filteredStudents.filter((s) => s.completed).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Students</h1>
        <p className="text-gray-600 mt-1">
          Monitor and engage with your student community
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Students</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {totalStudents}
              </p>
            </div>
            <div className="p-3 bg-blue-500 rounded-lg">
              <Users className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Enrollments</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {totalEnrollments}
              </p>
            </div>
            <div className="p-3 bg-green-500 rounded-lg">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Progress</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {averageProgress.toFixed(0)}%
              </p>
            </div>
            <div className="p-3 bg-purple-500 rounded-lg">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {completedEnrollments}
              </p>
            </div>
            <div className="p-3 bg-yellow-500 rounded-lg">
              <Calendar className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search students..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10 w-full"
            />
          </div>

          {/* Course Filter */}
          <div className="sm:w-64">
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="input w-full"
            >
              <option value="all">All Courses</option>
              {courses.map((course) => (
                <option key={course.course_id} value={course.course_id}>
                  {course.course_title}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Students List */}
      <div className="card">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : filteredStudents.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {searchQuery || selectedCourse !== 'all'
                ? 'No students found'
                : 'No students yet'}
            </h3>
            <p className="text-gray-600">
              {searchQuery || selectedCourse !== 'all'
                ? 'Try adjusting your search or filter'
                : 'Students will appear here once they enroll in your courses'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Student
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Course
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Enrolled
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Progress
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Last Active
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredStudents.map((student) => (
                  <tr key={`${student.student_id}-${student.course_id}`} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <div>
                        <div className="font-medium text-gray-900">
                          {student.student_name}
                        </div>
                        <div className="text-sm text-gray-500 flex items-center gap-1">
                          <Mail className="w-3 h-3" />
                          {student.student_email}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-gray-900">{student.course_title}</div>
                    </td>
                    <td className="px-4 py-4 text-gray-600">
                      {new Date(student.enrolled_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                          <div
                            className="bg-primary-500 h-2 rounded-full"
                            style={{ width: `${student.progress_percentage}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600 min-w-[40px]">
                          {student.progress_percentage.toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      {student.completed ? (
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">
                          Completed
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                          In Progress
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-4 text-gray-600 text-sm">
                      {student.last_accessed
                        ? new Date(student.last_accessed).toLocaleDateString()
                        : 'Never'}
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
