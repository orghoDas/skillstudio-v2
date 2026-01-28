from sqlalchemy import Column, DateTime, DateTime, Integer, String, Text, Boolean, ForeignKey, Enum as SQEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class DifficultyLevel(str, enum.Enum):

    # course difficulty levels
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Course(Base):
    # course model - represents a course in the system

    __tablename__ = "courses"

    # primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(512), nullable=True)

    # course attributes
    difficulty_level = Column(SQEnum(DifficultyLevel, name="difficulty_level"), nullable=False, default=DifficultyLevel.BEGINNER)
    estimated_duration_hours = Column(Integer, nullable=True)

    # skills & prerequisites
    skills_taught = Column(JSONB, default=[], nullable=False) 
    prerequisites = Column(JSONB, default=[], nullable=False)

    # media
    thumbnail_url = Column(String(512), nullable=True)

    # ownership
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # status
    is_published = Column(Boolean, default=False)

    # statistics
    total_enrollments = Column(Integer, default=0)

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    instructor = relationship("User", back_populates="courses_created")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.ttle}>"


class Module(Base):
    # module model - represents a module within a course

    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False)
    est_duration_minutes = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module {self.title}>"
    

class ContentType(str, enum.Enum):
    
    # lesson content types
    VIDEO = "video"
    ARTICLE = "article"
    QUIZ = "quiz"
    INTERACTIVE = "interactive"
    CODE_EXERCISE = "code_exercise"


class Lesson(Base):
    # lesson model - represents a lesson within a Module

    __tablename__ = "lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False)
    content_type = Column(SQEnum(ContentType, name="content_type"), nullable=False, default=ContentType.ARTICLE)

    # content preferences
    content_url = Column(String(512), nullable=True)  # for video or external content
    content_body = Column(Text, nullable=True)  # for articles or text-based content
    content_metadata = Column(JSONB, default={}, nullable=False)  # additional metadata

    # learning attributes
    estimated_minutes = Column(Integer, nullable=True)
    difficulty_score = Column(Integer, nullable=True)  # e.g., 1-10 scale

    # prerequisites 
    prerequisites = Column(JSONB, default=[], nullable=False)

    # skills & objectives
    skill_tags = Column(JSONB, default=[], nullable=False)
    learning_objectives = Column(JSONB, default=[], nullable=False)

    sequence_order = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    module = relationship("Module", back_populates="lessons")
    progress_records = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lesson {self.title}>"
    


