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