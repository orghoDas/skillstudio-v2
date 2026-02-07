"""Pydantic schemas for live class functionality"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# Live Class Session Schemas
class LiveClassCreate(BaseModel):
    course_id: uuid.UUID
    title: str
    description: Optional[str] = None
    scheduled_start: datetime
    scheduled_end: datetime
    max_participants: Optional[int] = None
    is_recorded: bool = False
    metadata: Optional[Dict[str, Any]] = None


class LiveClassUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    max_participants: Optional[int] = None
    is_recorded: Optional[bool] = None
    meeting_url: Optional[str] = None
    recording_url: Optional[str] = None


class LiveClassResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    instructor_id: uuid.UUID
    title: str
    description: Optional[str]
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    meeting_url: Optional[str]
    meeting_id: Optional[str]
    meeting_password: Optional[str]
    recording_url: Optional[str]
    is_recorded: bool
    max_participants: Optional[int]
    current_participants: int
    chat_room_id: Optional[uuid.UUID]
    status: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LiveClassListResponse(BaseModel):
    sessions: List[LiveClassResponse]
    total: int
    skip: int
    limit: int


# Attendee Schemas
class AttendeeResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: Optional[datetime]
    left_at: Optional[datetime]
    duration_minutes: int
    questions_asked: int
    is_hand_raised: bool
    is_muted: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class JoinSessionResponse(BaseModel):
    session: LiveClassResponse
    meeting_url: Optional[str]
    chat_room_id: Optional[uuid.UUID]
