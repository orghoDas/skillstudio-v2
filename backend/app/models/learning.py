from sqlalchemy import Column, Date, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class GoalStatus(str, enum.Enum):
    # learning goal statuses
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class LearningGoal(Base):
    # learning goals set by learners

    __tablename__ = "learning_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    goal_description = Column(Text, nullable=False)
    target_role = Column(String(255), nullable=True)
    target_skills = Column(JSONB, default=[], nullable=False)

    target_completion_date = Column(Date, nullable=True)
    current_status = Column(SQLEnum(GoalStatus, name="goal_status"), nullable=False, default=GoalStatus.ACTIVE)

    # metadata
    initial_skill_snapshot = Column(JSONB, default={}, nullable=False)
    completion_percentage = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # relationships
    user = relationship("User", back_populates="learning_goals")
    enrollments = relationship("Enrollment", back_populates="learning_goal")

    def __repr__(self):
        return f'<learning goal {self.goal_description[:50]}>'
    

class Enrollment(Base):
    # user enrollment in courses

    __tablename__ = "enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    learning_goal_id = Column(UUID(as_uuid=True), ForeignKey("learning_goals.id"), nullable=True)

    progress_percentage = Column(Integer, default=0)
    current_module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=True)
    current_lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=True)
    
    status = Column(String(50), nullable=False, default='active')  # active, completed, dropped
    certificate_url = Column(String(512), nullable=True)

    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    learning_goal = relationship("LearningGoal", back_populates="enrollments")

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id}>'
    

class ProgressStatus(str, enum.Enum):
    """Lesson progress status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVISION_NEEDED = "revision_needed"
    SKIPPED = "skipped"


class LessonProgress(Base):
    """
    Tracks individual lesson progress
    """
    __tablename__ = "lesson_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(
        SQLEnum(ProgressStatus, name="progress_status"),
        nullable=False,
        default=ProgressStatus.NOT_STARTED
    )
    
    # Time tracking
    time_spent_seconds = Column(Integer, default=0)
    completion_percentage = Column(Integer, default=0)
    
    # Engagement signals
    video_watch_percentage = Column(Integer, nullable=True)
    interactions = Column(JSONB, default={}, nullable=False)  # {"pauses": 3, "rewinds": 5}
    
    first_accessed = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress_records")
    
    def __repr__(self):
        return f"<LessonProgress user={self.user_id} lesson={self.lesson_id}>"