"use client";

import React, { useEffect, useState } from 'react';
import { Trophy, Medal, Award, Crown } from 'lucide-react';
import { getLeaderboard } from '@/lib/gamification-service';

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  full_name: string;
  total_xp: number;
  level: number;
  courses_completed: number;
  current_streak: number;
}

interface LeaderboardProps {
  timeframe?: 'all_time' | 'monthly' | 'weekly';
  limit?: number;
}

export default function Leaderboard({ timeframe = 'all_time', limit = 10 }: LeaderboardProps) {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [myRank, setMyRank] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState(timeframe);

  useEffect(() => {
    fetchLeaderboard();
  }, [selectedTimeframe]);

  const fetchLeaderboard = async () => {
    try {
      const data = await getLeaderboard(selectedTimeframe, limit);
      setLeaderboard(data.leaderboard);
      setMyRank(data.my_rank);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Crown className="text-yellow-500" size={24} />;
    if (rank === 2) return <Medal className="text-gray-400" size={24} />;
    if (rank === 3) return <Medal className="text-amber-600" size={24} />;
    return <span className="text-gray-600 font-bold">#{rank}</span>;
  };

  const getRankBgClass = (rank: number) => {
    if (rank === 1) return 'bg-gradient-to-r from-yellow-100 to-yellow-50 border-yellow-400';
    if (rank === 2) return 'bg-gradient-to-r from-gray-100 to-gray-50 border-gray-400';
    if (rank === 3) return 'bg-gradient-to-r from-amber-100 to-amber-50 border-amber-400';
    return 'bg-white border-gray-200';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Trophy className="text-yellow-500" size={28} />
          <h2 className="text-2xl font-bold text-gray-800">Leaderboard</h2>
        </div>

        <select
          value={selectedTimeframe}
          onChange={(e) => setSelectedTimeframe(e.target.value as any)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="all_time">All Time</option>
          <option value="monthly">This Month</option>
          <option value="weekly">This Week</option>
        </select>
      </div>

      {myRank && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
          <p className="text-sm text-blue-800">
            <strong>Your Rank:</strong> #{myRank}
          </p>
        </div>
      )}

      <div className="space-y-2">
        {leaderboard.map((entry) => (
          <div
            key={entry.user_id}
            className={`${getRankBgClass(entry.rank)} border rounded-lg p-4 flex items-center justify-between transition-all hover:shadow-md`}
          >
            <div className="flex items-center gap-4 flex-1">
              <div className="w-12 flex items-center justify-center">
                {getRankIcon(entry.rank)}
              </div>

              <div className="flex-1">
                <h3 className="font-semibold text-gray-800">{entry.full_name}</h3>
                <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                  <span>Level {entry.level}</span>
                  <span>•</span>
                  <span>{entry.courses_completed} courses</span>
                  <span>•</span>
                  <span>{entry.current_streak} day streak</span>
                </div>
              </div>

              <div className="text-right">
                <div className="text-2xl font-bold text-purple-600">
                  {entry.total_xp.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">XP</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {leaderboard.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Trophy size={48} className="mx-auto mb-4 opacity-30" />
          <p>No leaderboard data yet</p>
          <p className="text-sm">Start completing courses to climb the ranks!</p>
        </div>
      )}
    </div>
  );
}
