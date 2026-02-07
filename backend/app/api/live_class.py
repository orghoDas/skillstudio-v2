"""Live class API endpoints for scheduling and managing live sessions"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from typing import List, Optional
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user, require_instructor
from app.core.websocket_manager import manager
from app.models.user import User
from app.models.course import Course
from app.models.realtime import (
    LiveClassSession, LiveClassAttendee, ChatRoom, ChatRoomType
)
from app.schemas.live_class import (
    LiveClassCreate, LiveClassUpdate, LiveClassResponse,
    LiveClassListResponse, AttendeeResponse, JoinSessionResponse
)

router = APIRouter(prefix="/live-classes", tags=["Live Classes"])


@router.post("", response_model=LiveClassResponse)
async def create_live_class(
    session_data: LiveClassCreate,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Schedule a new live class session (Instructors only)"""
    # Verify course ownership
    result = await db.execute(
        select(Course).where(
            and_(
                Course.id == session_data.course_id,
                Course.instructor_id == current_user.id
            )
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    # Create chat room for the live class
    chat_room = ChatRoom(
        id=uuid.uuid4(),
        name=f"Live Class: {session_data.title}",
        room_type=ChatRoomType.LIVE_CLASS,
        is_active=True
    )
    db.add(chat_room)
    await db.flush()
    
    # Create live class session
    session = LiveClassSession(
        id=uuid.uuid4(),
        course_id=session_data.course_id,
        instructor_id=current_user.id,
        title=session_data.title,
        description=session_data.description,
        scheduled_start=session_data.scheduled_start,
        scheduled_end=session_data.scheduled_end,
        max_participants=session_data.max_participants,
        chat_room_id=chat_room.id,
        is_recorded=session_data.is_recorded,
        metadata=session_data.metadata or {}
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session


@router.get("", response_model=LiveClassListResponse)
async def get_live_classes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    course_id: Optional[uuid.UUID] = None,
    upcoming: bool = True,
    skip: int = 0,
    limit: int = 50
):
    """Get live class sessions"""
    query = select(LiveClassSession)
    
    # Filter by course if specified
    if course_id:
        query = query.where(LiveClassSession.course_id == course_id)
    
    # Filter upcoming or past sessions
    if upcoming:
        query = query.where(LiveClassSession.scheduled_start >= datetime.utcnow())
        query = query.order_by(LiveClassSession.scheduled_start)
    else:
        query = query.where(LiveClassSession.scheduled_start < datetime.utcnow())
        query = query.order_by(desc(LiveClassSession.scheduled_start))
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(LiveClassSession.id))
    if course_id:
        count_query = count_query.where(LiveClassSession.course_id == course_id)
    if upcoming:
        count_query = count_query.where(LiveClassSession.scheduled_start >= datetime.utcnow())
    else:
        count_query = count_query.where(LiveClassSession.scheduled_start < datetime.utcnow())
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return LiveClassListResponse(
        sessions=sessions,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{session_id}", response_model=LiveClassResponse)
async def get_live_class(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific live class session"""
    result = await db.execute(
        select(LiveClassSession).where(LiveClassSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Live class not found")
    
    return session


@router.put("/{session_id}", response_model=LiveClassResponse)
async def update_live_class(
    session_id: uuid.UUID,
    session_data: LiveClassUpdate,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Update a live class session (Instructor only)"""
    result = await db.execute(
        select(LiveClassSession).where(
            and_(
                LiveClassSession.id == session_id,
                LiveClassSession.instructor_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Live class not found or access denied")
    
    # Update fields
    update_data = session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    await db.commit()
    await db.refresh(session)
    
    return session


@router.post("/{session_id}/start", response_model=LiveClassResponse)
async def start_live_class(
    session_id: uuid.UUID,
    meeting_url: str = Query(..., description="Video conferencing URL"),
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Start a live class session (Instructor only)"""
    result = await db.execute(
        select(LiveClassSession).where(
            and_(
                LiveClassSession.id == session_id,
                LiveClassSession.instructor_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Live class not found or access denied")
    
    if session.status == "in_progress":
        raise HTTPException(status_code=400, detail="Session already started")
    
    # Update session
    session.actual_start = datetime.utcnow()
    session.meeting_url = meeting_url
    session.status = "in_progress"
    
    await db.commit()
    await db.refresh(session)
    
    # Notify all enrolled students (via WebSocket or notification system)
    # This would integrate with your notification system
    
    return session


@router.post("/{session_id}/join", response_model=JoinSessionResponse)
async def join_live_class(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Join a live class session"""
    result = await db.execute(
        select(LiveClassSession).where(LiveClassSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Live class not found")
    
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session is not currently in progress")
    
    # Check if already joined
    attendee_result = await db.execute(
        select(LiveClassAttendee).where(
            and_(
                LiveClassAttendee.session_id == session_id,
                LiveClassAttendee.user_id == current_user.id
            )
        )
    )
    attendee = attendee_result.scalar_one_or_none()
    
    if not attendee:
        # Create new attendee record
        attendee = LiveClassAttendee(
            id=uuid.uuid4(),
            session_id=session_id,
            user_id=current_user.id,
            joined_at=datetime.utcnow()
        )
        db.add(attendee)
        
        # Increment current participants
        session.current_participants += 1
        await db.commit()
        await db.refresh(attendee)
    else:
        # Update joined timestamp
        attendee.joined_at = datetime.utcnow()
        attendee.left_at = None
        await db.commit()
    
    return JoinSessionResponse(
        session=session,
        meeting_url=session.meeting_url,
        chat_room_id=session.chat_room_id
    )


@router.post("/{session_id}/leave")
async def leave_live_class(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Leave a live class session"""
    result = await db.execute(
        select(LiveClassAttendee).where(
            and_(
                LiveClassAttendee.session_id == session_id,
                LiveClassAttendee.user_id == current_user.id
            )
        )
    )
    attendee = result.scalar_one_or_none()
    
    if not attendee:
        raise HTTPException(status_code=404, detail="Not attending this session")
    
    # Update attendee record
    attendee.left_at = datetime.utcnow()
    
    if attendee.joined_at:
        duration = (attendee.left_at - attendee.joined_at).total_seconds() / 60
        attendee.duration_minutes += int(duration)
    
    # Decrement current participants
    session_result = await db.execute(
        select(LiveClassSession).where(LiveClassSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    
    if session and session.current_participants > 0:
        session.current_participants -= 1
    
    await db.commit()
    
    return {"message": "Left session successfully"}


@router.post("/{session_id}/end", response_model=LiveClassResponse)
async def end_live_class(
    session_id: uuid.UUID,
    recording_url: Optional[str] = None,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db)
):
    """End a live class session (Instructor only)"""
    result = await db.execute(
        select(LiveClassSession).where(
            and_(
                LiveClassSession.id == session_id,
                LiveClassSession.instructor_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Live class not found or access denied")
    
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Session already ended")
    
    # Update session
    session.actual_end = datetime.utcnow()
    session.status = "completed"
    
    if recording_url:
        session.recording_url = recording_url
    
    session.current_participants = 0
    
    await db.commit()
    await db.refresh(session)
    
    return session


@router.get("/{session_id}/attendees", response_model=List[AttendeeResponse])
async def get_session_attendees(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all attendees of a live class session"""
    # Verify access (instructor or attendee)
    session_result = await db.execute(
        select(LiveClassSession).where(LiveClassSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Live class not found")
    
    # Get attendees
    result = await db.execute(
        select(LiveClassAttendee)
        .where(LiveClassAttendee.session_id == session_id)
        .order_by(LiveClassAttendee.joined_at)
    )
    attendees = result.scalars().all()
    
    return attendees


@router.delete("/{session_id}")
async def delete_live_class(
    session_id: uuid.UUID,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Delete a live class session (Instructor only)"""
    result = await db.execute(
        select(LiveClassSession).where(
            and_(
                LiveClassSession.id == session_id,
                LiveClassSession.instructor_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Live class not found or access denied")
    
    if session.status == "in_progress":
        raise HTTPException(status_code=400, detail="Cannot delete session in progress")
    
    await db.delete(session)
    await db.commit()
    
    return {"message": "Live class deleted successfully"}
