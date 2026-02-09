'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  getLiveClass,
  joinLiveClass,
  leaveLiveClass,
  getLiveClassAttendees,
  LiveClass,
  Attendee,
  formatSessionStatus,
  canJoinSession,
} from '@/lib/live-class-service';
import { Video, Calendar, Clock, Users, ExternalLink, MessageCircle, ArrowLeft } from 'lucide-react';

export default function LiveClassDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;

  const [session, setSession] = useState<LiveClass | null>(null);
  const [attendees, setAttendees] = useState<Attendee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [joining, setJoining] = useState(false);
  const [hasJoined, setHasJoined] = useState(false);

  useEffect(() => {
    if (sessionId) {
      loadSession();
    }
  }, [sessionId]);

  async function loadSession() {
    try {
      setLoading(true);
      setError('');
      
      const sessionData = await getLiveClass(sessionId);
      setSession(sessionData);
      
      // Load attendees
      const attendeesData = await getLiveClassAttendees(sessionId);
      setAttendees(attendeesData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load session details');
    } finally {
      setLoading(false);
    }
  }

  async function handleJoinSession() {
    if (!session) return;

    try {
      setJoining(true);
      setError('');
      
      const joinData = await joinLiveClass(sessionId);
      setHasJoined(true);
      
      // If there's a meeting URL, open it in a new tab
      if (joinData.meeting_url) {
        window.open(joinData.meeting_url, '_blank');
      }
      
      // Reload session to update participant count
      await loadSession();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join session');
    } finally {
      setJoining(false);
    }
  }

  async function handleLeaveSession() {
    try {
      await leaveLiveClass(sessionId);
      setHasJoined(false);
      await loadSession();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to leave session');
    }
  }

  function formatDate(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
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
    if (minutes < 60) return `${minutes} minutes`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours} hour${hours > 1 ? 's' : ''} ${remainingMinutes} minutes` : `${hours} hour${hours > 1 ? 's' : ''}`;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading session...</p>
        </div>
      </div>
    );
  }

  if (error && !session) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!session) return null;

  const status = formatSessionStatus(session);
  const canJoin = canJoinSession(session);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => router.push('/dashboard/live-classes')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 font-medium"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Live Classes
        </button>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-8">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <h1 className="text-2xl font-bold">{session.title}</h1>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    status.label === 'Live Now' ? 'bg-red-500' :
                    status.label === 'Upcoming' ? 'bg-green-500' :
                    'bg-gray-500'
                  }`}>
                    {status.label}
                  </span>
                </div>
                {session.description && (
                  <p className="text-blue-100 text-lg">{session.description}</p>
                )}
              </div>
            </div>
          </div>

          {/* Session Details */}
          <div className="p-8">
            {/* Error Message */}
            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            {/* Info Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-500">Date</p>
                  <p className="text-gray-900 font-medium">{formatDate(session.scheduled_start)}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-500">Time</p>
                  <p className="text-gray-900 font-medium">
                    {formatTime(session.scheduled_start)} - {formatTime(session.scheduled_end)}
                  </p>
                  <p className="text-sm text-gray-500">
                    Duration: {getDuration(session.scheduled_start, session.scheduled_end)}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Users className="h-5 w-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-500">Participants</p>
                  <p className="text-gray-900 font-medium">
                    {session.current_participants}
                    {session.max_participants && ` / ${session.max_participants}`}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Video className="h-5 w-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-500">Recording</p>
                  <p className="text-gray-900 font-medium">
                    {session.is_recorded ? 'Session will be recorded' : 'Not recorded'}
                  </p>
                </div>
              </div>
            </div>

            {/* Recording Link */}
            {session.recording_url && (
              <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <p className="text-sm text-purple-900 mb-2 font-medium">Recording Available</p>
                <a
                  href={session.recording_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-purple-600 hover:text-purple-700 flex items-center gap-2 font-medium"
                >
                  <ExternalLink className="h-4 w-4" />
                  Watch Recording
                </a>
              </div>
            )}

            {/* Join Button */}
            {canJoin && (
              <div className="mb-6">
                {!hasJoined ? (
                  <button
                    onClick={handleJoinSession}
                    disabled={joining}
                    className={`w-full bg-blue-600 text-white px-6 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg ${
                      joining ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {joining ? 'Joining...' : 'Join Live Class Now'}
                  </button>
                ) : (
                  <div className="space-y-3">
                    <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
                      ✓ You have joined this session
                    </div>
                    {session.meeting_url && (
                      <a
                        href={session.meeting_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full bg-blue-600 text-white px-6 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg text-center"
                      >
                        Open Meeting Room
                      </a>
                    )}
                    <button
                      onClick={handleLeaveSession}
                      className="w-full text-red-600 hover:text-red-700 font-medium"
                    >
                      Leave Session
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Chat Room Link */}
            {session.chat_room_id && (
              <div className="mb-6">
                <button
                  onClick={() => router.push(`/dashboard/chat?room=${session.chat_room_id}`)}
                  className="w-full flex items-center justify-center gap-2 border border-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  <MessageCircle className="h-5 w-5" />
                  Open Session Chat
                </button>
              </div>
            )}

            {/* Attendees List */}
            {attendees.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Attendees ({attendees.length})
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {attendees.slice(0, 12).map((attendee) => (
                    <div
                      key={attendee.id}
                      className="flex items-center gap-2 p-2 bg-gray-50 rounded"
                    >
                      <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                        {attendee.user_id.substring(0, 2).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900 truncate">Attendee</p>
                        {attendee.joined_at && (
                          <p className="text-xs text-gray-500">
                            {attendee.duration_minutes > 0 && `${attendee.duration_minutes} min`}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                {attendees.length > 12 && (
                  <p className="text-sm text-gray-500 mt-3">
                    +{attendees.length - 12} more attendees
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
