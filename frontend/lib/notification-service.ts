import api from './api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper to get auth token
const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

// Types
export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  course_id?: string;
  enrollment_id?: string;
  payment_id?: string;
  discussion_id?: string;
  metadata: Record<string, any>;
  action_url?: string;
  is_read: boolean;
  read_at?: string;
  created_at: string;
}

export interface NotificationPreferences {
  id: string;
  user_id: string;
  email_course_updates: boolean;
  email_new_enrollments: boolean;
  email_course_completions: boolean;
  email_new_reviews: boolean;
  email_discussion_replies: boolean;
  email_payment_updates: boolean;
  email_payout_updates: boolean;
  email_marketing: boolean;
  inapp_course_updates: boolean;
  inapp_new_enrollments: boolean;
  inapp_course_completions: boolean;
  inapp_new_reviews: boolean;
  inapp_discussion_replies: boolean;
  inapp_payment_updates: boolean;
  inapp_payout_updates: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  total: number;
  unread_count: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// API Functions

export async function getNotifications(
  unreadOnly: boolean = false,
  type?: string,
  limit: number = 20,
  offset: number = 0
): Promise<NotificationsResponse> {
  const token = getAuthToken();
  const params = new URLSearchParams();
  
  params.append('unread_only', unreadOnly.toString());
  if (type) params.append('type', type);
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());
  
  const response = await fetch(`${API_BASE_URL}/api/notifications/?${params.toString()}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch notifications');
  }
  
  return response.json();
}

export async function markNotificationsAsRead(notificationIds: string[]): Promise<{ updated_count: number }> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/notifications/mark-as-read`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ notification_ids: notificationIds }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to mark notifications as read');
  }
  
  return response.json();
}

export async function markAllNotificationsAsRead(): Promise<{ updated_count: number }> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/notifications/mark-all-as-read`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to mark all notifications as read');
  }
  
  return response.json();
}

export async function deleteNotification(notificationId: string): Promise<{ message: string }> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/notifications/${notificationId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete notification');
  }
  
  return response.json();
}

export async function getNotificationPreferences(): Promise<NotificationPreferences> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/notifications/preferences`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch notification preferences');
  }
  
  return response.json();
}

export async function updateNotificationPreferences(
  preferences: Partial<NotificationPreferences>
): Promise<NotificationPreferences> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/notifications/preferences`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(preferences),
  });
  
  if (!response.ok) {
    throw new Error('Failed to update notification preferences');
  }
  
  return response.json();
}
