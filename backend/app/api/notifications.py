from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.notification import Notification, NotificationPreference, NotificationType
from app.schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    NotificationMarkAsRead,
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
)

router = APIRouter(prefix="/notifications")


@router.get("/", response_model=dict)
async def get_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's notifications with pagination
    """
    stmt = select(Notification).where(Notification.user_id == current_user.id)
    
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)
    
    if type:
        stmt = stmt.where(Notification.type == type)
    
    stmt = stmt.order_by(Notification.created_at.desc())
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get unread count
    unread_stmt = select(func.count()).where(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    unread_result = await db.execute(unread_stmt)
    unread_count = unread_result.scalar()
    
    # Pagination
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    notifications = result.scalars().all()
    
    return {
        "notifications": [NotificationResponse.model_validate(n) for n in notifications],
        "total": total,
        "unread_count": unread_count,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(notifications) < total,
    }


@router.post("/mark-as-read")
async def mark_notifications_as_read(
    data: NotificationMarkAsRead,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark one or more notifications as read
    """
    notification_uuids = [uuid.UUID(nid) for nid in data.notification_ids]
    
    stmt = (
        update(Notification)
        .where(
            and_(
                Notification.id.in_(notification_uuids),
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
        .values(is_read=True, read_at=datetime.utcnow())
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return {"updated_count": result.rowcount}


@router.post("/mark-all-as-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark all notifications as read for current user
    """
    stmt = (
        update(Notification)
        .where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
        .values(is_read=True, read_at=datetime.utcnow())
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return {"updated_count": result.rowcount}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific notification
    """
    notification_uuid = uuid.UUID(notification_id)
    
    stmt = select(Notification).where(
        and_(
            Notification.id == notification_uuid,
            Notification.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    await db.delete(notification)
    await db.commit()
    
    return {"message": "Notification deleted"}


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_notification_preferences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's notification preferences
    """
    stmt = select(NotificationPreference).where(
        NotificationPreference.user_id == current_user.id
    )
    result = await db.execute(stmt)
    preferences = result.scalar_one_or_none()
    
    # Create default preferences if not exist
    if not preferences:
        preferences = NotificationPreference(user_id=current_user.id)
        db.add(preferences)
        await db.commit()
        await db.refresh(preferences)
    
    return NotificationPreferenceResponse.model_validate(preferences)


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_notification_preferences(
    data: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's notification preferences
    """
    stmt = select(NotificationPreference).where(
        NotificationPreference.user_id == current_user.id
    )
    result = await db.execute(stmt)
    preferences = result.scalar_one_or_none()
    
    if not preferences:
        preferences = NotificationPreference(user_id=current_user.id)
        db.add(preferences)
    
    # Update all fields
    for field, value in data.model_dump().items():
        setattr(preferences, field, value)
    
    preferences.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(preferences)
    
    return NotificationPreferenceResponse.model_validate(preferences)


# Helper function to create notifications (can be used by other modules)
async def create_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    type: NotificationType,
    title: str,
    message: str,
    action_url: Optional[str] = None,
    course_id: Optional[uuid.UUID] = None,
    enrollment_id: Optional[uuid.UUID] = None,
    payment_id: Optional[uuid.UUID] = None,
    discussion_id: Optional[uuid.UUID] = None,
    metadata: Optional[dict] = None,
) -> Notification:
    """
    Create a new notification
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        action_url=action_url,
        course_id=course_id,
        enrollment_id=enrollment_id,
        payment_id=payment_id,
        discussion_id=discussion_id,
        meta_data=metadata or {},
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification
