from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class Assessment(Base):
    # assessment/quiz for skill evaluation
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # assessment type
    is_diagnostic = Column(Boolean, default=False) 

    # skills being assessed
    skills_assessed = Column(JSONB, default=[], nullable=False)

    # configuration
    time_limit_minutes = Column(Integer, nullable=True)  # null means no time limit
    passing_score = Column(Integer, default=60)  # percentage required to pass

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    attemps = relationship("AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Assessment {self.title}>'


class AssessmentQuestion(Base):
    # Individual questions within an assessment
    __tablename__ = "assessment_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey('assessments.id', ondelete="CASCADE"), nullable=False)

    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # e.g., 'multiple_choice', 'true_false', 'short_answer'

    # options and answers stored as JSON
    options = Column(JSONB, nullable=True)  # for multiple choice questions
    correct_answer = Column(JSONB, nullable=False)  # could be a single answer or multiple answers

    explanation = Column(Text, nullable=True)  # explanation for the correct answer

    # metadata
    difficulty_level = Column(Integer, nullable=False, default=5)
    points = Column(Integer, default=1)
    skill_tags = Column(JSONB, default=[], nullable=False)

    sequence_order = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    assessment = relationship("Assessment", back_populates="questions")

    def __repr__(self):
        return f'<AssessmentQuestion {self.question_text[:50]}>'
    

class AssessmentAttempt(Base):
    # users attempt at an assessment
    __tablename__ = "assessment_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey('assessments.id', ondelete="CASCADE"), nullable=False)

    # results
    score_percecntage = Column(Numeric(5, 2), nullable=False)
    points_earned = Column(Integer, nullable=False)
    points_possible = Column(Integer, nullable=False)

    time_taken_seconds = Column(Integer, nullable=False)

    # detailed answers
    answers = Column(JSONB, nullable=False)  # {question_id: user_answer, ...}

    # performance breakdown 
    skill_scores = Column(JSONB, nullable=True)  # {skill: score_percentage, ...}

    # metadata
    attempt_number = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)

    # Ai generated feedback
    feedback = Column(Text, nullable=True)

    attempted_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    user = relationship("User", back_populates="assessment_attempts")
    assessment = relationship("Assessment", back_populates="attempts")

    def __repr__(self):
        return f'<AssessmentAttempt User:{self.user_id} score:{self.score_percentage}%>'
    
