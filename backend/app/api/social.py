from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_active_instructor
from app.models import (
    User,
    Course,
    Enrollment,
    CourseReview,
    Certificate,
    Discussion,
    DiscussionReply,
    Lesson
)
from app.schemas.social import (
    CourseReviewCreate,
    CourseReviewUpdate,
    CourseReviewResponse,
    InstructorReviewResponse,
    CertificateCreate,
    CertificateResponse,
    CertificateVerification,
    DiscussionCreate,
    DiscussionUpdate,
    DiscussionResponse,
    DiscussionListResponse,
    DiscussionReplyCreate,
    DiscussionReplyUpdate,
    DiscussionReplyResponse
)

router = APIRouter(prefix="/social", tags=["social"])


# ==================== COURSE REVIEWS ====================

@router.post('/courses/{course_id}/reviews', response_model=CourseReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    course_id: UUID,
    review_data: CourseReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a course review - only enrolled students can review"""
    
    # Check if course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    # Check if user is enrolled
    result = await db.execute(
        select(Enrollment).where(
            and_(Enrollment.user_id == current_user.id, Enrollment.course_id == course_id)
        )
    )
    enrollment = result.scalar_one_or_none()
    
    # Check if already reviewed
    result = await db.execute(
        select(CourseReview).where(
            and_(CourseReview.user_id == current_user.id, CourseReview.course_id == course_id)
        )
    )
    existing_review = result.scalar_one_or_none()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reviewed this course")
    
    new_review = CourseReview(
        course_id=course_id,
        user_id=current_user.id,
        rating=review_data.rating,
        title=review_data.title,
        review_text=review_data.review_text,
        is_verified_purchase=enrollment is not None
    )
    
    db.add(new_review)
    
    # Update course average rating
    result = await db.execute(
        select(func.avg(CourseReview.rating)).where(CourseReview.course_id == course_id)
    )
    avg_rating = result.scalar()
    course.average_rating = round(avg_rating, 2) if avg_rating else None
    
    await db.commit()
    await db.refresh(new_review)
    
    return new_review


@router.get('/courses/{course_id}/reviews', response_model=List[CourseReviewResponse])
async def get_course_reviews(
    course_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("recent", regex="^(recent|helpful|rating)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews for a course"""
    
    query = select(CourseReview).where(CourseReview.course_id == course_id)
    
    # Apply sorting
    if sort_by == "recent":
        query = query.order_by(CourseReview.created_at.desc())
    elif sort_by == "helpful":
        query = query.order_by(CourseReview.helpful_count.desc())
    elif sort_by == "rating":
        query = query.order_by(CourseReview.rating.desc())
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return reviews


@router.put('/reviews/{review_id}', response_model=CourseReviewResponse)
async def update_review(
    review_id: UUID,
    review_data: CourseReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update own review"""
    
    result = await db.execute(select(CourseReview).where(CourseReview.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this review")
    
    update_data = review_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    # Recalculate course average rating if rating changed
    if 'rating' in update_data:
        result = await db.execute(
            select(func.avg(CourseReview.rating)).where(CourseReview.course_id == review.course_id)
        )
        avg_rating = result.scalar()
        result = await db.execute(select(Course).where(Course.id == review.course_id))
        course = result.scalar_one()
        course.average_rating = round(avg_rating, 2) if avg_rating else None
    
    await db.commit()
    await db.refresh(review)
    
    return review


@router.delete('/reviews/{review_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete own review"""
    
    result = await db.execute(select(CourseReview).where(CourseReview.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this review")
    
    course_id = review.course_id
    await db.delete(review)
    
    # Recalculate course average rating
    result = await db.execute(
        select(func.avg(CourseReview.rating)).where(CourseReview.course_id == course_id)
    )
    avg_rating = result.scalar()
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one()
    course.average_rating = round(avg_rating, 2) if avg_rating else None
    
    await db.commit()


@router.post('/reviews/{review_id}/instructor-response', response_model=CourseReviewResponse)
async def respond_to_review(
    review_id: UUID,
    response_data: InstructorReviewResponse,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Instructor response to review"""
    
    result = await db.execute(select(CourseReview).where(CourseReview.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    # Check if instructor owns the course
    result = await db.execute(select(Course).where(Course.id == review.course_id))
    course = result.scalar_one()
    
    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    review.instructor_response = response_data.instructor_response
    review.instructor_response_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(review)
    
    return review


@router.post('/reviews/{review_id}/helpful', response_model=CourseReviewResponse)
async def mark_review_helpful(
    review_id: UUID,
    helpful: bool = Query(..., description="True for helpful, False for not helpful"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark review as helpful or not helpful"""
    
    result = await db.execute(select(CourseReview).where(CourseReview.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if helpful:
        review.helpful_count += 1
    else:
        review.not_helpful_count += 1
    
    await db.commit()
    await db.refresh(review)
    
    return review


# ==================== CERTIFICATES ====================

@router.post('/certificates/generate/{course_id}', response_model=CertificateResponse, status_code=status.HTTP_201_CREATED, deprecated=True)
async def generate_certificate(
    course_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    [DEPRECATED] Generate certificate for course completion
    
    This endpoint is deprecated. Please use POST /certificates/generate/{enrollment_id} instead,
    which generates actual PDF certificates and provides better validation.
    
    This endpoint creates a Certificate database record using course_id,
    while the preferred endpoint uses enrollment_id for more precise tracking.
    """
    
    # Check if already has certificate
    result = await db.execute(
        select(Certificate).where(
            and_(Certificate.user_id == current_user.id, Certificate.course_id == course_id)
        )
    )
    existing_cert = result.scalar_one_or_none()
    if existing_cert and not existing_cert.is_revoked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificate already exists")
    
    # Check enrollment and completion
    result = await db.execute(
        select(Enrollment).where(
            and_(Enrollment.user_id == current_user.id, Enrollment.course_id == course_id)
        )
    )
    enrollment = result.scalar_one_or_none()
    
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not enrolled in this course")
    
    if enrollment.completion_percentage < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course not completed. Current progress: {enrollment.completion_percentage}%"
        )
    
    # Generate certificate number
    cert_number = f"CERT-{datetime.utcnow().year}-{str(uuid.uuid4())[:8].upper()}"
    
    new_certificate = Certificate(
        user_id=current_user.id,
        course_id=course_id,
        certificate_number=cert_number,
        completion_percentage=enrollment.completion_percentage,
        final_grade=enrollment.final_grade,
        total_hours_spent=enrollment.total_time_spent_hours,
        skills_achieved=[],  # TODO: Extract from course
        verification_url=f"/api/v1/social/certificates/verify/{cert_number}"
    )
    
    db.add(new_certificate)
    await db.commit()
    await db.refresh(new_certificate)
    
    return new_certificate


@router.get('/certificates/my', response_model=List[CertificateResponse])
async def get_my_certificates(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all certificates for current user"""
    
    result = await db.execute(
        select(Certificate).where(
            and_(Certificate.user_id == current_user.id, Certificate.is_revoked == False)
        ).order_by(Certificate.issued_date.desc())
    )
    certificates = result.scalars().all()
    
    return certificates


@router.get('/certificates/verify/{certificate_number}', response_model=CertificateVerification)
async def verify_certificate(
    certificate_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Public endpoint to verify certificate authenticity"""
    
    result = await db.execute(
        select(Certificate, User, Course).join(User).join(Course).where(
            Certificate.certificate_number == certificate_number
        )
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    
    cert, user, course = row
    
    return CertificateVerification(
        certificate_number=cert.certificate_number,
        user_name=user.full_name,
        course_title=course.title,
        issued_date=cert.issued_date,
        is_valid=not cert.is_revoked,
        completion_percentage=float(cert.completion_percentage),
        skills_achieved=cert.skills_achieved
    )


# ==================== DISCUSSIONS ====================

@router.post('/courses/{course_id}/discussions', response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
async def create_discussion(
    course_id: UUID,
    discussion_data: DiscussionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new discussion thread"""
    
    # Check if course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    # If lesson_id provided, check if it exists and belongs to course
    if discussion_data.lesson_id:
        result = await db.execute(select(Lesson).where(Lesson.id == discussion_data.lesson_id))
        lesson = result.scalar_one_or_none()
        if not lesson:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    
    new_discussion = Discussion(
        course_id=course_id,
        lesson_id=discussion_data.lesson_id,
        user_id=current_user.id,
        title=discussion_data.title,
        content=discussion_data.content,
        category=discussion_data.category,
        tags=discussion_data.tags
    )
    
    db.add(new_discussion)
    await db.commit()
    await db.refresh(new_discussion)
    
    return new_discussion


@router.get('/courses/{course_id}/discussions', response_model=List[DiscussionListResponse])
async def get_course_discussions(
    course_id: UUID,
    category: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all discussions for a course"""
    
    query = select(Discussion).where(Discussion.course_id == course_id)
    
    if category:
        query = query.where(Discussion.category == category)
    
    if is_resolved is not None:
        query = query.where(Discussion.is_resolved == is_resolved)
    
    # Pinned first, then by last activity
    query = query.order_by(Discussion.is_pinned.desc(), Discussion.last_activity_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    discussions = result.scalars().all()
    
    return discussions


@router.get('/discussions/{discussion_id}', response_model=DiscussionResponse)
async def get_discussion(
    discussion_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a single discussion thread"""
    
    result = await db.execute(select(Discussion).where(Discussion.id == discussion_id))
    discussion = result.scalar_one_or_none()
    
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")
    
    # Increment views
    discussion.views_count += 1
    await db.commit()
    await db.refresh(discussion)
    
    return discussion


@router.put('/discussions/{discussion_id}', response_model=DiscussionResponse)
async def update_discussion(
    discussion_id: UUID,
    discussion_data: DiscussionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a discussion - owner or instructor only"""
    
    result = await db.execute(select(Discussion).where(Discussion.id == discussion_id))
    discussion = result.scalar_one_or_none()
    
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")
    
    # Check permissions
    is_owner = discussion.user_id == current_user.id
    
    # Get course to check if user is instructor
    result = await db.execute(select(Course).where(Course.id == discussion.course_id))
    course = result.scalar_one()
    is_instructor = course.created_by == current_user.id
    
    if not (is_owner or is_instructor):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    update_data = discussion_data.dict(exclude_unset=True)
    
    # Only instructors can pin/lock
    if not is_instructor:
        update_data.pop('is_pinned', None)
        update_data.pop('is_locked', None)
    
    for field, value in update_data.items():
        setattr(discussion, field, value)
    
    await db.commit()
    await db.refresh(discussion)
    
    return discussion


@router.post('/discussions/{discussion_id}/replies', response_model=DiscussionReplyResponse, status_code=status.HTTP_201_CREATED)
async def create_reply(
    discussion_id: UUID,
    reply_data: DiscussionReplyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Reply to a discussion"""
    
    result = await db.execute(select(Discussion).where(Discussion.id == discussion_id))
    discussion = result.scalar_one_or_none()
    
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")
    
    if discussion.is_locked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discussion is locked")
    
    # Check if user is instructor
    result = await db.execute(select(Course).where(Course.id == discussion.course_id))
    course = result.scalar_one()
    is_instructor = course.created_by == current_user.id
    
    new_reply = DiscussionReply(
        discussion_id=discussion_id,
        user_id=current_user.id,
        parent_reply_id=reply_data.parent_reply_id,
        content=reply_data.content,
        is_instructor_response=is_instructor
    )
    
    db.add(new_reply)
    
    # Update discussion reply count and last activity
    discussion.reply_count += 1
    discussion.last_activity_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(new_reply)
    
    return new_reply


@router.get('/discussions/{discussion_id}/replies', response_model=List[DiscussionReplyResponse])
async def get_replies(
    discussion_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all replies for a discussion"""
    
    result = await db.execute(
        select(DiscussionReply).where(DiscussionReply.discussion_id == discussion_id).order_by(DiscussionReply.created_at.asc())
    )
    replies = result.scalars().all()
    
    return replies


@router.post('/discussions/{discussion_id}/upvote', response_model=DiscussionResponse)
async def upvote_discussion(
    discussion_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upvote a discussion"""
    
    result = await db.execute(select(Discussion).where(Discussion.id == discussion_id))
    discussion = result.scalar_one_or_none()
    
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")
    
    discussion.upvotes += 1
    
    await db.commit()
    await db.refresh(discussion)
    
    return discussion


import uuid
