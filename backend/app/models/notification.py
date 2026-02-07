from sqlalchemy import Column, String, Boolean, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    COURSE_UPDATE = "course_update"
    NEW_ENROLLMENT = "new_enrollment"
    COURSE_COMPLETION = "course_completion"
    NEW_REVIEW = "new_review"
    REVIEW_RESPONSE = "review_response"
    DISCUSSION_REPLY = "discussion_reply"
    PAYMENT_SUCCESS = "payment_success"
    PAYOUT_APPROVED = "payout_approved"
    PAYOUT_COMPLETED = "payout_completed"
    NEW_CERTIFICATE = "new_certificate"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Link to related entities
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    enrollment_id = Column(UUID(as_uuid=True), nullable=True)
    payment_id = Column(UUID(as_uuid=True), nullable=True)
    discussion_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Metadata for additional data (e.g., actor name, amounts, etc.)
    meta_data = Column(JSONB, nullable=False, default=dict)
    
    # Action URL (where to redirect when clicked)
    action_url = Column(String(512), nullable=True)
    
    # Read status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Created timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    course = relationship("Course", foreign_keys=[course_id])


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Email notifications
    email_course_updates = Column(Boolean, default=True, nullable=False)
    email_new_enrollments = Column(Boolean, default=True, nullable=False)
    email_course_completions = Column(Boolean, default=True, nullable=False)
    email_new_reviews = Column(Boolean, default=True, nullable=False)
    email_discussion_replies = Column(Boolean, default=True, nullable=False)
    email_payment_updates = Column(Boolean, default=True, nullable=False)
    email_payout_updates = Column(Boolean, default=True, nullable=False)
    email_marketing = Column(Boolean, default=True, nullable=False)
    
    # In-app notifications
    inapp_course_updates = Column(Boolean, default=True, nullable=False)
    inapp_new_enrollments = Column(Boolean, default=True, nullable=False)
    inapp_course_completions = Column(Boolean, default=True, nullable=False)
    inapp_new_reviews = Column(Boolean, default=True, nullable=False)
    inapp_discussion_replies = Column(Boolean, default=True, nullable=False)
    inapp_payment_updates = Column(Boolean, default=True, nullable=False)
    inapp_payout_updates = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")
