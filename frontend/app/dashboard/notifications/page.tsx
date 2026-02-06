'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  getNotifications,
  getNotificationPreferences,
  updateNotificationPreferences,
  markNotificationsAsRead,
  deleteNotification,
  type Notification,
  type NotificationPreferences,
} from '@/lib/notification-service';

export default function NotificationsPage() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'unread' | 'settings'>('all');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  useEffect(() => {
    loadNotifications();
  }, [activeTab, offset]);

  useEffect(() => {
    if (activeTab === 'settings') {
      loadPreferences();
    }
  }, [activeTab]);

  async function loadNotifications() {
    try {
      setLoading(true);
      const data = await getNotifications(activeTab === 'unread', undefined, limit, offset);
      setNotifications(offset === 0 ? data.notifications : [...notifications, ...data.notifications]);
      setTotal(data.total);
      setHasMore(data.has_more);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadPreferences() {
    try {
      const data = await getNotificationPreferences();
      setPreferences(data);
    } catch (err) {
      console.error('Failed to load preferences:', err);
    }
  }

  async function handleMarkAsRead(notificationId: string) {
    try {
      await markNotificationsAsRead([notificationId]);
      setNotifications(notifications.map(n => 
        n.id === notificationId ? { ...n, is_read: true, read_at: new Date().toISOString() } : n
      ));
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  }

  async function handleDelete(notificationId: string) {
    try {
      await deleteNotification(notificationId);
      setNotifications(notifications.filter(n => n.id !== notificationId));
    } catch (err) {
      console.error('Failed to delete notification:', err);
    }
  }

  async function handleSavePreferences() {
    if (!preferences) return;
    
    try {
      setSaving(true);
      await updateNotificationPreferences(preferences);
    } catch (err) {
      console.error('Failed to save preferences:', err);
    } finally {
      setSaving(false);
    }
  }

  function getNotificationIcon(type: string) {
    switch (type) {
      case 'course_update':
      case 'new_enrollment':
        return '📚';
      case 'course_completion':
      case 'new_certificate':
        return '🎓';
      case 'new_review':
      case 'review_response':
        return '⭐';
      case 'discussion_reply':
        return '💬';
      case 'payment_success':
      case 'payout_approved':
      case 'payout_completed':
        return '💰';
      case 'achievement_unlocked':
        return '🏆';
      case 'system_announcement':
        return '📢';
      default:
        return '🔔';
    }
  }

  function getTimeAgo(dateString: string) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return date.toLocaleDateString();
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Notifications</h1>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => { setActiveTab('all'); setOffset(0); }}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'all'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                All
              </button>
              <button
                onClick={() => { setActiveTab('unread'); setOffset(0); }}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'unread'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Unread
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'settings'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Settings
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'settings' ? (
              /* Settings Tab */
              preferences && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Notifications</h3>
                    <div className="space-y-3">
                      {Object.entries(preferences)
                        .filter(([key]) => key.startsWith('email_'))
                        .map(([key, value]) => (
                          <label key={key} className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">
                              {key.replace('email_', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                            <input
                              type="checkbox"
                              checked={value as boolean}
                              onChange={(e) => setPreferences({ ...preferences, [key]: e.target.checked })}
                              className="h-4 w-4 text-blue-600 rounded"
                            />
                          </label>
                        ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">In-App Notifications</h3>
                    <div className="space-y-3">
                      {Object.entries(preferences)
                        .filter(([key]) => key.startsWith('inapp_'))
                        .map(([key, value]) => (
                          <label key={key} className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">
                              {key.replace('inapp_', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                            <input
                              type="checkbox"
                              checked={value as boolean}
                              onChange={(e) => setPreferences({ ...preferences, [key]: e.target.checked })}
                              className="h-4 w-4 text-blue-600 rounded"
                            />
                          </label>
                        ))}
                    </div>
                  </div>

                  <button
                    onClick={handleSavePreferences}
                    disabled={saving}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : 'Save Preferences'}
                  </button>
                </div>
              )
            ) : (
              /* Notifications List */
              <div className="space-y-4">
                {loading && notifications.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  </div>
                ) : notifications.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <svg className="mx-auto h-12 w-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                    <p className="text-sm">No notifications</p>
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`flex items-start space-x-4 p-4 rounded-lg border ${
                        !notification.is_read ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200'
                      }`}
                    >
                      <span className="text-3xl flex-shrink-0">{getNotificationIcon(notification.type)}</span>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm ${!notification.is_read ? 'font-semibold' : 'font-medium'} text-gray-900`}>
                          {notification.title}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          {notification.message}
                        </p>
                        <div className="flex items-center space-x-4 mt-2">
                          <p className="text-xs text-gray-500">
                            {getTimeAgo(notification.created_at)}
                          </p>
                          {!notification.is_read && (
                            <button
                              onClick={() => handleMarkAsRead(notification.id)}
                              className="text-xs text-blue-600 hover:text-blue-700"
                            >
                              Mark as read
                            </button>
                          )}
                          {notification.action_url && (
                            <Link
                              href={notification.action_url}
                              className="text-xs text-blue-600 hover:text-blue-700"
                            >
                              View
                            </Link>
                          )}
                          <button
                            onClick={() => handleDelete(notification.id)}
                            className="text-xs text-red-600 hover:text-red-700"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}

                {hasMore && (
                  <div className="text-center pt-4">
                    <button
                      onClick={() => setOffset(offset + limit)}
                      disabled={loading}
                      className="bg-gray-200 text-gray-900 px-6 py-2 rounded-lg font-semibold hover:bg-gray-300 disabled:opacity-50"
                    >
                      {loading ? 'Loading...' : 'Load More'}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
