from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_active_admin
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.learning import Enrollment
from app.models.monetization import Payment, InstructorPayout, SubscriptionPlan, PayoutStatus
from app.models.social import CourseReview

router = APIRouter(prefix="/admin")


@router.get("/stats")
async def get_platform_stats(
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get platform-wide statistics for admin dashboard
    """
    # User stats
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    learners_result = await db.execute(select(func.count(User.id)).where(User.role == UserRole.LEARNER))
    total_learners = learners_result.scalar()
    
    instructors_result = await db.execute(select(func.count(User.id)).where(User.role == UserRole.INSTRUCTOR))
    total_instructors = instructors_result.scalar()
    
    # Course stats
    total_courses_result = await db.execute(select(func.count(Course.id)))
    total_courses = total_courses_result.scalar()
    
    published_courses_result = await db.execute(select(func.count(Course.id)).where(Course.is_published == True))
    published_courses = published_courses_result.scalar()
    
    # Enrollment stats
    total_enrollments_result = await db.execute(select(func.count(Enrollment.id)))
    total_enrollments = total_enrollments_result.scalar()
    
    # Revenue stats
    total_revenue_result = await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == 'completed')
    )
    total_revenue = total_revenue_result.scalar() or 0
    
    # This month's revenue
    first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_revenue_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.status == 'completed',
                Payment.created_at >= first_of_month
            )
        )
    )
    month_revenue = month_revenue_result.scalar() or 0
    
    # Pending payouts
    pending_payouts_result = await db.execute(
        select(func.sum(InstructorPayout.amount)).where(InstructorPayout.status == PayoutStatus.PENDING)
    )
    pending_payouts = pending_payouts_result.scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "learners": total_learners,
            "instructors": total_instructors,
        },
        "courses": {
            "total": total_courses,
            "published": published_courses,
            "draft": total_courses - published_courses,
        },
        "enrollments": {
            "total": total_enrollments,
        },
        "revenue": {
            "total": float(total_revenue),
            "this_month": float(month_revenue),
            "pending_payouts": float(pending_payouts),
        },
    }


@router.get("/users")
async def get_all_users(
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all users with filtering
    """
    stmt = select(User)
    
    if role:
        stmt = stmt.where(User.role == role)
    
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    
    if search:
        search_filter = or_(
            User.full_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%")
        )
        stmt = stmt.where(search_filter)
    
    stmt = stmt.order_by(User.created_at.desc())
    
    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Pagination
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "email_verified": user.email_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
            for user in users
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: UserRole,
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a user's role
    """
    user_uuid = uuid.UUID(user_id)
    
    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = role
    await db.commit()
    
    return {"message": f"User role updated to {role.value}"}


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate a user account
    """
    user_uuid = uuid.UUID(user_id)
    
    stmt = update(User).where(User.id == user_uuid).values(is_active=True)
    result = await db.execute(stmt)
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User activated"}


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate a user account
    """
    user_uuid = uuid.UUID(user_id)
    
    stmt = update(User).where(User.id == user_uuid).values(is_active=False)
    result = await db.execute(stmt)
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deactivated"}


@router.get("/courses")
async def get_all_courses_admin(
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    search: Optional[str] = Query(None, description="Search by title"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all courses (admin view with unpublished courses)
    """
    stmt = select(Course)
    
    if is_published is not None:
        stmt = stmt.where(Course.is_published == is_published)
    
    if search:
        stmt = stmt.where(Course.title.ilike(f"%{search}%"))
    
    stmt = stmt.order_by(Course.created_at.desc())
    
    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Pagination
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    courses = result.scalars().all()
    
    return {
        "courses": [
            {
                "id": str(course.id),
                "title": course.title,
                "instructor_id": str(course.instructor_id),
                "is_published": course.is_published,
                "is_certified": course.is_certified,
                "enrollment_count": course.enrollment_count,
                "average_rating": course.average_rating,
                "created_at": course.created_at.isoformat() if course.created_at else None,
            }
            for course in courses
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.delete("/courses/{course_id}")
async def delete_course_admin(
    course_id: str,
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a course (admin only)
    """
    course_uuid = uuid.UUID(course_id)
    
    stmt = select(Course).where(Course.id == course_uuid)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    await db.delete(course)
    await db.commit()
    
    return {"message": "Course deleted"}


@router.get("/payouts")
async def get_all_payouts(
    status: Optional[PayoutStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all payout requests
    """
    stmt = select(InstructorPayout)
    
    if status:
        stmt = stmt.where(InstructorPayout.status == status)
    
    stmt = stmt.order_by(InstructorPayout.requested_at.desc())
    
    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Pagination
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    payouts = result.scalars().all()
    
    return {
        "payouts": [
            {
                "id": str(payout.id),
                "instructor_id": str(payout.instructor_id),
                "amount": float(payout.amount),
                "currency": payout.currency,
                "status": payout.status.value,
                "payout_method": payout.payout_method,
                "requested_at": payout.requested_at.isoformat() if payout.requested_at else None,
                "completed_at": payout.completed_at.isoformat() if payout.completed_at else None,
            }
            for payout in payouts
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.put("/payouts/{payout_id}/approve")
async def approve_payout(
    payout_id: str,
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve a payout request
    """
    payout_uuid = uuid.UUID(payout_id)
    
    stmt = select(InstructorPayout).where(InstructorPayout.id == payout_uuid)
    result = await db.execute(stmt)
    payout = result.scalar_one_or_none()
    
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    payout.status = PayoutStatus.PROCESSING
    payout.processed_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Payout approved and processing"}


@router.put("/payouts/{payout_id}/complete")
async def complete_payout(
    payout_id: str,
    transaction_reference: str,
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a payout as completed
    """
    payout_uuid = uuid.UUID(payout_id)
    
    stmt = select(InstructorPayout).where(InstructorPayout.id == payout_uuid)
    result = await db.execute(stmt)
    payout = result.scalar_one_or_none()
    
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    payout.status = PayoutStatus.COMPLETED
    payout.transaction_reference = transaction_reference
    payout.completed_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Payout marked as completed"}


@router.put("/payouts/{payout_id}/reject")
async def reject_payout(
    payout_id: str,
    reason: str,
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Reject a payout request
    """
    payout_uuid = uuid.UUID(payout_id)
    
    stmt = select(InstructorPayout).where(InstructorPayout.id == payout_uuid)
    result = await db.execute(stmt)
    payout = result.scalar_one_or_none()
    
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    payout.status = PayoutStatus.CANCELLED
    payout.failed_reason = reason
    payout.admin_notes = reason
    
    await db.commit()
    
    return {"message": "Payout rejected"}


@router.get("/reviews/reported")
async def get_reported_reviews(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get reported/flagged reviews for moderation
    """
    # This would require a reported flag on CourseReview model
    # For now, return all 1-star reviews as potentially problematic
    stmt = select(CourseReview).where(CourseReview.rating <= 2).order_by(CourseReview.created_at.desc())
    
    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Pagination
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    reviews = result.scalars().all()
    
    return {
        "reviews": [
            {
                "id": str(review.id),
                "course_id": str(review.course_id),
                "user_id": str(review.user_id),
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat() if review.created_at else None,
            }
            for review in reviews
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
