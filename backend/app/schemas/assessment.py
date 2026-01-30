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
class QuestionCreate(BaseModel):
    # schema for creating a question
    question_text: str  = Field(..., min_length=10)
    question_type: str = Field(..., pattern="^(mcq|true_false|code)$")
    options: Optional[List[Dict[str, str]]] = None
    correct_answer: Dict[str, Any]
    explanation: Optional[str] = None
    difficulty_level: int = Field(5, ge=1, le=10)
    points: int = Field(..., ge=1)
    skill_tags: List[str] = []
    sequence_order: int = Field(..., ge=1)


class QuestionResponse(BaseModel):
    # schema for question response
    id: UUID
    question_text: str
    question_type: str
    options: Optional[List[Dict[str, str]]]
    difficulty_level: int
    points: int
    skill_tags: List[str]
    sequence_order: int

    class Config:
        from_attributes = True


class QuestionWithAnswer(QuestionResponse):
    # schema for question response including correct answer
    correct_answer: Dict[str, Any]
    explanation: Optional[str]


# attempt schemas
class SubmitAnswerRequest(BaseModel):
    # schema for submitting an answer
    answers: List[Dict[str, Any]]  # List of {question_id: UUID, answer: Any}


class AssessmentAttemptResponse(BaseModel):
    # schema for assessment attempt response
    id: UUID
    assessment_id: UUID
    score_percentage: float
    points_earned: int
    points_possible: int
    time_taken_seconds: int
    skill_scores: Optional[Dict[str, float]] 
    attempt_number: int
    passed: bool
    feedback: Optional[str]
    attempted_at: datetime
    answers: List[Dict[str, Any]]  # List of {question_id: UUID, given_answer: Any, correct: bool}

    class Config:
        from_attributes = True


class DiagnosticResultResponse(BaseModel):
    # schema for diagnostic result response with profiling
    attempt: AssessmentAttemptResponse
    skill_levels: Dict[str, int]
    knowledge_gaps: List[str]
    recommended_courses: List[UUID]
    suggested_learning_path: List[Dict[str, Any]]  # List of {course_id: UUID, reason: str} 
    