from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Date, Numeric, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class AchievementCategory(str, enum.Enum):
    LEARNING = "learning"
    SOCIAL = "social"
    COMPLETION = "completion"
    STREAK = "streak"
    MASTERY = "mastery"


class AchievementRarity(str, enum.Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Achievement(Base):
    """Achievement/Badge definitions"""
    
    __tablename__ = "achievements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    icon_url = Column(String(512), nullable=True)
    badge_color = Column(String(50), nullable=True)
    points = Column(Integer, default=0)
    
    # Requirements
    requirement_type = Column(String(100), nullable=False)  # courses_completed, streak_days, etc.
    requirement_value = Column(Integer, nullable=False)
    requirement_data = Column(JSONB, nullable=True)
    
    is_active = Column(Boolean, default=True)
    rarity = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Achievement {self.name}>"


class UserAchievement(Base):
    """User's unlocked achievements"""
    
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    progress = Column(Integer, default=0)
    is_displayed = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    def __repr__(self):
        return f"<UserAchievement user={self.user_id} achievement={self.achievement_id}>"


class UserStats(Base):
    """User gamification statistics"""
    
    __tablename__ = "user_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # XP and Level
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    
    # Completion stats
    courses_completed = Column(Integer, default=0)
    lessons_completed = Column(Integer, default=0)
    quizzes_completed = Column(Integer, default=0)
    
    # Streaks
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    last_activity_date = Column(Date, nullable=True)
    
    # Engagement
    total_study_time_minutes = Column(Integer, default=0)
    achievements_unlocked = Column(Integer, default=0)
    rank_position = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="stats")
    
    def calculate_level(self):
        """Calculate level from XP (level = sqrt(total_xp / 100))"""
        import math
        return max(1, int(math.sqrt(self.total_xp / 100)))
    
    def xp_for_next_level(self):
        """Calculate XP needed for next level"""
        next_level = self.level + 1
        return (next_level ** 2) * 100
    
    def __repr__(self):
        return f"<UserStats user={self.user_id} level={self.level} xp={self.total_xp}>"


class XPTransaction(Base):
    """XP gain/loss transaction log"""
    
    __tablename__ = "xp_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    reference_type = Column(String(100), nullable=True)  # lesson, quiz, achievement
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="xp_transactions")
    
    def __repr__(self):
        return f"<XPTransaction user={self.user_id} amount={self.amount}>"


class LeaderboardCache(Base):
    """Cached leaderboard for performance"""
    
    __tablename__ = "leaderboard_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    rank = Column(Integer, nullable=False)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    courses_completed = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    timeframe = Column(String(50), default='all_time')  # all_time, monthly, weekly
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="leaderboard_entry")
    
    def __repr__(self):
        return f"<LeaderboardCache rank={self.rank} user={self.user_id}>"
