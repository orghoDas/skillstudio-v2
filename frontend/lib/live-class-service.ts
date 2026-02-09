/**
 * Live Class Service
 * Handles live class scheduling, joining, and management
 */

import api from './api';

export interface LiveClass {
  id: string;
  course_id: string;
  instructor_id: string;
  title: string;
  description?: string;
  scheduled_start: string;
  scheduled_end: string;
  actual_start?: string;
  actual_end?: string;
  meeting_url?: string;
  meeting_id?: string;
  meeting_password?: string;
  recording_url?: string;
  is_recorded: boolean;
  max_participants?: number;
  current_participants: number;
  chat_room_id?: string;
  status: 'scheduled' | 'live' | 'ended' | 'cancelled';
  metadata: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface CreateLiveClass {
  course_id: string;
  title: string;
  description?: string;
  scheduled_start: string;
  scheduled_end: string;
  max_participants?: number;
  is_recorded?: boolean;
  metadata?: Record<string, any>;
}

export interface UpdateLiveClass {
  title?: string;
  description?: string;
  scheduled_start?: string;
  scheduled_end?: string;
  max_participants?: number;
  is_recorded?: boolean;
  meeting_url?: string;
  recording_url?: string;
}

export interface Attendee {
  id: string;
  session_id: string;
  user_id: string;
  joined_at?: string;
  left_at?: string;
  duration_minutes: number;
  questions_asked: number;
  is_hand_raised: boolean;
  is_muted: boolean;
  created_at: string;
}

export interface JoinSessionResponse {
  session: LiveClass;
  meeting_url?: string;
  chat_room_id?: string;
}

/**
 * Create/schedule a new live class (Instructor only)
 */
export async function createLiveClass(data: CreateLiveClass): Promise<LiveClass> {
  const response = await api.post('/live-classes', data);
  return response.data;
}

/**
 * Get list of live class sessions
 */
export async function getLiveClasses(params?: {
  course_id?: string;
  upcoming?: boolean;
  skip?: number;
  limit?: number;
}): Promise<{ sessions: LiveClass[]; total: number; skip: number; limit: number }> {
  const response = await api.get('/live-classes', { params });
  return response.data;
}

/**
 * Get details of a specific live class session
 */
export async function getLiveClass(sessionId: string): Promise<LiveClass> {
  const response = await api.get(`/live-classes/${sessionId}`);
  return response.data;
}

/**
 * Update a live class session (Instructor only)
 */
export async function updateLiveClass(
  sessionId: string,
  data: UpdateLiveClass
): Promise<LiveClass> {
  const response = await api.put(`/live-classes/${sessionId}`, data);
  return response.data;
}

/**
 * Start a live class session (Instructor only)
 */
export async function startLiveClass(
  sessionId: string,
  meetingUrl: string
): Promise<LiveClass> {
  const response = await api.post(`/live-classes/${sessionId}/start`, null, {
    params: { meeting_url: meetingUrl },
  });
  return response.data;
}

/**
 * Join a live class session
 */
export async function joinLiveClass(sessionId: string): Promise<JoinSessionResponse> {
  const response = await api.post(`/live-classes/${sessionId}/join`);
  return response.data;
}

/**
 * Leave a live class session
 */
export async function leaveLiveClass(sessionId: string): Promise<{ message: string }> {
  const response = await api.post(`/live-classes/${sessionId}/leave`);
  return response.data;
}

/**
 * End a live class session (Instructor only)
 */
export async function endLiveClass(sessionId: string): Promise<LiveClass> {
  const response = await api.post(`/live-classes/${sessionId}/end`);
  return response.data;
}

/**
 * Get attendees of a live class session
 */
export async function getLiveClassAttendees(sessionId: string): Promise<Attendee[]> {
  const response = await api.get(`/live-classes/${sessionId}/attendees`);
  return response.data;
}

/**
 * Delete a live class session (Instructor only)
 */
export async function deleteLiveClass(sessionId: string): Promise<void> {
  await api.delete(`/live-classes/${sessionId}`);
}

/**
 * Format session status for display
 */
export function formatSessionStatus(session: LiveClass): {
  label: string;
  color: string;
} {
  const now = new Date();
  const start = new Date(session.scheduled_start);
  const end = new Date(session.scheduled_end);

  if (session.status === 'cancelled') {
    return { label: 'Cancelled', color: 'text-gray-500' };
  }

  if (session.status === 'ended' || (session.actual_end && now > new Date(session.actual_end))) {
    return { label: 'Ended', color: 'text-gray-600' };
  }

  if (session.status === 'live' || (session.actual_start && !session.actual_end)) {
    return { label: 'Live Now', color: 'text-red-600 font-bold' };
  }

  if (now >= start && now <= end) {
    return { label: 'In Progress', color: 'text-green-600' };
  }

  if (now < start) {
    return { label: 'Upcoming', color: 'text-blue-600' };
  }

  return { label: 'Past', color: 'text-gray-500' };
}

/**
 * Check if user can join session
 */
export function canJoinSession(session: LiveClass): boolean {
  const now = new Date();
  const start = new Date(session.scheduled_start);
  const end = new Date(session.scheduled_end);

  // Can join 10 minutes before start time until session ends
  const joinWindow = new Date(start.getTime() - 10 * 60 * 1000);

  return (
    session.status !== 'cancelled' &&
    session.status !== 'ended' &&
    now >= joinWindow &&
    now <= end &&
    session.meeting_url !== null
  );
}
