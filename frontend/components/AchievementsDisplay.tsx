"use client";

import React, { useEffect, useState } from 'react';
import { Award, Lock, Star, Sparkles } from 'lucide-react';

interface Achievement {
  id: string;
  name: string;
  description: string;
  category: string;
  rarity: string;
  points: number;
  icon_url?: string;
  badge_color?: string;
  unlocked_at?: string;
}

interface AchievementsData {
  unlocked: Achievement[];
  total_unlocked: number;
}

export default function AchievementsDisplay() {
  const [achievements, setAchievements] = useState<AchievementsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAchievements();
  }, []);

  const fetchAchievements = async () => {
    try {
      const response = await fetch('/api/gamification/achievements', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setAchievements(data);
    } catch (error) {
      console.error('Failed to fetch achievements:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'border-gray-400 bg-gray-50';
      case 'rare': return 'border-blue-500 bg-blue-50';
      case 'epic': return 'border-purple-500 bg-purple-50';
      case 'legendary': return 'border-yellow-500 bg-yellow-50';
      default: return 'border-gray-400 bg-gray-50';
    }
  };

  const getRarityGlow = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'shadow-sm';
      case 'rare': return 'shadow-md shadow-blue-200';
      case 'epic': return 'shadow-lg shadow-purple-300';
      case 'legendary': return 'shadow-xl shadow-yellow-300 animate-pulse';
      default: return 'shadow-sm';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'learning': return <Star className="text-blue-500" size={20} />;
      case 'completion': return <Award className="text-green-500" size={20} />;
      case 'streak': return <Sparkles className="text-orange-500" size={20} />;
      case 'mastery': return <Award className="text-purple-500" size={20} />;
      default: return <Award className="text-gray-500" size={20} />;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!achievements) {
    return <div>Error loading achievements</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Award className="text-yellow-500" size={28} />
            Achievements
          </h2>
          <p className="text-gray-600 text-sm mt-1">
            {achievements.total_unlocked} achievement{achievements.total_unlocked !== 1 ? 's' : ''} unlocked
          </p>
        </div>
      </div>

      {achievements.unlocked.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <Lock size={48} className="mx-auto mb-4 opacity-30" />
          <p className="mb-2">No achievements yet</p>
          <p className="text-sm">Complete courses and lessons to unlock achievements!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {achievements.unlocked.map((achievement) => (
            <div
              key={achievement.id}
              className={`${getRarityColor(achievement.rarity)} ${getRarityGlow(achievement.rarity)} border-2 rounded-lg p-4 transition-all hover:scale-105`}
            >
              <div className="flex items-start gap-3">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${achievement.badge_color || 'bg-yellow-400'}`}>
                  {getCategoryIcon(achievement.category)}
                </div>

                <div className="flex-1">
                  <h3 className="font-bold text-gray-800 mb-1 flex items-center gap-2">
                    {achievement.name}
                    {achievement.rarity === 'legendary' && (
                      <Sparkles className="text-yellow-500" size={16} />
                    )}
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    {achievement.description}
                  </p>

                  <div className="flex items-center justify-between text-xs">
                    <span className={`px-2 py-1 rounded-full ${
                      achievement.rarity === 'common' ? 'bg-gray-200 text-gray-700' :
                      achievement.rarity === 'rare' ? 'bg-blue-200 text-blue-700' :
                      achievement.rarity === 'epic' ? 'bg-purple-200 text-purple-700' :
                      'bg-yellow-200 text-yellow-700'
                    }`}>
                      {achievement.rarity.toUpperCase()}
                    </span>

                    <span className="text-purple-600 font-semibold">
                      +{achievement.points} XP
                    </span>
                  </div>

                  {achievement.unlocked_at && (
                    <p className="text-xs text-gray-500 mt-2">
                      Unlocked {new Date(achievement.unlocked_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
