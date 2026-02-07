/**
 * Admin Analytics Service
 * Handles platform-wide analytics and metrics for administrators
 */

import api from './api';

export interface PlatformOverview {
  total_users: number;
  total_learners: number;
  total_instructors: number;
  total_courses: number;
  total_enrollments: number;
  total_revenue: number;
  active_subscriptions: number;
  avg_courses_per_instructor: number;
}

export interface UserGrowthMetrics {
  new_users: number;
  growth_rate: number;
  daily_signups: Array<{ date: string; count: number }>;
}

export interface EngagementMetrics {
  dau: number;
  mau: number;
  wau: number;
  dau_mau_ratio: number;
  avg_session_duration_minutes: number;
  course_completion_rate: number;
}

export interface RevenueMetrics {
  period_revenue: number;
  mrr: number;
  avg_transaction_value: number;
  daily_revenue: Array<{ date: string; amount: number }>;
}

export interface TopCourse {
  course_id: string;
  title: string;
  enrollments: number;
  revenue: number;
  avg_rating: number;
}

export interface TopInstructor {
  instructor_id: string;
  name: string;
  total_students: number;
  total_earnings: number;
  courses_count: number;
}

export interface DashboardData {
  overview: PlatformOverview;
  user_growth: UserGrowthMetrics;
  engagement: EngagementMetrics;
  revenue: RevenueMetrics;
  top_courses: TopCourse[];
  top_instructors: TopInstructor[];
}

/**
 * Get platform overview statistics
 */
export async function getPlatformOverview(): Promise<PlatformOverview> {
  const response = await api.get('/admin/analytics/overview');
  return response.data;
}

/**
 * Get user growth metrics
 */
export async function getUserGrowth(days: number = 30): Promise<UserGrowthMetrics> {
  const response = await api.get('/admin/analytics/user-growth', {
    params: { days }
  });
  return response.data;
}

/**
 * Get engagement metrics
 */
export async function getEngagementMetrics(days: number = 30): Promise<EngagementMetrics> {
  const response = await api.get('/admin/analytics/engagement', {
    params: { days }
  });
  return response.data;
}

/**
 * Get revenue metrics
 */
export async function getRevenueMetrics(days: number = 30): Promise<RevenueMetrics> {
  const response = await api.get('/admin/analytics/revenue', {
    params: { days }
  });
  return response.data;
}

/**
 * Get top performing courses
 */
export async function getTopCourses(
  metric: 'enrollments' | 'revenue' | 'rating' = 'enrollments',
  limit: number = 10
): Promise<TopCourse[]> {
  const response = await api.get('/admin/analytics/top-courses', {
    params: { metric, limit }
  });
  return response.data;
}

/**
 * Get top instructors
 */
export async function getTopInstructors(limit: number = 10): Promise<TopInstructor[]> {
  const response = await api.get('/admin/analytics/top-instructors', {
    params: { limit }
  });
  return response.data;
}

/**
 * Get complete dashboard data (all metrics in one call)
 */
export async function getDashboardData(days: number = 30): Promise<DashboardData> {
  const response = await api.get('/admin/analytics/dashboard', {
    params: { days }
  });
  return response.data;
}

/**
 * Manually trigger daily metrics aggregation (admin only)
 */
export async function aggregateDailyMetrics(date?: string): Promise<{ success: boolean }> {
  const endpoint = date 
    ? `/admin/analytics/aggregate/${date}`
    : '/admin/analytics/aggregate';
  const response = await api.post(endpoint);
  return response.data;
}

export default {
  getPlatformOverview,
  getUserGrowth,
  getEngagementMetrics,
  getRevenueMetrics,
  getTopCourses,
  getTopInstructors,
  getDashboardData,
  aggregateDailyMetrics
};
