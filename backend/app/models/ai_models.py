from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric, BigInteger, cast
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, ENUM as PGENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class SnapshotType(str, enum.Enum):
    """Learning path snapshot types"""
    INITIAL = "initial"
    WEEKLY_ADJUSTMENT = "weekly_adjustment"
    MILESTONE = "milestone"
    MANUAL = "manual"


class LearningPathSnapshot(Base):
    """
    Stores AI-generated learning path versions over time
    Tracks how recommendations evolve based on learner progress
    """
    __tablename__ = "learning_path_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    learning_goal_id = Column(UUID(as_uuid=True), ForeignKey('learning_goals.id', ondelete='CASCADE'), nullable=True)
    
    # Use PostgreSQL ENUM type that references existing database enum
    snapshot_type = Column(
        PGENUM('initial', 'weekly_adjustment', 'milestone', 'manual', name='snapshot_type', create_type=False),
        nullable=False,
        default="initial"
    )
    
    # The recommended learning path
    # Structure: [{"type": "course", "id": "uuid", "title": "...", "sequence": 1, "reason": "..."}]
    recommended_path = Column(JSONB, nullable=False)
    
    # Path metadata
    estimated_total_hours = Column(Integer, nullable=True)
    estimated_completion_date = Column(DateTime(timezone=True), nullable=True)
    confidence_score = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    
    # What changed from previous snapshot
    changes_from_previous = Column(JSONB, nullable=True)
    adjustment_reasons = Column(JSONB, nullable=True)  # Why path was adjusted
    
    # Only one active path per user/goal
    active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    learning_goal = relationship("LearningGoal")
    
    def __repr__(self):
        return f'<LearningPathSnapshot user={self.user_id} type={self.snapshot_type.value}>'


class RecommendationType(str, enum.Enum):
    """Types of recommendations"""
    NEXT_LESSON = "next_lesson"
    REVISION = "revision"
    PRACTICE = "practice"
    DIFFICULTY_ADJUSTMENT = "difficulty_adjustment"
    COURSE = "course"


class RecommendationAction(str, enum.Enum):
    """User action on recommendation"""
    ACCEPTED = "accepted"
    SKIPPED = "skipped"
    MODIFIED = "modified"
    IGNORED = "ignored"


class Recommendation(Base):
    """
    AI-generated recommendations for learners
    Tracks what was recommended, why, and how users responded
    """
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Use PostgreSQL ENUM type
    recommendation_type = Column(
        PGENUM('next_lesson', 'revision', 'practice', 'difficulty_adjustment', 'course', name='recommendation_type', create_type=False),
        nullable=False,
        index=True
    )
    
    # What's being recommended (polymorphic - can be lesson, assessment, course)
    recommended_content_id = Column(UUID(as_uuid=True), nullable=True)
    recommended_content_type = Column(String(50), nullable=True)  # 'lesson', 'assessment', 'course'
    
    # Recommendation metadata
    reason = Column(Text, nullable=False)  # Human-readable explanation
    confidence_score = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    priority = Column(Integer, default=5)  # 1 = highest priority
    
    # AI model information
    model_version = Column(String(50), nullable=True)
    features_used = Column(JSONB, nullable=True)  # Which features drove this recommendation
    
    # User interaction  
    user_action = Column(
        PGENUM('accepted', 'skipped', 'modified', 'ignored', name='recommendation_action', create_type=False),
        nullable=True
    )
    actioned_at = Column(DateTime(timezone=True), nullable=True)
    
    # Recommendations can expire
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f'<Recommendation {self.recommendation_type.value} for user={self.user_id}>'


class MLModelMetadata(Base):
    """
    Metadata for ML models used in the platform
    Tracks model versions, performance, and deployment
    """
    __tablename__ = "ml_model_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=True)  # 'collaborative_filtering', 'difficulty_predictor', etc.
    
    # Model artifacts
    model_path = Column(String(500), nullable=True)  # S3 path or local file path
    feature_columns = Column(JSONB, nullable=True)  # Which features the model uses
    
    # Performance metrics
    performance_metrics = Column(JSONB, nullable=True)  # {"accuracy": 0.87, "precision": 0.82, ...}
    
    # Training metadata
    training_data_size = Column(Integer, nullable=True)
    trained_at = Column(DateTime(timezone=True), nullable=True)
    
    # Only one active version per model_name
    is_active = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f'<MLModel {self.model_name} v{self.model_version}>'


class LearnerEvent(Base):
    """
    Time-series event tracking for learner behavior
    NOTE: In production, this should be a partitioned table by event_timestamp
    """
    __tablename__ = "learner_events"
    
    # Use BigInteger for auto-incrementing ID in partitioned table
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    event_type = Column(String(100), nullable=False, index=True)
    # Event types: 'lesson_start', 'lesson_pause', 'lesson_completed', 'quiz_attempt', etc.
    
    event_timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    
    # Context references
    lesson_id = Column(UUID(as_uuid=True), ForeignKey('lessons.id', ondelete='CASCADE'), nullable=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey('assessments.id', ondelete='CASCADE'), nullable=True)
    session_id = Column(String(100), nullable=True, index=True)
    
    # Flexible event data
    event_data = Column(JSONB, nullable=True)
    # Example: {"duration_seconds": 120, "completion_percentage": 75, "video_speed": 1.5}
    
    # Device/browser metadata
    device_type = Column(String(50), nullable=True)  # 'mobile', 'desktop', 'tablet'
    browser = Column(String(100), nullable=True)
    ip_address = Column(INET, nullable=True)
    
    # Relationships
    user = relationship("User")
    lesson = relationship("Lesson")
    assessment = relationship("Assessment")
    
    def __repr__(self):
        return f'<LearnerEvent {self.event_type} user={self.user_id} at {self.event_timestamp}>'


# Create indexes for common queries
from sqlalchemy import Index

# Composite indexes for efficient queries
Index('idx_path_snapshots_user_active', LearningPathSnapshot.user_id, LearningPathSnapshot.active)
Index('idx_recommendations_user_expires', Recommendation.user_id, Recommendation.expires_at)
Index('idx_events_user_timestamp', LearnerEvent.user_id, LearnerEvent.event_timestamp.desc())
Index('idx_events_type_timestamp', LearnerEvent.event_type, LearnerEvent.event_timestamp.desc())
