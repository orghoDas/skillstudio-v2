/**
 * Gamification Service
 * Handles XP, achievements, leaderboards, and user stats
 */

import api from './api';

export interface UserStats {
  user_id: string;
  level: number;
  total_xp: number;
  xp_for_next_level: number;
  current_streak_days: number;
  longest_streak_days: number;
  courses_completed: number;
  lessons_completed: number;
  quizzes_completed: number;
  total_study_time_minutes: number;
  achievements_unlocked: number;
  rank_position?: number;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  category: 'learning' | 'social' | 'completion' | 'streak' | 'mastery';
  requirement_type: string;
  requirement_value: number;
  points: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  icon_url?: string;
  badge_color?: string;
  is_active: boolean;
}

export interface UserAchievement {
  id: string;
  user_id: string;
  achievement_id: string;
  unlocked_at: string;
  achievement: Achievement;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  level: number;
  total_xp: number;
  courses_completed: number;
  current_streak_days: number;
}

/**
 * Get current user's gamification stats
 */
export async function getMyStats(): Promise<UserStats> {
  const response = await api.get('/gamification/stats');
  return response.data;
}

/**
 * Get another user's public stats
 */
export async function getUserStats(userId: string): Promise<UserStats> {
  const response = await api.get(`/gamification/stats/${userId}`);
  return response.data;
}

/**
 * Get current user's achievements
 */
export async function getMyAchievements(): Promise<UserAchievement[]> {
  const response = await api.get('/gamification/achievements');
  return response.data;
}

/**
 * Get another user's achievements
 */
export async function getUserAchievements(userId: string): Promise<UserAchievement[]> {
  const response = await api.get(`/gamification/achievements/${userId}`);
  return response.data;
}

/**
 * Manually check and unlock achievements (force refresh)
 */
export async function checkAchievements(): Promise<{ unlocked: UserAchievement[] }> {
  const response = await api.post('/gamification/achievements/check');
  return response.data;
}

/**
 * Get leaderboard
 */
export async function getLeaderboard(
  timeframe: 'all_time' | 'monthly' | 'weekly' = 'all_time',
  limit: number = 100
): Promise<LeaderboardEntry[]> {
  const response = await api.get('/gamification/leaderboard', {
    params: { timeframe, limit }
  });
  return response.data;
}

/**
 * Update daily streak
 */
export async function updateStreak(): Promise<{ current_streak: number; xp_awarded: number }> {
  const response = await api.post('/gamification/streak/update');
  return response.data;
}

// Admin functions
export async function createAchievement(data: {
  name: string;
  description: string;
  category: string;
  requirement_type: string;
  requirement_value: number;
  points?: number;
  rarity?: string;
  icon_url?: string;
  badge_color?: string;
}): Promise<Achievement> {
  const response = await api.post('/gamification/admin/achievement/create', data);
  return response.data;
}

export async function seedDefaultAchievements(): Promise<{ created: number }> {
  const response = await api.post('/gamification/admin/achievements/seed');
  return response.data;
}

export async function rebuildLeaderboard(): Promise<{ updated: number }> {
  const response = await api.post('/gamification/admin/leaderboard/rebuild');
  return response.data;
}

export default {
  getMyStats,
  getUserStats,
  getMyAchievements,
  getUserAchievements,
  checkAchievements,
  getLeaderboard,
  updateStreak,
  createAchievement,
  seedDefaultAchievements,
  rebuildLeaderboard
};
