from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class LearnerProfileUpdate(BaseModel):
    # schema for updating learner profile
    learning_style: Optional[str] = Field(None, max_length=50)
    preferred_pace: Optional[str] = Field(None, max_length=50)
    study_hours_per_week: Optional[int] = Field(None, gt=0, le=168)
    skill_levels: Optional[dict] = None
    knowledge_gaps: Optional[List[str]] = None
    preferred_study_times: Optional[List[str]] = None


class LearnerProfileResponse(BaseModel):
    # schema for retrieving learner profile
    id: UUID
    user_id: UUID
    learning_style: Optional[str]
    preferred_pace: Optional[str]
    study_hours_per_week: Optional[int]
    skill_levels: Optional[dict]
    knowledge_gaps: Optional[List[str]]
    avg_session_duration_minutes: Optional[int]
    preferred_study_times: Optional[List[str]]
    completion_rate_30d: Optional[float]
    avg_quiz_score_30d: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True