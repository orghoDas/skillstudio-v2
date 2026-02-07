"""
Gamification API Routes
Handles achievements, leaderboards, XP, and user stats
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.gamification import GamificationService


router = APIRouter(prefix="/api/gamification", tags=["Gamification"])


class AwardXPRequest(BaseModel):
    user_id: UUID
    amount: int
    reason: str
    reference_type: str | None = None
    reference_id: UUID | None = None


class CreateAchievementRequest(BaseModel):
    name: str
    description: str
    category: str
    requirement_type: str
    requirement_value: int
    points: int = 100
    rarity: str = "common"
    icon_url: str | None = None
    badge_color: str | None = None


@router.get("/stats")
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current user's gamification stats
    """
    gamification_service = GamificationService()
    stats = await gamification_service.get_or_create_user_stats(db, current_user.id)
    
    return {
        "user_id": str(stats.user_id),
        "total_xp": stats.total_xp,
        "level": stats.level,
        "xp_for_next_level": stats.xp_for_next_level(),
        "courses_completed": stats.courses_completed,
        "lessons_completed": stats.lessons_completed,
        "quizzes_completed": stats.quizzes_completed,
        "current_streak_days": stats.current_streak_days,
        "longest_streak_days": stats.longest_streak_days,
        "total_study_time_minutes": stats.total_study_time_minutes,
        "achievements_unlocked": stats.achievements_unlocked,
        "rank_position": stats.rank_position
    }


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get any user's public stats
    """
    gamification_service = GamificationService()
    stats = await gamification_service.get_or_create_user_stats(db, user_id)
    
    return {
        "user_id": str(stats.user_id),
        "total_xp": stats.total_xp,
        "level": stats.level,
        "courses_completed": stats.courses_completed,
        "current_streak_days": stats.current_streak_days,
        "longest_streak_days": stats.longest_streak_days,
        "achievements_unlocked": stats.achievements_unlocked,
        "rank_position": stats.rank_position
    }


@router.get("/achievements")
async def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current user's achievements
    """
    gamification_service = GamificationService()
    achievements = await gamification_service.get_user_achievements(db, current_user.id)
    
    return achievements


@router.get("/achievements/{user_id}")
async def get_user_achievements(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get any user's achievements (public)
    """
    gamification_service = GamificationService()
    achievements = await gamification_service.get_user_achievements(db, user_id)
    
    return achievements


@router.post("/achievements/check")
async def check_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manually trigger achievement check (useful after big updates)
    """
    gamification_service = GamificationService()
    newly_unlocked = await gamification_service.check_and_unlock_achievements(
        db, current_user.id
    )
    
    return {
        "newly_unlocked_count": len(newly_unlocked),
        "achievements": [
            {
                "id": str(ach.id),
                "name": ach.name,
                "description": ach.description,
                "points": ach.points,
                "rarity": ach.rarity
            }
            for ach in newly_unlocked
        ]
    }


@router.get("/leaderboard")
async def get_leaderboard(
    timeframe: str = Query("all_time", regex="^(all_time|monthly|weekly)$"),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get leaderboard
    """
    gamification_service = GamificationService()
    leaderboard = await gamification_service.get_leaderboard(db, timeframe, limit)
    
    # Find current user's position
    user_rank = next(
        (entry["rank"] for entry in leaderboard if entry["user_id"] == str(current_user.id)),
        None
    )
    
    return {
        "timeframe": timeframe,
        "leaderboard": leaderboard,
        "my_rank": user_rank
    }


@router.post("/streak/update")
async def update_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update user's learning streak (call when user completes activity)
    """
    gamification_service = GamificationService()
    streak_data = await gamification_service.update_streak(db, current_user.id)
    
    return {
        "current_streak": streak_data["current_streak"],
        "longest_streak": streak_data["longest_streak"]
    }


# Admin endpoints
@router.post("/admin/achievement/create")
async def create_achievement(
    request: CreateAchievementRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create new achievement (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    gamification_service = GamificationService()
    achievement = await gamification_service.create_achievement(
        db,
        name=request.name,
        description=request.description,
        category=request.category,
        requirement_type=request.requirement_type,
        requirement_value=request.requirement_value,
        points=request.points,
        rarity=request.rarity,
        icon_url=request.icon_url,
        badge_color=request.badge_color
    )
    
    return {
        "id": str(achievement.id),
        "name": achievement.name,
        "description": achievement.description,
        "points": achievement.points
    }


@router.post("/admin/leaderboard/rebuild")
async def rebuild_leaderboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Rebuild leaderboard cache (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    gamification_service = GamificationService()
    await gamification_service.update_leaderboard_cache(db)
    
    return {"message": "Leaderboard cache rebuilt"}


@router.post("/admin/achievements/seed")
async def seed_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Seed default achievements (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    gamification_service = GamificationService()
    await gamification_service.seed_default_achievements(db)
    
    return {"message": "Default achievements created"}
