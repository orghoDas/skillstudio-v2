from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class LearnerProfile(Base):
    # learner profile - stores learning preferences and behavioral data

    __tablename__ = "learner_profiles"

    # primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    #  learning preferences
    learning_style = Column(String(50), nullable=True)  # e.g., visual, auditory, kinesthetic, reading
    preferred_pace = Column(String(50), nullable=True)  # e.g., slow, med, fast
    study_hours_per_week = Column(Integer, nullable=True)

    # skill levels (JSONB)
    # example structure: {'python': 7, 'sql': 5, 'data_analysis': 6}
    skill_levels = Column(JSONB, default={}, nullable=False)

    # knowledge gaps (JSONB array)
    # example structure: ['machine_learning', 'cloud_computing']
    knowledge_gaps = Column(JSONB, default=[], nullable=False)

    # behavioral metrics
    avg_session_duration_mins = Column(Integer, nullable=True)

    # preferred study times (JSONB)
    # example structure: [{'day': 'monday', 'hour': 20}, {'day': 'wednesday', 'hour': 18}]
    preferred_study_times = Column(JSONB, default=[], nullable=False)

    # engagement indicators (last 30 days)
    completion_rate_30d = Column(Numeric(5, 2), nullable=True)  # percentage
    avg_quiz_score_30d = Column(Numeric(5, 2), nullable=True)  # percentage

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    user = relationship("User", back_populates="learner_profile")

    def __repr__(self):
        return f'<LearnerProfile user_id={self.user_id}>'