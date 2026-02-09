'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getLiveClasses, LiveClass, formatSessionStatus, canJoinSession } from '@/lib/live-class-service';
import { Video, Calendar, Clock, Users, ExternalLink } from 'lucide-react';

export default function LiveClassesPage() {
  const router = useRouter();
  const [upcomingSessions, setUpcomingSessions] = useState<LiveClass[]>([]);
  const [pastSessions, setPastSessions] = useState<LiveClass[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming');

  useEffect(() => {
    loadSessions();
  }, []);

  async function loadSessions() {
    try {
      setLoading(true);
      setError('');
      
      // Load upcoming sessions
      const upcomingData = await getLiveClasses({ upcoming: true, limit: 50 });
      setUpcomingSessions(upcomingData.sessions);
      
      // Load past sessions
      const pastData = await getLiveClasses({ upcoming: false, limit: 20 });
      setPastSessions(pastData.sessions);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load live classes');
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }

  function formatTime(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    });
  }

  function getDuration(start: string, end: string) {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const minutes = Math.round((endDate.getTime() - startDate.getTime()) / (1000 * 60));
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  }

  const sessions = activeTab === 'upcoming' ? upcomingSessions : pastSessions;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Live Classes</h1>
          <p className="text-gray-600">Join scheduled live sessions and webinars</p>
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('upcoming')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'upcoming'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Upcoming ({upcomingSessions.length})
            </button>
            <button
              onClick={() => setActiveTab('past')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'past'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Past ({pastSessions.length})
            </button>
          </nav>
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
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {activeTab === 'upcoming' ? 'No Upcoming Sessions' : 'No Past Sessions'}
            </h3>
            <p className="text-gray-500">
              {activeTab === 'upcoming'
                ? 'Check back later for scheduled live classes'
                : 'You haven\'t attended any live classes yet'}
            </p>
          </div>
        ) : (
          /* Session List */
          <div className="space-y-4">
            {sessions.map((session) => {
              const status = formatSessionStatus(session);
              const canJoin = canJoinSession(session);

              return (
                <div
                  key={session.id}
                  className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Title and Status */}
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {session.title}
                        </h3>
                        <span className={`text-sm font-medium ${status.color}`}>
                          {status.label}
                        </span>
                        {session.is_recorded && (
                          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                            Recorded
                          </span>
                        )}
                      </div>

                      {/* Description */}
                      {session.description && (
                        <p className="text-gray-600 mb-4">{session.description}</p>
                      )}

                      {/* Session Details */}
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          {formatDate(session.scheduled_start)}
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4" />
                          {formatTime(session.scheduled_start)} - {formatTime(session.scheduled_end)}
                          <span className="text-gray-400">
                            ({getDuration(session.scheduled_start, session.scheduled_end)})
                          </span>
                        </div>
                        {session.max_participants && (
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            {session.current_participants}/{session.max_participants} participants
                          </div>
                        )}
                      </div>

                      {/* Recording Link for Past Sessions */}
                      {session.recording_url && activeTab === 'past' && (
                        <div className="mt-4">
                          <a
                            href={session.recording_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-2"
                          >
                            <ExternalLink className="h-4 w-4" />
                            View Recording
                          </a>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="ml-6 flex flex-col gap-2">
                      {canJoin && (
                        <button
                          onClick={() => router.push(`/dashboard/live-classes/${session.id}`)}
                          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                        >
                          Join Session
                        </button>
                      )}
                      <button
                        onClick={() => router.push(`/dashboard/live-classes/${session.id}`)}
                        className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
