from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models.social import DiscussionCategory


# ==================== COURSE REVIEWS ====================

class CourseReviewBase(BaseModel):
    """Base schema for course reviews"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    title: Optional[str] = Field(None, max_length=200)
    review_text: Optional[str] = None


class CourseReviewCreate(CourseReviewBase):
    """Schema for creating a course review"""
    pass


class CourseReviewUpdate(BaseModel):
    """Schema for updating a course review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    review_text: Optional[str] = None


class CourseReviewResponse(CourseReviewBase):
    """Schema for course review response"""
    id: UUID
    course_id: UUID
    user_id: UUID
    helpful_count: int
    not_helpful_count: int
    is_verified_purchase: bool
    instructor_response: Optional[str]
    instructor_response_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InstructorReviewResponse(BaseModel):
    """Schema for instructor response to review"""
    instructor_response: str


# ==================== CERTIFICATES ====================

class CertificateBase(BaseModel):
    """Base schema for certificates"""
    completion_percentage: float = Field(..., ge=0, le=100)
    final_grade: Optional[float] = Field(None, ge=0, le=100)
    total_hours_spent: Optional[float] = Field(None, ge=0)
    skills_achieved: List[str] = []


class CertificateCreate(CertificateBase):
    """Schema for creating a certificate"""
    pass


class CertificateResponse(CertificateBase):
    """Schema for certificate response"""
    id: UUID
    user_id: UUID
    course_id: UUID
    certificate_number: str
    issued_date: datetime
    certificate_url: Optional[str]
    verification_url: Optional[str]
    is_revoked: bool
    revoked_at: Optional[datetime]
    revoked_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CertificateVerification(BaseModel):
    """Schema for public certificate verification"""
    certificate_number: str
    user_name: str
    course_title: str
    issued_date: datetime
    is_valid: bool
    completion_percentage: float
    skills_achieved: List[str]


# ==================== DISCUSSIONS ====================

class DiscussionBase(BaseModel):
    """Base schema for discussions"""
    title: str = Field(..., min_length=5, max_length=300)
    content: str = Field(..., min_length=10)
    category: DiscussionCategory = DiscussionCategory.GENERAL
    tags: List[str] = []


class DiscussionCreate(DiscussionBase):
    """Schema for creating a discussion"""
    lesson_id: Optional[UUID] = None


class DiscussionUpdate(BaseModel):
    """Schema for updating a discussion"""
    title: Optional[str] = Field(None, min_length=5, max_length=300)
    content: Optional[str] = Field(None, min_length=10)
    category: Optional[DiscussionCategory] = None
    tags: Optional[List[str]] = None
    is_resolved: Optional[bool] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None


class DiscussionResponse(DiscussionBase):
    """Schema for discussion response"""
    id: UUID
    course_id: UUID
    lesson_id: Optional[UUID]
    user_id: UUID
    is_pinned: bool
    is_resolved: bool
    is_locked: bool
    views_count: int
    reply_count: int
    upvotes: int
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    
    class Config:
        from_attributes = True


class DiscussionListResponse(BaseModel):
    """Schema for listing discussions (summary view)"""
    id: UUID
    title: str
    category: DiscussionCategory
    user_id: UUID
    is_pinned: bool
    is_resolved: bool
    views_count: int
    reply_count: int
    upvotes: int
    created_at: datetime
    last_activity_at: datetime
    tags: List[str]
    
    class Config:
        from_attributes = True


# ==================== DISCUSSION REPLIES ====================

class DiscussionReplyBase(BaseModel):
    """Base schema for discussion replies"""
    content: str = Field(..., min_length=1)


class DiscussionReplyCreate(DiscussionReplyBase):
    """Schema for creating a discussion reply"""
    parent_reply_id: Optional[UUID] = None


class DiscussionReplyUpdate(BaseModel):
    """Schema for updating a discussion reply"""
    content: str = Field(..., min_length=1)


class DiscussionReplyResponse(DiscussionReplyBase):
    """Schema for discussion reply response"""
    id: UUID
    discussion_id: UUID
    user_id: UUID
    parent_reply_id: Optional[UUID]
    is_instructor_response: bool
    is_accepted_answer: bool
    upvotes: int
    is_edited: bool
    edited_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
