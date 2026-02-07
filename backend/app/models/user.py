from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    # user role enumeration
    LEARNER = "learner"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"

class User(Base):
    # user model - represents all users in the system
    __tablename__ = "users"

    # primary key
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    # authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # profile
    full_name = Column(String(255), nullable=False)
    role = Column(
        SQEnum(UserRole), name='user_role', nullable=False, default=UserRole.LEARNER, index = True
    )

    # status
    is_active = Column(Boolean, default=True, index=True)
    email_verified = Column(Boolean, default=False)

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # relationships
    learner_profile = relationship(
        'LearnerProfile', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )

    courses_created = relationship(
        'Course', back_populates='instructor', cascade='all, delete-orphan'
    )

    learning_goals = relationship(
        'LearningGoal', back_populates='user', cascade='all, delete-orphan'
    )

    enrollments = relationship(
        'Enrollment', back_populates='user', cascade='all, delete-orphan'
    ) 

    lesson_progress = relationship(
        'LessonProgress', back_populates='user', cascade='all, delete-orphan'
    )

    assessment_attempts = relationship(
        'AssessmentAttempt', back_populates='user', cascade='all, delete-orphan'
    )

    reviews = relationship(
        'CourseReview', back_populates='user', cascade='all, delete-orphan'
    )

    certificates = relationship(
        'Certificate', back_populates='user', cascade='all, delete-orphan'
    )

    discussions = relationship(
        'Discussion', back_populates='user', cascade='all, delete-orphan'
    )

    discussion_replies = relationship(
        'DiscussionReply', back_populates='user', cascade='all, delete-orphan'
    )

    subscription = relationship(
        'UserSubscription', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )

    payments = relationship(
        'Payment', back_populates='user', cascade='all, delete-orphan'
    )

    notifications = relationship(
        'Notification', back_populates='user', cascade='all, delete-orphan'
    )

    notification_preferences = relationship(
        'NotificationPreference', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )

    # Gamification relationships
    achievements = relationship(
        'UserAchievement', back_populates='user', cascade='all, delete-orphan'
    )

    stats = relationship(
        'UserStats', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )

    xp_transactions = relationship(
        'XPTransaction', back_populates='user', cascade='all, delete-orphan'
    )

    leaderboard_entry = relationship(
        'LeaderboardCache', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )

    # Video analytics relationships
    video_analytics = relationship(
        'VideoAnalytics', back_populates='user', cascade='all, delete-orphan'
    )

    # Instructor analytics
    instructor_analytics = relationship(
        'InstructorAnalytics', back_populates='instructor', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<User {self.email} ({self.role.value})>'
    
    @property
    def is_learner(self) -> bool:
        return self.role == UserRole.LEARNER
    
    @property
    def is_instructor(self) -> bool:
        return self.role == UserRole.INSTRUCTOR
    
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN