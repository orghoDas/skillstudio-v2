"""Collaborative code editing API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.websocket_manager import manager
from app.models.user import User
from app.models.realtime import (
    CollaborativeSession, CollaborativeParticipant
)
from app.schemas.collaborative import (
    CollaborativeSessionCreate, CollaborativeSessionUpdate,
    CollaborativeSessionResponse, CollaborativeSessionListResponse,
    ParticipantResponse, CodeUpdateMessage
)

router = APIRouter(prefix="/collaborative", tags=["Collaborative Editing"])


# WebSocket endpoint for real-time collaborative editing
@router.websocket("/ws/{session_id}")
async def collaborative_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time collaborative code editing"""
    try:
        # Verify user (simplified - use proper JWT validation in production)
        user_id = token  # Placeholder
        
        # Verify session access
        result = await db.execute(
            select(CollaborativeSession).where(
                CollaborativeSession.id == uuid.UUID(session_id)
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return
        
        # Check if user has access
        if not session.is_public:
            participant_result = await db.execute(
                select(CollaborativeParticipant).where(
                    and_(
                        CollaborativeParticipant.session_id == uuid.UUID(session_id),
                        CollaborativeParticipant.user_id == uuid.UUID(user_id)
                    )
                )
            )
            participant = participant_result.scalar_one_or_none()
            
            if not participant and session.owner_id != uuid.UUID(user_id):
                await websocket.close(code=1008, reason="Access denied")
                return
        else:
            # Create participant record for public session
            participant = CollaborativeParticipant(
                id=uuid.uuid4(),
                session_id=uuid.UUID(session_id),
                user_id=uuid.UUID(user_id),
                is_active=True
            )
            db.add(participant)
            await db.commit()
        
        # Accept connection
        await manager.connect(websocket, user_id)
        await manager.join_room(websocket, session_id)
        
        # Update participant status
        if participant:
            participant.is_active = True
            participant.last_active_at = datetime.utcnow()
            await db.commit()
        
        # Notify room
        await manager.broadcast_to_room(
            {
                "type": "user_joined",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            session_id
        )
        
        try:
            while True:
                data = await websocket.receive_json()
                
                if data.get("type") == "code_update":
                    # Update session code
                    session.code_content = data.get("content", "")
                    session.updated_at = datetime.utcnow()
                    await db.commit()
                    
                    # Broadcast to all participants except sender
                    await manager.broadcast_to_room(
                        {
                            "type": "code_update",
                            "content": session.code_content,
                            "user_id": user_id,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        session_id,
                        exclude=websocket
                    )
                
                elif data.get("type") == "cursor_update":
                    # Update participant cursor position
                    if participant:
                        participant.cursor_position = data.get("position", {})
                        participant.last_active_at = datetime.utcnow()
                        await db.commit()
                    
                    # Broadcast cursor position
                    await manager.broadcast_to_room(
                        {
                            "type": "cursor_update",
                            "user_id": user_id,
                            "position": data.get("position", {}),
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        session_id,
                        exclude=websocket
                    )
                
                elif data.get("type") == "selection_update":
                    # Broadcast selection range
                    await manager.broadcast_to_room(
                        {
                            "type": "selection_update",
                            "user_id": user_id,
                            "selection": data.get("selection", {}),
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        session_id,
                        exclude=websocket
                    )
                
        except WebSocketDisconnect:
            # Update participant status
            if participant:
                participant.is_active = False
                await db.commit()
            
            # Notify room
            await manager.broadcast_to_room(
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                session_id
            )
            
    finally:
        manager.disconnect(websocket)
        await manager.leave_room(websocket, session_id)


@router.post("", response_model=CollaborativeSessionResponse)
async def create_session(
    session_data: CollaborativeSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new collaborative editing session"""
    session = CollaborativeSession(
        id=uuid.uuid4(),
        lesson_id=session_data.lesson_id,
        owner_id=current_user.id,
        title=session_data.title,
        description=session_data.description,
        language=session_data.language,
        code_content=session_data.code_content or "",
        max_collaborators=session_data.max_collaborators,
        is_public=session_data.is_public,
        access_code=session_data.access_code,
        metadata=session_data.metadata or {}
    )
    db.add(session)
    
    # Add owner as participant
    participant = CollaborativeParticipant(
        id=uuid.uuid4(),
        session_id=session.id,
        user_id=current_user.id,
        is_active=True
    )
    db.add(participant)
    
    await db.commit()
    await db.refresh(session)
    
    return session


@router.get("", response_model=CollaborativeSessionListResponse)
async def get_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50
):
    """Get collaborative editing sessions"""
    # Get sessions where user is participant or owner
    query = select(CollaborativeSession).join(CollaborativeParticipant).where(
        or_(
            CollaborativeParticipant.user_id == current_user.id,
            CollaborativeSession.owner_id == current_user.id
        )
    )
    
    if active_only:
        query = query.where(CollaborativeSession.is_active == True)
    
    query = query.order_by(desc(CollaborativeSession.updated_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(CollaborativeSession.id))
        .join(CollaborativeParticipant)
        .where(
            or_(
                CollaborativeParticipant.user_id == current_user.id,
                CollaborativeSession.owner_id == current_user.id
            )
        )
    )
    total = count_result.scalar()
    
    return CollaborativeSessionListResponse(
        sessions=sessions,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{session_id}", response_model=CollaborativeSessionResponse)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    access_code: Optional[str] = None
):
    """Get a collaborative editing session"""
    result = await db.execute(
        select(CollaborativeSession).where(CollaborativeSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check access
    if not session.is_public and session.owner_id != current_user.id:
        if session.access_code and access_code == session.access_code:
            # Valid access code - add as participant
            participant = CollaborativeParticipant(
                id=uuid.uuid4(),
                session_id=session_id,
                user_id=current_user.id,
                is_active=True
            )
            db.add(participant)
            await db.commit()
        else:
            # Check if already participant
            participant_result = await db.execute(
                select(CollaborativeParticipant).where(
                    and_(
                        CollaborativeParticipant.session_id == session_id,
                        CollaborativeParticipant.user_id == current_user.id
                    )
                )
            )
            if not participant_result.scalar_one_or_none():
                raise HTTPException(status_code=403, detail="Access denied")
    
    return session


@router.put("/{session_id}", response_model=CollaborativeSessionResponse)
async def update_session(
    session_id: uuid.UUID,
    session_data: CollaborativeSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a collaborative editing session (Owner only)"""
    result = await db.execute(
        select(CollaborativeSession).where(
            and_(
                CollaborativeSession.id == session_id,
                CollaborativeSession.owner_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or access denied")
    
    # Update fields
    update_data = session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    await db.commit()
    await db.refresh(session)
    
    return session


@router.get("/{session_id}/participants", response_model=List[ParticipantResponse])
async def get_participants(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all participants in a collaborative session"""
    # Verify access
    session_result = await db.execute(
        select(CollaborativeSession).where(CollaborativeSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get participants
    result = await db.execute(
        select(CollaborativeParticipant)
        .where(CollaborativeParticipant.session_id == session_id)
        .order_by(CollaborativeParticipant.joined_at)
    )
    participants = result.scalars().all()
    
    return participants


@router.delete("/{session_id}")
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a collaborative editing session (Owner only)"""
    result = await db.execute(
        select(CollaborativeSession).where(
            and_(
                CollaborativeSession.id == session_id,
                CollaborativeSession.owner_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or access denied")
    
    await db.delete(session)
    await db.commit()
    
    return {"message": "Session deleted successfully"}
