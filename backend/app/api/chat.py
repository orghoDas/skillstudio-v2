"""Chat API endpoints for real-time messaging"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.websocket_manager import manager
from app.models.user import User
from app.models.realtime import (
    ChatRoom, ChatParticipant, ChatMessage, 
    ChatRoomType, MessageType
)
from app.schemas.chat import (
    ChatRoomCreate, ChatRoomResponse, ChatRoomListResponse,
    ChatMessageCreate, ChatMessageResponse, ChatMessageListResponse,
    ChatParticipantResponse
)

router = APIRouter(prefix="/chat", tags=["Chat"])


# WebSocket endpoint for real-time chat
@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time chat in a specific room"""
    try:
        # Verify token and get user (simplified - expand with proper JWT validation)
        # In production, decode JWT token to get user_id
        user_id = token  # Placeholder - replace with actual JWT decoding
        
        # Verify user has access to this room
        result = await db.execute(
            select(ChatParticipant).where(
                and_(
                    ChatParticipant.room_id == uuid.UUID(room_id),
                    ChatParticipant.user_id == uuid.UUID(user_id)
                )
            )
        )
        participant = result.scalar_one_or_none()
        
        if not participant:
            await websocket.close(code=1008, reason="Access denied")
            return
        
        # Accept connection and join room
        await manager.connect(websocket, user_id)
        await manager.join_room(websocket, room_id)
        
        # Update participant online status
        participant.is_online = True
        await db.commit()
        
        # Notify room that user joined
        await manager.broadcast_to_room(
            {
                "type": "user_joined",
                "user_id": user_id,
                "room_id": room_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            room_id
        )
        
        try:
            while True:
                # Receive message from WebSocket
                data = await websocket.receive_json()
                
                # Handle different message types
                if data.get("type") == "message":
                    # Create message in database
                    message = ChatMessage(
                        id=uuid.uuid4(),
                        room_id=uuid.UUID(room_id),
                        sender_id=uuid.UUID(user_id),
                        message_type=MessageType.TEXT,
                        content=data.get("content", ""),
                        metadata=data.get("metadata", {})
                    )
                    db.add(message)
                    await db.commit()
                    await db.refresh(message)
                    
                    # Broadcast to room
                    await manager.broadcast_to_room(
                        {
                            "type": "new_message",
                            "message_id": str(message.id),
                            "room_id": room_id,
                            "sender_id": user_id,
                            "content": message.content,
                            "message_type": message.message_type.value,
                            "created_at": message.created_at.isoformat(),
                            "metadata": message.metadata
                        },
                        room_id
                    )
                
                elif data.get("type") == "typing":
                    # Broadcast typing indicator
                    await manager.broadcast_to_room(
                        {
                            "type": "user_typing",
                            "user_id": user_id,
                            "room_id": room_id,
                            "is_typing": data.get("is_typing", False)
                        },
                        room_id,
                        exclude=websocket
                    )
                
                elif data.get("type") == "read":
                    # Update last read timestamp
                    participant.last_read_at = datetime.utcnow()
                    await db.commit()
                    
        except WebSocketDisconnect:
            # Update participant online status
            participant.is_online = False
            await db.commit()
            
            # Notify room that user left
            await manager.broadcast_to_room(
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "room_id": room_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                room_id
            )
            
    finally:
        manager.disconnect(websocket)
        await manager.leave_room(websocket, room_id)


@router.post("/rooms", response_model=ChatRoomResponse)
async def create_chat_room(
    room_data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat room"""
    # Create room
    room = ChatRoom(
        id=uuid.uuid4(),
        name=room_data.name,
        room_type=room_data.room_type,
        course_id=room_data.course_id,
        max_participants=room_data.max_participants,
        metadata=room_data.metadata or {}
    )
    db.add(room)
    
    # Add creator as participant
    participant = ChatParticipant(
        id=uuid.uuid4(),
        room_id=room.id,
        user_id=current_user.id
    )
    db.add(participant)
    
    # Add other participants if specified
    if room_data.participant_ids:
        for user_id in room_data.participant_ids:
            if user_id != current_user.id:
                participant = ChatParticipant(
                    id=uuid.uuid4(),
                    room_id=room.id,
                    user_id=user_id
                )
                db.add(participant)
    
    await db.commit()
    await db.refresh(room)
    
    return room


@router.get("/rooms", response_model=ChatRoomListResponse)
async def get_user_chat_rooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get all chat rooms for the current user"""
    # Get rooms where user is a participant
    result = await db.execute(
        select(ChatRoom)
        .join(ChatParticipant)
        .where(ChatParticipant.user_id == current_user.id)
        .order_by(desc(ChatRoom.updated_at))
        .offset(skip)
        .limit(limit)
    )
    rooms = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(ChatRoom.id))
        .join(ChatParticipant)
        .where(ChatParticipant.user_id == current_user.id)
    )
    total = count_result.scalar()
    
    return ChatRoomListResponse(
        rooms=rooms,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/rooms/{room_id}", response_model=ChatRoomResponse)
async def get_chat_room(
    room_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific chat room"""
    # Verify user has access
    result = await db.execute(
        select(ChatParticipant).where(
            and_(
                ChatParticipant.room_id == room_id,
                ChatParticipant.user_id == current_user.id
            )
        )
    )
    participant = result.scalar_one_or_none()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Access denied to this room")
    
    # Get room
    result = await db.execute(
        select(ChatRoom).where(ChatRoom.id == room_id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return room


@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    room_id: uuid.UUID,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to a chat room"""
    # Verify user has access
    result = await db.execute(
        select(ChatParticipant).where(
            and_(
                ChatParticipant.room_id == room_id,
                ChatParticipant.user_id == current_user.id
            )
        )
    )
    participant = result.scalar_one_or_none()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Access denied to this room")
    
    # Create message
    message = ChatMessage(
        id=uuid.uuid4(),
        room_id=room_id,
        sender_id=current_user.id,
        message_type=message_data.message_type,
        content=message_data.content,
        metadata=message_data.metadata or {},
        reply_to_id=message_data.reply_to_id
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    # Broadcast via WebSocket
    await manager.broadcast_to_room(
        {
            "type": "new_message",
            "message_id": str(message.id),
            "room_id": str(room_id),
            "sender_id": str(current_user.id),
            "content": message.content,
            "message_type": message.message_type.value,
            "created_at": message.created_at.isoformat(),
            "metadata": message.metadata
        },
        str(room_id)
    )
    
    return message


@router.get("/rooms/{room_id}/messages", response_model=ChatMessageListResponse)
async def get_messages(
    room_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    before: Optional[datetime] = None
):
    """Get messages from a chat room"""
    # Verify user has access
    result = await db.execute(
        select(ChatParticipant).where(
            and_(
                ChatParticipant.room_id == room_id,
                ChatParticipant.user_id == current_user.id
            )
        )
    )
    participant = result.scalar_one_or_none()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Access denied to this room")
    
    # Build query
    query = select(ChatMessage).where(
        and_(
            ChatMessage.room_id == room_id,
            ChatMessage.is_deleted == False
        )
    )
    
    if before:
        query = query.where(ChatMessage.created_at < before)
    
    query = query.order_by(desc(ChatMessage.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(ChatMessage.id)).where(
            and_(
                ChatMessage.room_id == room_id,
                ChatMessage.is_deleted == False
            )
        )
    )
    total = count_result.scalar()
    
    return ChatMessageListResponse(
        messages=list(reversed(messages)),  # Return in chronological order
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/rooms/{room_id}/participants", response_model=List[ChatParticipantResponse])
async def get_room_participants(
    room_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all participants in a chat room"""
    # Verify user has access
    result = await db.execute(
        select(ChatParticipant).where(
            and_(
                ChatParticipant.room_id == room_id,
                ChatParticipant.user_id == current_user.id
            )
        )
    )
    participant = result.scalar_one_or_none()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Access denied to this room")
    
    # Get all participants
    result = await db.execute(
        select(ChatParticipant)
        .where(ChatParticipant.room_id == room_id)
        .order_by(ChatParticipant.joined_at)
    )
    participants = result.scalars().all()
    
    return participants


@router.delete("/rooms/{room_id}/messages/{message_id}")
async def delete_message(
    room_id: uuid.UUID,
    message_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a message (soft delete)"""
    # Get message
    result = await db.execute(
        select(ChatMessage).where(
            and_(
                ChatMessage.id == message_id,
                ChatMessage.room_id == room_id
            )
        )
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Only sender can delete their own message
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own messages")
    
    # Soft delete
    message.is_deleted = True
    message.deleted_at = datetime.utcnow()
    await db.commit()
    
    # Broadcast deletion
    await manager.broadcast_to_room(
        {
            "type": "message_deleted",
            "message_id": str(message_id),
            "room_id": str(room_id),
            "deleted_at": message.deleted_at.isoformat()
        },
        str(room_id)
    )
    
    return {"message": "Message deleted successfully"}
