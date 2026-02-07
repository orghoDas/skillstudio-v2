"""
Gamification Service
Handles XP, achievements, leaderboards, and user stats
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc
from sqlalchemy.orm import selectinload

from app.models.gamification import (
    Achievement,
    UserAchievement,
    UserStats,
    XPTransaction,
    LeaderboardCache
)
from app.models.user import User
from app.models.learning import Enrollment, LessonProgress
from app.models.assessment import AssessmentAttempt


class GamificationService:
    """Service for gamification features"""
    
    # XP values for different actions
    XP_VALUES = {
        "lesson_completed": 50,
        "quiz_passed": 100,
        "quiz_perfect": 150,
        "course_completed": 500,
        "daily_streak": 20,
        "achievement_unlocked": 200,
        "first_review": 50,
        "discussion_post": 30
    }
    
    async def get_or_create_user_stats(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> UserStats:
        """Get or create user stats"""
        result = await db.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = UserStats(user_id=user_id)
            db.add(stats)
            await db.commit()
            await db.refresh(stats)
        
        return stats
    
    async def award_xp(
        self,
        db: AsyncSession,
        user_id: UUID,
        amount: int,
        reason: str,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Award XP to a user"""
        # Get user stats
        stats = await self.get_or_create_user_stats(db, user_id)
        
        # Record transaction
        transaction = XPTransaction(
            user_id=user_id,
            amount=amount,
            reason=reason,
            reference_type=reference_type,
            reference_id=reference_id
        )
        db.add(transaction)
        
        # Update stats
        old_level = stats.level
        stats.total_xp += amount
        stats.level = stats.calculate_level()
        
        await db.commit()
        await db.refresh(stats)
        
        # Check if level up occurred
        level_up = stats.level > old_level
        
        # Check for achievements
        await self.check_and_unlock_achievements(db, user_id)
        
        # Update leaderboard cache
        await self.update_leaderboard_cache(db, user_id)
        
        return {
            "xp_awarded": amount,
            "total_xp": stats.total_xp,
            "level": stats.level,
            "level_up": level_up,
            "xp_for_next_level": stats.xp_for_next_level()
        }
    
    async def update_streak(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Dict[str, int]:
        """Update user's learning streak"""
        stats = await self.get_or_create_user_stats(db, user_id)
        
        today = date.today()
        last_activity = stats.last_activity_date
        
        # Check if activity is today (already updated)
        if last_activity == today:
            return {
                "current_streak": stats.current_streak_days,
                "longest_streak": stats.longest_streak_days
            }
        
        # Check if streak continues (yesterday)
        if last_activity == today - timedelta(days=1):
            stats.current_streak_days += 1
            # Award streak XP
            await self.award_xp(
                db, user_id, 
                self.XP_VALUES["daily_streak"], 
                f"Daily streak: {stats.current_streak_days} days"
            )
        elif last_activity is None or last_activity < today - timedelta(days=1):
            # Streak broken, reset to 1
            stats.current_streak_days = 1
        
        # Update longest streak if needed
        if stats.current_streak_days > stats.longest_streak_days:
            stats.longest_streak_days = stats.current_streak_days
        
        stats.last_activity_date = today
        await db.commit()
        await db.refresh(stats)
        
        return {
            "current_streak": stats.current_streak_days,
            "longest_streak": stats.longest_streak_days
        }
    
    async def on_lesson_completed(
        self,
        db: AsyncSession,
        user_id: UUID,
        lesson_id: UUID,
        study_time_minutes: int = 0
    ):
        """Handle lesson completion event"""
        stats = await self.get_or_create_user_stats(db, user_id)
        
        # Update stats
        stats.lessons_completed += 1
        stats.total_study_time_minutes += study_time_minutes
        await db.commit()
        
        # Award XP
        await self.award_xp(
            db, user_id,
            self.XP_VALUES["lesson_completed"],
            "Completed a lesson",
            reference_type="lesson",
            reference_id=lesson_id
        )
        
        # Update streak
        await self.update_streak(db, user_id)
    
    async def on_quiz_completed(
        self,
        db: AsyncSession,
        user_id: UUID,
        quiz_id: UUID,
        score_percentage: float
    ):
        """Handle quiz completion event"""
        stats = await self.get_or_create_user_stats(db, user_id)
        
        stats.quizzes_completed += 1
        await db.commit()
        
        # Award XP based on performance
        if score_percentage == 100:
            xp_amount = self.XP_VALUES["quiz_perfect"]
            reason = "Perfect quiz score!"
        elif score_percentage >= 70:
            xp_amount = self.XP_VALUES["quiz_passed"]
            reason = f"Passed quiz with {score_percentage}%"
        else:
            xp_amount = self.XP_VALUES["quiz_passed"] // 2
            reason = f"Attempted quiz ({score_percentage}%)"
        
        await self.award_xp(
            db, user_id,
            xp_amount,
            reason,
            reference_type="quiz",
            reference_id=quiz_id
        )
    
    async def on_course_completed(
        self,
        db: AsyncSession,
        user_id: UUID,
        course_id: UUID
    ):
        """Handle course completion event"""
        stats = await self.get_or_create_user_stats(db, user_id)
        
        stats.courses_completed += 1
        await db.commit()
        
        # Award XP
        await self.award_xp(
            db, user_id,
            self.XP_VALUES["course_completed"],
            "Completed a course!",
            reference_type="course",
            reference_id=course_id
        )
    
    async def create_achievement(
        self,
        db: AsyncSession,
        name: str,
        description: str,
        category: str,
        requirement_type: str,
        requirement_value: int,
        points: int = 100,
        rarity: str = "common",
        icon_url: Optional[str] = None,
        badge_color: Optional[str] = None,
        requirement_data: Optional[Dict] = None
    ) -> Achievement:
        """Create a new achievement"""
        achievement = Achievement(
            name=name,
            description=description,
            category=category,
            requirement_type=requirement_type,
            requirement_value=requirement_value,
            points=points,
            rarity=rarity,
            icon_url=icon_url,
            badge_color=badge_color,
            requirement_data=requirement_data
        )
        
        db.add(achievement)
        await db.commit()
        await db.refresh(achievement)
        
        return achievement
    
    async def check_and_unlock_achievements(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> List[Achievement]:
        """Check and unlock eligible achievements"""
        # Get user stats
        stats = await self.get_or_create_user_stats(db, user_id)
        
        # Get all active achievements
        result = await db.execute(
            select(Achievement).where(Achievement.is_active == True)
        )
        achievements = result.scalars().all()
        
        # Get user's unlocked achievements
        result = await db.execute(
            select(UserAchievement.achievement_id)
            .where(UserAchievement.user_id == user_id)
        )
        unlocked_ids = {row[0] for row in result.fetchall()}
        
        newly_unlocked = []
        
        for achievement in achievements:
            if achievement.id in unlocked_ids:
                continue
            
            # Check if requirement is met
            requirement_met = False
            
            if achievement.requirement_type == "courses_completed":
                requirement_met = stats.courses_completed >= achievement.requirement_value
            elif achievement.requirement_type == "lessons_completed":
                requirement_met = stats.lessons_completed >= achievement.requirement_value
            elif achievement.requirement_type == "streak_days":
                requirement_met = stats.current_streak_days >= achievement.requirement_value
            elif achievement.requirement_type == "total_xp":
                requirement_met = stats.total_xp >= achievement.requirement_value
            elif achievement.requirement_type == "level":
                requirement_met = stats.level >= achievement.requirement_value
            elif achievement.requirement_type == "quizzes_completed":
                requirement_met = stats.quizzes_completed >= achievement.requirement_value
            
            if requirement_met:
                # Unlock achievement
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    progress=100
                )
                db.add(user_achievement)
                
                # Update stats
                stats.achievements_unlocked += 1
                
                # Award achievement points as XP
                await self.award_xp(
                    db, user_id,
                    achievement.points,
                    f"Unlocked: {achievement.name}",
                    reference_type="achievement",
                    reference_id=achievement.id
                )
                
                newly_unlocked.append(achievement)
        
        if newly_unlocked:
            await db.commit()
        
        return newly_unlocked
    
    async def get_leaderboard(
        self,
        db: AsyncSession,
        timeframe: str = "all_time",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get leaderboard"""
        result = await db.execute(
            select(LeaderboardCache)
            .options(selectinload(LeaderboardCache.user))
            .where(LeaderboardCache.timeframe == timeframe)
            .order_by(LeaderboardCache.rank)
            .limit(limit)
        )
        
        entries = result.scalars().all()
        
        return [
            {
                "rank": entry.rank,
                "user_id": str(entry.user_id),
                "full_name": entry.user.full_name,
                "total_xp": entry.total_xp,
                "level": entry.level,
                "courses_completed": entry.courses_completed,
                "current_streak": entry.current_streak
            }
            for entry in entries
        ]
    
    async def update_leaderboard_cache(
        self,
        db: AsyncSession,
        user_id: Optional[UUID] = None
    ):
        """Update leaderboard cache (run this periodically)"""
        # If specific user, update just that user
        if user_id:
            stats = await self.get_or_create_user_stats(db, user_id)
            
            # Calculate rank
            result = await db.execute(
                select(func.count(UserStats.id))
                .where(UserStats.total_xp > stats.total_xp)
            )
            rank = result.scalar() + 1
            
            # Update or create cache entry
            result = await db.execute(
                select(LeaderboardCache).where(LeaderboardCache.user_id == user_id)
            )
            cache = result.scalar_one_or_none()
            
            if cache:
                cache.rank = rank
                cache.total_xp = stats.total_xp
                cache.level = stats.level
                cache.courses_completed = stats.courses_completed
                cache.current_streak = stats.current_streak_days
                cache.last_updated = datetime.utcnow()
            else:
                cache = LeaderboardCache(
                    user_id=user_id,
                    rank=rank,
                    total_xp=stats.total_xp,
                    level=stats.level,
                    courses_completed=stats.courses_completed,
                    current_streak=stats.current_streak_days
                )
                db.add(cache)
            
            await db.commit()
        else:
            # Full leaderboard rebuild
            result = await db.execute(
                select(UserStats)
                .order_by(desc(UserStats.total_xp))
            )
            all_stats = result.scalars().all()
            
            # Delete old cache
            await db.execute(
                LeaderboardCache.__table__.delete()
            )
            
            # Insert new rankings
            for rank, stats in enumerate(all_stats, start=1):
                cache = LeaderboardCache(
                    user_id=stats.user_id,
                    rank=rank,
                    total_xp=stats.total_xp,
                    level=stats.level,
                    courses_completed=stats.courses_completed,
                    current_streak=stats.current_streak_days
                )
                db.add(cache)
            
            await db.commit()
    
    async def get_user_achievements(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get user's achievements"""
        result = await db.execute(
            select(UserAchievement)
            .options(selectinload(UserAchievement.achievement))
            .where(UserAchievement.user_id == user_id)
            .order_by(desc(UserAchievement.unlocked_at))
        )
        
        user_achievements = result.scalars().all()
        
        return {
            "unlocked": [
                {
                    "id": str(ua.achievement.id),
                    "name": ua.achievement.name,
                    "description": ua.achievement.description,
                    "category": ua.achievement.category,
                    "rarity": ua.achievement.rarity,
                    "points": ua.achievement.points,
                    "icon_url": ua.achievement.icon_url,
                    "badge_color": ua.achievement.badge_color,
                    "unlocked_at": ua.unlocked_at.isoformat()
                }
                for ua in user_achievements
            ],
            "total_unlocked": len(user_achievements)
        }
    
    async def seed_default_achievements(self, db: AsyncSession):
        """Create default achievements"""
        default_achievements = [
            # Learning achievements
            {"name": "First Steps", "description": "Complete your first lesson", "category": "learning", 
             "requirement_type": "lessons_completed", "requirement_value": 1, "points": 50, "rarity": "common"},
            {"name": "Learning Enthusiast", "description": "Complete 10 lessons", "category": "learning",
             "requirement_type": "lessons_completed", "requirement_value": 10, "points": 100, "rarity": "common"},
            {"name": "Knowledge Seeker", "description": "Complete 50 lessons", "category": "learning",
             "requirement_type": "lessons_completed", "requirement_value": 50, "points": 300, "rarity": "rare"},
            
            # Course completions
            {"name": "Course Graduate", "description": "Complete your first course", "category": "completion",
             "requirement_type": "courses_completed", "requirement_value": 1, "points": 200, "rarity": "common"},
            {"name": "Multi-Skilled", "description": "Complete 5 courses", "category": "completion",
             "requirement_type": "courses_completed", "requirement_value": 5, "points": 500, "rarity": "rare"},
            {"name": "Master Learner", "description": "Complete 10 courses", "category": "completion",
             "requirement_type": "courses_completed", "requirement_value": 10, "points": 1000, "rarity": "epic"},
            
            # Streak achievements
            {"name": "Committed", "description": "Maintain a 7-day learning streak", "category": "streak",
             "requirement_type": "streak_days", "requirement_value": 7, "points": 150, "rarity": "common"},
            {"name": "Dedicated", "description": "Maintain a 30-day learning streak", "category": "streak",
             "requirement_type": "streak_days", "requirement_value": 30, "points": 500, "rarity": "rare"},
            {"name": "Unstoppable", "description": "Maintain a 100-day learning streak", "category": "streak",
             "requirement_type": "streak_days", "requirement_value": 100, "points": 2000, "rarity": "legendary"},
            
            # Level achievements
            {"name": "Level 5", "description": "Reach level 5", "category": "mastery",
             "requirement_type": "level", "requirement_value": 5, "points": 200, "rarity": "common"},
            {"name": "Level 10", "description": "Reach level 10", "category": "mastery",
             "requirement_type": "level", "requirement_value": 10, "points": 500, "rarity": "rare"},
            {"name": "Level 25", "description": "Reach level 25", "category": "mastery",
             "requirement_type": "level", "requirement_value": 25, "points": 1500, "rarity": "epic"},
        ]
        
        for ach_data in default_achievements:
            await self.create_achievement(db, **ach_data)
