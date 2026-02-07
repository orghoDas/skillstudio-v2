"""Pydantic schemas for collaborative editing"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# Collaborative Session Schemas
class CollaborativeSessionCreate(BaseModel):
    lesson_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    language: str = "python"
    code_content: Optional[str] = None
    max_collaborators: int = 10
    is_public: bool = False
    access_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CollaborativeSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    code_content: Optional[str] = None
    max_collaborators: Optional[int] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    access_code: Optional[str] = None


class CollaborativeSessionResponse(BaseModel):
    id: uuid.UUID
    lesson_id: Optional[uuid.UUID]
    owner_id: uuid.UUID
    title: str
    description: Optional[str]
    language: str
    code_content: str
    is_active: bool
    max_collaborators: int
    is_public: bool
    access_code: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CollaborativeSessionListResponse(BaseModel):
    sessions: List[CollaborativeSessionResponse]
    total: int
    skip: int
    limit: int


# Participant Schemas
class ParticipantResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    user_id: uuid.UUID
    cursor_position: Dict[str, Any]
    is_active: bool
    joined_at: datetime
    last_active_at: datetime
    
    class Config:
        from_attributes = True


# WebSocket Message Schemas
class CodeUpdateMessage(BaseModel):
    type: str = "code_update"
    content: str
    user_id: uuid.UUID
    timestamp: datetime


class CursorUpdateMessage(BaseModel):
    type: str = "cursor_update"
    user_id: uuid.UUID
    position: Dict[str, int]  # line, column
    timestamp: datetime


class SelectionUpdateMessage(BaseModel):
    type: str = "selection_update"
    user_id: uuid.UUID
    selection: Dict[str, Any]  # start, end positions
    timestamp: datetime
