from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, ForeignKey, Enum as SQEnum, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class CourseReview(Base):
    """Course review and rating model - enables social proof and trust"""

    __tablename__ = "course_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Rating and feedback
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=True)
    review_text = Column(Text, nullable=True)
    
    # Helpfulness tracking
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    
    # Metadata
    is_verified_purchase = Column(Boolean, default=False)  # Did they actually enroll?
    instructor_response = Column(Text, nullable=True)
    instructor_response_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

    def __repr__(self):
        return f"<CourseReview {self.id} - {self.rating} stars>"


class Certificate(Base):
    """Certificate model - gives learners proof of completion"""

    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    # Certificate details
    certificate_number = Column(String(50), unique=True, nullable=False)  # e.g., CERT-2026-001234
    issued_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Performance metrics
    completion_percentage = Column(Numeric(5, 2), nullable=False)  # e.g., 100.00
    final_grade = Column(Numeric(5, 2), nullable=True)  # e.g., 95.50
    total_hours_spent = Column(Numeric(6, 2), nullable=True)  # e.g., 42.75
    
    # Skills achieved
    skills_achieved = Column(JSONB, default=[], nullable=False)  # List of skills mastered
    
    # Certificate metadata
    certificate_url = Column(String(512), nullable=True)  # S3 or Cloudinary URL
    verification_url = Column(String(512), nullable=True)  # Public verification link
    
    # Status
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")

    def __repr__(self):
        return f"<Certificate {self.certificate_number}>"


class DiscussionCategory(str, enum.Enum):
    """Discussion categories for organizing forum posts"""
    GENERAL = "general"  # General course questions
    LESSON_SPECIFIC = "lesson_specific"  # About a specific lesson
    TECHNICAL = "technical"  # Technical issues
    CAREER = "career"  # Career advice
    PROJECTS = "projects"  # Project showcase
    ANNOUNCEMENTS = "announcements"  # Instructor announcements


class Discussion(Base):
    """Discussion forum model - enables community learning"""

    __tablename__ = "discussions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Content
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(SQEnum(DiscussionCategory, name="discussion_category"), nullable=False, default=DiscussionCategory.GENERAL)
    
    # Status and metadata
    is_pinned = Column(Boolean, default=False)  # Instructors can pin important threads
    is_resolved = Column(Boolean, default=False)  # Question answered?
    is_locked = Column(Boolean, default=False)  # No more replies allowed
    
    # Engagement metrics
    views_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    
    # Tags for searchability
    tags = Column(JSONB, default=[], nullable=False)  # e.g., ["python", "async", "beginner"]
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    course = relationship("Course", back_populates="discussions")
    lesson = relationship("Lesson", back_populates="discussions")
    user = relationship("User", back_populates="discussions")
    replies = relationship("DiscussionReply", back_populates="discussion", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Discussion {self.title}>"


class DiscussionReply(Base):
    """Replies to discussion threads"""

    __tablename__ = "discussion_replies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    discussion_id = Column(UUID(as_uuid=True), ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_reply_id = Column(UUID(as_uuid=True), ForeignKey("discussion_replies.id", ondelete="CASCADE"), nullable=True)  # For nested replies
    
    # Content
    content = Column(Text, nullable=False)
    
    # Metadata
    is_instructor_response = Column(Boolean, default=False)
    is_accepted_answer = Column(Boolean, default=False)  # Marked as solving the question
    upvotes = Column(Integer, default=0)
    
    # Edit tracking
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    discussion = relationship("Discussion", back_populates="replies")
    user = relationship("User", back_populates="discussion_replies")
    nested_replies = relationship("DiscussionReply", backref="parent_reply", remote_side=[id])

    def __repr__(self):
        return f"<DiscussionReply {self.id}>"
