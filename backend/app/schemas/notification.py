from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.notification import NotificationType


# Notification Schemas
class NotificationBase(BaseModel):
    title: str = Field(..., max_length=255)
    message: str
    type: NotificationType
    action_url: Optional[str] = None
    meta_data: Dict[str, Any] = Field(default_factory=dict)


class NotificationCreate(NotificationBase):
    user_id: str
    course_id: Optional[str] = None
    enrollment_id: Optional[str] = None
    payment_id: Optional[str] = None
    discussion_id: Optional[str] = None


class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    course_id: Optional[str]
    enrollment_id: Optional[str]
    payment_id: Optional[str]
    discussion_id: Optional[str]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationMarkAsRead(BaseModel):
    notification_ids: list[str]


# Notification Preference Schemas
class NotificationPreferenceBase(BaseModel):
    # Email notifications
    email_course_updates: bool = True
    email_new_enrollments: bool = True
    email_course_completions: bool = True
    email_new_reviews: bool = True
    email_discussion_replies: bool = True
    email_payment_updates: bool = True
    email_payout_updates: bool = True
    email_marketing: bool = True
    
    # In-app notifications
    inapp_course_updates: bool = True
    inapp_new_enrollments: bool = True
    inapp_course_completions: bool = True
    inapp_new_reviews: bool = True
    inapp_discussion_replies: bool = True
    inapp_payment_updates: bool = True
    inapp_payout_updates: bool = True


class NotificationPreferenceUpdate(NotificationPreferenceBase):
    pass


class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
