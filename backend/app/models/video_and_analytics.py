from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class VideoStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class VideoAnalytics(Base):
    """Track video watch analytics"""
    
    __tablename__ = "video_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    watch_duration_seconds = Column(Integer, nullable=True)
    completion_percentage = Column(Numeric(5, 2), nullable=True)
    playback_speed = Column(Numeric(3, 2), nullable=True)
    quality_selected = Column(String(50), nullable=True)
    device_type = Column(String(50), nullable=True)
    
    watched_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lesson = relationship("Lesson", back_populates="video_analytics")
    user = relationship("User", back_populates="video_analytics")
    
    def __repr__(self):
        return f"<VideoAnalytics lesson={self.lesson_id} user={self.user_id}>"


class PlatformAnalytics(Base):
    """Aggregated platform-wide analytics"""
    
    __tablename__ = "platform_analytics"
    __table_args__ = (
        UniqueConstraint('date', 'timeframe', 'metric_type', name='uq_platform_analytics'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False, index=True)
    timeframe = Column(String(50), nullable=False)  # daily, weekly, monthly
    metric_type = Column(String(100), nullable=False)  # users, revenue, engagement
    metric_data = Column(JSONB, nullable=False)
    # Example metric_data structure:
    # {
    #   "dau": 1234,
    #   "mau": 5678,
    #   "new_users": 45,
    #   "revenue": 12345.67,
    #   "courses_completed": 89,
    #   "avg_engagement_minutes": 45.6
    # }
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PlatformAnalytics {self.date} {self.timeframe} {self.metric_type}>"


class CourseAnalytics(Base):
    """Per-course analytics aggregation"""
    
    __tablename__ = "course_analytics"
    __table_args__ = (
        UniqueConstraint('course_id', 'date', name='uq_course_analytics_date'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    enrollments_count = Column(Integer, default=0)
    completions_count = Column(Integer, default=0)
    avg_completion_time_hours = Column(Numeric(10, 2), nullable=True)
    avg_rating = Column(Numeric(3, 2), nullable=True)
    total_revenue = Column(Numeric(12, 2), default=0)
    active_learners = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="analytics")
    
    def __repr__(self):
        return f"<CourseAnalytics course={self.course_id} date={self.date}>"


class InstructorAnalytics(Base):
    """Per-instructor analytics aggregation"""
    
    __tablename__ = "instructor_analytics"
    __table_args__ = (
        UniqueConstraint('instructor_id', 'date', name='uq_instructor_analytics_date'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    total_students = Column(Integer, default=0)
    total_courses = Column(Integer, default=0)
    total_revenue = Column(Numeric(12, 2), default=0)
    avg_course_rating = Column(Numeric(3, 2), nullable=True)
    total_enrollments = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    instructor = relationship("User", back_populates="instructor_analytics")
    
    def __repr__(self):
        return f"<InstructorAnalytics instructor={self.instructor_id} date={self.date}>"
