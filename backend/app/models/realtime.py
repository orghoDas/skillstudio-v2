from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from app.core.database import Base


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    CODE = "code"
    SYSTEM = "system"


class ChatRoomType(str, enum.Enum):
    DIRECT = "direct"  # One-on-one chat
    COURSE = "course"  # Course discussion
    LIVE_CLASS = "live_class"  # Live class chat
    GROUP = "group"  # Group chat


class ChatRoom(Base):
    """Chat room model for real-time messaging"""
    __tablename__ = "chat_rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    room_type = Column(SQLEnum(ChatRoomType), nullable=False, default=ChatRoomType.DIRECT)
    
    # Related entities
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    live_class_id = Column(UUID(as_uuid=True), nullable=True)  # For live class sessions
    
    # Room settings
    is_active = Column(Boolean, default=True, nullable=False)
    max_participants = Column(Integer, nullable=True)  # null = unlimited
    metadata = Column(JSONB, default=dict, nullable=False)  # Extra settings
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")
    participants = relationship("ChatParticipant", back_populates="room", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_chat_room_course', 'course_id'),
        Index('idx_chat_room_type', 'room_type'),
    )


class ChatParticipant(Base):
    """Chat room participants"""
    __tablename__ = "chat_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Participant status
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_read_at = Column(DateTime(timezone=True), nullable=True)
    is_online = Column(Boolean, default=False, nullable=False)
    is_muted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    room = relationship("ChatRoom", back_populates="participants")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_chat_participant_room', 'room_id'),
        Index('idx_chat_participant_user', 'user_id'),
    )


class ChatMessage(Base):
    """Chat messages"""
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Message content
    message_type = Column(SQLEnum(MessageType), nullable=False, default=MessageType.TEXT)
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, default=dict, nullable=False)  # File URLs, code language, etc.
    
    # Message status
    is_edited = Column(Boolean, default=False, nullable=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Reply/thread support
    reply_to_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User")
    reply_to = relationship("ChatMessage", remote_side=[id])
    
    __table_args__ = (
        Index('idx_chat_message_room_created', 'room_id', 'created_at'),
        Index('idx_chat_message_sender', 'sender_id'),
    )


class LiveClassSession(Base):
    """Live class/webinar sessions"""
    __tablename__ = "live_class_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Session details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    
    # Video conferencing
    meeting_url = Column(String(512), nullable=True)  # Zoom, Jitsi, Agora link
    meeting_id = Column(String(255), nullable=True)
    meeting_password = Column(String(255), nullable=True)
    
    # Recording
    recording_url = Column(String(512), nullable=True)
    is_recorded = Column(Boolean, default=False, nullable=False)
    
    # Session metadata
    max_participants = Column(Integer, nullable=True)
    current_participants = Column(Integer, default=0, nullable=False)
    chat_room_id = Column(UUID(as_uuid=True), ForeignKey("chat_rooms.id", ondelete="SET NULL"), nullable=True)
    
    # Status
    status = Column(String(50), default="scheduled", nullable=False)  # scheduled, live, ended, cancelled
    metadata = Column(JSONB, default=dict, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    course = relationship("Course")
    instructor = relationship("User", foreign_keys=[instructor_id])
    chat_room = relationship("ChatRoom")
    attendees = relationship("LiveClassAttendee", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_live_class_course', 'course_id'),
        Index('idx_live_class_instructor', 'instructor_id'),
        Index('idx_live_class_scheduled', 'scheduled_start'),
    )


class LiveClassAttendee(Base):
    """Live class attendees"""
    __tablename__ = "live_class_attendees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("live_class_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Attendance tracking
    joined_at = Column(DateTime(timezone=True), nullable=True)
    left_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, default=0, nullable=False)
    
    # Participation
    questions_asked = Column(Integer, default=0, nullable=False)
    is_hand_raised = Column(Boolean, default=False, nullable=False)
    is_muted = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("LiveClassSession", back_populates="attendees")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_live_class_attendee_session', 'session_id'),
        Index('idx_live_class_attendee_user', 'user_id'),
    )


class CollaborativeSession(Base):
    """Collaborative code editing sessions"""
    __tablename__ = "collaborative_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Session details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(50), default="python", nullable=False)  # python, javascript, etc.
    
    # Code content
    code_content = Column(Text, default="", nullable=False)
    
    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    max_collaborators = Column(Integer, default=10, nullable=False)
    
    # Access control
    is_public = Column(Boolean, default=False, nullable=False)
    access_code = Column(String(50), nullable=True)  # Optional access code
    
    metadata = Column(JSONB, default=dict, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User")
    collaborators = relationship("CollaborativeParticipant", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_collab_session_owner', 'owner_id'),
        Index('idx_collab_session_active', 'is_active'),
    )


class CollaborativeParticipant(Base):
    """Collaborative session participants"""
    __tablename__ = "collaborative_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("collaborative_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Participant details
    cursor_position = Column(JSONB, default=dict, nullable=False)  # {line: 1, column: 0}
    is_active = Column(Boolean, default=True, nullable=False)
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_active_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("CollaborativeSession", back_populates="collaborators")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_collab_participant_session', 'session_id'),
        Index('idx_collab_participant_user', 'user_id'),
    )
