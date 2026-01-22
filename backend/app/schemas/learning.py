from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from app.models.learning import GoalStatus, ProgressStatus


# learning goal schemas
class LearningGoalBase(BaseModel):
    # base learning goal schema
    goal_description: str = Field(..., min_length=1, max_length=500)
    target_role : Optional[str] = Field(None, max_length=100)
    target_skills: List[str] = []
    target_completion_date: Optional[date] = None


class LearningGoalCreate(LearningGoalBase):
    # schema for creating a learning goal
    pass


class LearningGoalUpdate(BaseModel):
    # schema for updating a learning goal
    goal_description: Optional[str] = Field(None, min_length=1, max_length=500)
    target_role : Optional[str] = Field(None, max_length=100)
    target_skills: Optional[List[str]] = None
    target_completion_date: Optional[date] = None
    current_status: Optional[GoalStatus] = None


class LearningGoalResponse(LearningGoalBase):
    # schema for learning goal response
    id: UUID
    user_id: UUID
    current_status: GoalStatus
    initial_skill_snapshot : dict
    completion_percentage: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] 

    class Config:
        from_attributes = True


# enrollment schemas
class EnrollmentCreate(BaseModel):
    # schema for creating an enrollment
    course_id: UUID
    learning_goal_id: Optional[UUID] = None


class EnrollmentResponse(BaseModel):
    # schema for enrollment response
    id: UUID
    user_id: UUID
    course_id: UUID
    learning_goal_id: Optional[UUID]
    progress_percentage: int
    enrolled_at: datetime
    last_accessed: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# progress schemas
class LessonProgressUpdate(BaseModel):
    # schema for updating lesson progress
    status: Optional[ProgressStatus] = None
    time_spent_seconds: Optional[int] = Field(None, ge=0)
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    video_watch_percentage: Optional[int] = Field(None, ge=0, le=100)
    interactions: Optional[dict] = None


class LessonProgressResponse(BaseModel):
    # schema for lesson progress response
    id: UUID
    user_id: UUID
    lesson_id: UUID
    status: ProgressStatus
    time_spent_seconds: int
    completion_percentage: int
    video_watch_percentage: Optional[int]
    interactions: dict
    first_accessed: Optional[datetime]
    last_accessed: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
    