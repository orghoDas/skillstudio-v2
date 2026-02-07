"""Pydantic schemas for chat functionality"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.realtime import ChatRoomType, MessageType


# Chat Room Schemas
class ChatRoomCreate(BaseModel):
    name: Optional[str] = None
    room_type: ChatRoomType
    course_id: Optional[uuid.UUID] = None
    max_participants: Optional[int] = None
    participant_ids: Optional[List[uuid.UUID]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRoomResponse(BaseModel):
    id: uuid.UUID
    name: Optional[str]
    room_type: ChatRoomType
    course_id: Optional[uuid.UUID]
    is_active: bool
    max_participants: Optional[int]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ChatRoomListResponse(BaseModel):
    rooms: List[ChatRoomResponse]
    total: int
    skip: int
    limit: int


# Chat Message Schemas
class ChatMessageCreate(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    reply_to_id: Optional[uuid.UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    sender_id: uuid.UUID
    message_type: MessageType
    content: str
    metadata: Dict[str, Any]
    is_edited: bool
    edited_at: Optional[datetime]
    is_deleted: bool
    deleted_at: Optional[datetime]
    reply_to_id: Optional[uuid.UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessageListResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total: int
    skip: int
    limit: int


# Chat Participant Schemas
class ChatParticipantResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime
    last_read_at: Optional[datetime]
    is_online: bool
    is_muted: bool
    
    class Config:
        from_attributes = True


# WebSocket Message Schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TypingIndicator(BaseModel):
    user_id: uuid.UUID
    room_id: uuid.UUID
    is_typing: bool


class UserPresence(BaseModel):
    user_id: uuid.UUID
    room_id: uuid.UUID
    is_online: bool
    timestamp: datetime
