from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models.course import DifficultyLevel, ContentType


# course schemas
class CourseBase(BaseModel):
    # base course schema
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    est_duration_minutes: Optional[int] = Field(None, gt=0)
    skills_taught: list[str] = []
    prerequisites: list[dict] = []
    thumbnail_url: Optional[str] = None


class CourseCreate(CourseBase):
    # schema for creating a course
    pass


class CourseUpdate(CourseBase):
    # schema for updating a course
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    difficulty_level: Optional[DifficultyLevel] = None
    est_duration_minutes: Optional[int] = Field(None, gt=0)
    skills_taught: Optional[list[str]] = None
    prerequisites: Optional[list[dict]] = None
    thumbnail_url: Optional[str] = None
    is_published: Optional[bool] = None


class CourseResponse(CourseBase):
    # schema for course response
    id: UUID
    title: str
    short_description: Optional[str]
    difficulty_level: DifficultyLevel
    est_duration_minutes: Optional[int]
    skills_taught: list[str]
    thumbnail_url: Optional[str]
    is_published: bool
    total_enrollments: int
    created_at: datetime

    class Config:
        from_attributes = True


# module schema
class ModuleBase(BaseModel):
    # base module schema
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    sequence_order: int = Field(..., ge=1)
    est_duration_minutes: Optional[int] = Field(None, gt=0)


class ModuleCreate(ModuleBase):
    # schema for creating a module
    pass


class ModuleUpdate(ModuleBase):
    # schema for updating a module
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    sequence_order: Optional[int] = Field(None, ge=1)
    est_duration_minutes: Optional[int] = Field(None, gt=0)


class ModuleResponse(ModuleBase):
    # schema for module response
    id: UUID
    course_id: UUID
    created_at: datetime

    class config:
        from_attributes = True 


# lesson schema
class LessonBase(BaseModel):
    # base lesson schema
    title: str = Field(..., min_length=3, max_length=200)
    content_type: ContentType = ContentType.ARTICLE
    content_url: Optional[str] = None
    content_body: Optional[str] = None
    content_metadata: dict = {} 
    est_mins : Optional[int] = Field(None, gt=0)
    difficulty_score : Optional[int] = Field(None, ge=1, le=10)
    prerequisites: list[dict] = []
    skill_tags : list[str] = []
    learning_objectives : list[str] = []
    sequence_order: int = Field(..., ge=1)


class LessonCreate(LessonBase):
    # schema for creating a lesson
    pass


class LessonUpdate(LessonBase):
    # schema for updating a lesson
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content_type: Optional[ContentType] = None
    content_url: Optional[str] = None
    content_body: Optional[str] = None
    content_metadata: Optional[dict] = None
    est_mins : Optional[int] = Field(None, gt=0)
    difficulty_score : Optional[int] = Field(None, ge=1, le=10)
    prerequisites: Optional[list[dict]] = None
    skill_tags : Optional[list[str]] = None
    learning_objectives : Optional[list[str]] = None
    sequence_order: Optional[int] = Field(None, ge=1)
    is_published: Optional[bool] = None


class LessonResponse(LessonBase):
    # schema for lesson response
    id: UUID
    module_id: UUID
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
