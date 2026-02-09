'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  getLiveClasses,
  createLiveClass,
  startLiveClass,
  endLiveClass,
  deleteLiveClass,
  LiveClass,
  CreateLiveClass,
  formatSessionStatus,
} from '@/lib/live-class-service';
import { instructorCourseService } from '@/lib/instructor-course-service';
import { Plus, Edit, Trash2, Play, StopCircle, Video, Calendar, Clock, Users } from 'lucide-react';

export default function InstructorLiveClassesPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<LiveClass[]>([]);
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);

  const [formData, setFormData] = useState<CreateLiveClass>({
    course_id: '',
    title: '',
    description: '',
    scheduled_start: '',
    scheduled_end: '',
    max_participants: undefined,
    is_recorded: false,
  });

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      setError('');
      
      // Load all sessions (upcoming and past)
      const [upcomingData, pastData, coursesData] = await Promise.all([
        getLiveClasses({ upcoming: true, limit: 50 }),
        getLiveClasses({ upcoming: false, limit: 20 }),
        instructorCourseService.getMyCourses(),
      ]);
      
      setSessions([...upcomingData.sessions, ...pastData.sessions]);
      setCourses(coursesData || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate() {
    try {
      setCreating(true);
      setError('');
      
      await createLiveClass(formData);
      setShowCreateModal(false);
      setFormData({
        course_id: '',
        title: '',
        description: '',
        scheduled_start: '',
        scheduled_end: '',
        max_participants: undefined,
        is_recorded: false,
      });
      
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create session');
    } finally {
      setCreating(false);
    }
  }

  async function handleStart(sessionId: string) {
    const meetingUrl = prompt('Enter the meeting URL (Zoom, Google Meet, etc.):');
    if (!meetingUrl) return;

    try {
      await startLiveClass(sessionId, meetingUrl);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start session');
    }
  }

  async function handleEnd(sessionId: string) {
    if (!confirm('Are you sure you want to end this session?')) return;

    try {
      await endLiveClass(sessionId);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to end session');
    }
  }

  async function handleDelete(sessionId: string) {
    if (!confirm('Are you sure you want to delete this session?')) return;

    try {
      await deleteLiveClass(sessionId);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete session');
    }
  }

  function formatDateTime(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Manage Live Classes</h1>
            <p className="text-gray-600">Schedule and manage live sessions for your courses</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            <Plus className="h-5 w-5" />
            Schedule Session
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading sessions...</p>
          </div>
        ) : sessions.length === 0 ? (
          /* Empty State */
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <Video className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Live Sessions</h3>
            <p className="text-gray-500 mb-6">Get started by scheduling your first live class</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Plus className="h-5 w-5" />
              Schedule Session
            </button>
          </div>
        ) : (
          /* Session List */
          <div className="space-y-4">
            {sessions.map((session) => {
              const status = formatSessionStatus(session);
              const isLive = session.status === 'live' || status.label === 'Live Now';
              const canStart = session.status === 'scheduled' && new Date(session.scheduled_start) <= new Date();

              return (
                <div
                  key={session.id}
                  className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{session.title}</h3>
                        <span className={`text-sm font-medium ${status.color}`}>
                          {status.label}
                        </span>
                      </div>

                      {session.description && (
                        <p className="text-gray-600 mb-4">{session.description}</p>
                      )}

                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          {formatDateTime(session.scheduled_start)}
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4" />
                          {formatDateTime(session.scheduled_end)}
                        </div>
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4" />
                          {session.current_participants}
                          {session.max_participants && ` / ${session.max_participants}`}
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="ml-6 flex gap-2">
                      {canStart && (
                        <button
                          onClick={() => handleStart(session.id)}
                          className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                          title="Start Session"
                        >
                          <Play className="h-4 w-4" />
                          Start
                        </button>
                      )}
                      {isLive && (
                        <button
                          onClick={() => handleEnd(session.id)}
                          className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                          title="End Session"
                        >
                          <StopCircle className="h-4 w-4" />
                          End
                        </button>
                      )}
                      <button
                        onClick={() => router.push(`/dashboard/live-classes/${session.id}`)}
                        className="flex items-center gap-2 text-blue-600 hover:text-blue-700 px-4 py-2"
                        title="View Details"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(session.id)}
                        className="flex items-center gap-2 text-red-600 hover:text-red-700 px-4 py-2"
                        title="Delete Session"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Schedule Live Class</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Course *
                  </label>
                  <select
                    value={formData.course_id}
                    onChange={(e) => setFormData({ ...formData, course_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select a course</option>
                    {courses.map((course) => (
                      <option key={course.id} value={course.id}>
                        {course.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Week 3: Advanced Concepts"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Optional session description"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Start Time *
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.scheduled_start}
                      onChange={(e) => setFormData({ ...formData, scheduled_start: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      End Time *
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.scheduled_end}
                      onChange={(e) => setFormData({ ...formData, scheduled_end: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Participants (Optional)
                  </label>
                  <input
                    type="number"
                    value={formData.max_participants || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        max_participants: e.target.value ? parseInt(e.target.value) : undefined,
                      })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Leave empty for unlimited"
                    min="1"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_recorded"
                    checked={formData.is_recorded}
                    onChange={(e) => setFormData({ ...formData, is_recorded: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="is_recorded" className="text-sm text-gray-700">
                    Record this session
                  </label>
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <button
                  onClick={handleCreate}
                  disabled={creating || !formData.course_id || !formData.title || !formData.scheduled_start || !formData.scheduled_end}
                  className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {creating ? 'Creating...' : 'Schedule Session'}
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
