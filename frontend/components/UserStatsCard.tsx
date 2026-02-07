"use client";

import React, { useEffect, useState } from 'react';
import { Trophy, Star, Award, TrendingUp, Flame, Book, Target } from 'lucide-react';
import { getMyStats } from '@/lib/gamification-service';

interface UserStatsData {
  total_xp: number;
  level: number;
  xp_for_next_level: number;
  courses_completed: number;
  lessons_completed: number;
  quizzes_completed: number;
  current_streak_days: number;
  longest_streak_days: number;
  total_study_time_minutes: number;
  achievements_unlocked: number;
  rank_position: number | null;
}

export default function UserStatsCard() {
  const [stats, setStats] = useState<UserStatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await getMyStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="bg-white rounded-lg shadow p-6 animate-pulse">Loading...</div>;
  }

  if (!stats) {
    return <div>Error loading stats</div>;
  }

  const xpProgress = ((stats.total_xp % stats.xp_for_next_level) / stats.xp_for_next_level) * 100;
  const studyHours = Math.floor(stats.total_study_time_minutes / 60);

  return (
    <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-xl p-6 text-white">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold">Level {stats.level}</h2>
          <p className="text-blue-100">Total XP: {stats.total_xp.toLocaleString()}</p>
        </div>
        <div className="relative">
          <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center">
            <Star size={40} className="text-yellow-300" />
          </div>
          {stats.rank_position && (
            <div className="absolute -bottom-2 -right-2 bg-yellow-400 text-purple-900 rounded-full w-8 h-8 flex items-center justify-center text-xs font-bold">
              #{stats.rank_position}
            </div>
          )}
        </div>
      </div>

      {/* XP Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm mb-1">
          <span>Progress to Level {stats.level + 1}</span>
          <span>{Math.floor(xpProgress)}%</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-3">
          <div
            className="bg-yellow-400 h-3 rounded-full transition-all duration-500"
            style={{ width: `${xpProgress}%` }}
          />
        </div>
        <p className="text-xs text-blue-100 mt-1">
          {stats.xp_for_next_level - (stats.total_xp % stats.xp_for_next_level)} XP remaining
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Book size={16} />
            <span className="text-xs opacity-90">Courses</span>
          </div>
          <p className="text-2xl font-bold">{stats.courses_completed}</p>
        </div>

        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Target size={16} />
            <span className="text-xs opacity-90">Lessons</span>
          </div>
          <p className="text-2xl font-bold">{stats.lessons_completed}</p>
        </div>

        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Flame size={16} className="text-orange-400" />
            <span className="text-xs opacity-90">Streak</span>
          </div>
          <p className="text-2xl font-bold">{stats.current_streak_days} days</p>
          <p className="text-xs opacity-75">Best: {stats.longest_streak_days}</p>
        </div>

        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Trophy size={16} className="text-yellow-400" />
            <span className="text-xs opacity-90">Achievements</span>
          </div>
          <p className="text-2xl font-bold">{stats.achievements_unlocked}</p>
        </div>
      </div>

      {/* Additional stats */}
      <div className="mt-4 pt-4 border-t border-white/20 flex justify-between text-sm">
        <div>
          <p className="opacity-75">Study Time</p>
          <p className="font-semibold">{studyHours}h {stats.total_study_time_minutes % 60}m</p>
        </div>
        <div>
          <p className="opacity-75">Quizzes</p>
          <p className="font-semibold">{stats.quizzes_completed} completed</p>
        </div>
      </div>
    </div>
  );
}
