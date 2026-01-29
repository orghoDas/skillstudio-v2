from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# assessment schemas
class AssessmentCreate(BaseModel):
    # schema for creating an assessment
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    is_diagnostic: bool = False
    skills_assessed: List[str] = []
    time_limit_minutes: Optional[int] = Field(None, gt=0)
    passing_score: int = Field(..., ge=0, le=100)


class AssessmentResponse(BaseModel):
    # schema for assessment response
    id: UUID
    title: str
    description: Optional[str] = None
    is_diagnostic: bool
    skills_assessed: List[str]
    time_limit_minutes: Optional[int]
    passing_score: int
    created_at: datetime

    class Config:
        from_attributes = True


# question schemas