from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_active_instructor
from app.models.user import User
from app.models.course import Course
from app.models.learning import Enrollment, Progress
from pydantic import BaseModel


router = APIRouter()


# Response schemas
class InstructorStats(BaseModel):
    total_courses: int
    total_students: int
    total_enrollments: int
    published_courses: int
    draft_courses: int
    average_course_rating: float


class CourseStats(BaseModel):
    course_id: str
    course_title: str
    total_enrollments: int
    active_students: int
    completion_rate: float
    average_rating: float


class StudentEnrollment(BaseModel):
    student_id: str
    student_name: str
    student_email: str
    course_id: str
    course_title: str
    enrolled_at: datetime
    progress_percentage: float
    completed: bool
    last_accessed: datetime | None


@router.get("/stats", response_model=InstructorStats)
async def get_instructor_stats(
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall statistics for the instructor
    """
    
    # Total courses
    total_courses_result = await db.execute(
        select(func.count(Course.id)).where(Course.created_by == current_user.id)
    )
    total_courses = total_courses_result.scalar() or 0
    
    # Published vs draft
    published_result = await db.execute(
        select(func.count(Course.id)).where(
            and_(Course.created_by == current_user.id, Course.is_published == True)
        )
    )
    published_courses = published_result.scalar() or 0
    draft_courses = total_courses - published_courses
    
    # Total enrollments across all courses
    enrollments_result = await db.execute(
        select(func.count(Enrollment.id))
        .join(Course, Enrollment.course_id == Course.id)
        .where(Course.created_by == current_user.id)
    )
    total_enrollments = enrollments_result.scalar() or 0
    
    # Unique students
    students_result = await db.execute(
        select(func.count(func.distinct(Enrollment.user_id)))
        .join(Course, Enrollment.course_id == Course.id)
        .where(Course.created_by == current_user.id)
    )
    total_students = students_result.scalar() or 0
    
    # Average course rating
    avg_rating_result = await db.execute(
        select(func.avg(Course.average_rating)).where(
            and_(Course.created_by == current_user.id, Course.average_rating.isnot(None))
        )
    )
    average_course_rating = avg_rating_result.scalar() or 0.0
    
    return InstructorStats(
        total_courses=total_courses,
        total_students=total_students,
        total_enrollments=total_enrollments,
        published_courses=published_courses,
        draft_courses=draft_courses,
        average_course_rating=round(average_course_rating, 2)
    )


@router.get("/courses/stats", response_model=List[CourseStats])
async def get_courses_stats(
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics for each course created by the instructor
    """
    
    # Get all instructor's courses
    courses_result = await db.execute(
        select(Course).where(Course.created_by == current_user.id)
    )
    courses = courses_result.scalars().all()
    
    course_stats_list = []
    
    for course in courses:
        # Total enrollments
        enrollments_result = await db.execute(
            select(func.count(Enrollment.id)).where(Enrollment.course_id == course.id)
        )
        total_enrollments = enrollments_result.scalar() or 0
        
        # Active students (accessed in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_result = await db.execute(
            select(func.count(func.distinct(Enrollment.user_id)))
            .where(
                and_(
                    Enrollment.course_id == course.id,
                    Enrollment.last_accessed >= thirty_days_ago
                )
            )
        )
        active_students = active_result.scalar() or 0
        
        # Completion rate
        if total_enrollments > 0:
            completed_result = await db.execute(
                select(func.count(Enrollment.id))
                .where(
                    and_(
                        Enrollment.course_id == course.id,
                        Enrollment.completed == True
                    )
                )
            )
            completed = completed_result.scalar() or 0
            completion_rate = (completed / total_enrollments) * 100
        else:
            completion_rate = 0.0
        
        course_stats_list.append(CourseStats(
            course_id=str(course.id),
            course_title=course.title,
            total_enrollments=total_enrollments,
            active_students=active_students,
            completion_rate=round(completion_rate, 2),
            average_rating=course.average_rating or 0.0
        ))
    
    return course_stats_list


@router.get("/students", response_model=List[StudentEnrollment])
async def get_instructor_students(
    course_id: UUID | None = None,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all students enrolled in instructor's courses
    Optionally filter by specific course
    """
    
    # Build query
    query = (
        select(Enrollment, User, Course)
        .join(User, Enrollment.user_id == User.id)
        .join(Course, Enrollment.course_id == Course.id)
        .where(Course.created_by == current_user.id)
    )
    
    if course_id:
        query = query.where(Enrollment.course_id == course_id)
    
    result = await db.execute(query.order_by(Enrollment.enrolled_at.desc()))
    enrollments_data = result.all()
    
    student_enrollments = []
    
    for enrollment, user, course in enrollments_data:
        student_enrollments.append(StudentEnrollment(
            student_id=str(user.id),
            student_name=user.full_name,
            student_email=user.email,
            course_id=str(course.id),
            course_title=course.title,
            enrolled_at=enrollment.enrolled_at,
            progress_percentage=enrollment.progress_percentage,
            completed=enrollment.completed,
            last_accessed=enrollment.last_accessed
        ))
    
    return student_enrollments


@router.get("/courses/{course_id}/analytics")
async def get_course_analytics(
    course_id: UUID,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed analytics for a specific course
    """
    
    # Verify course ownership
    course_result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = course_result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Enrollment trend (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    enrollments_result = await db.execute(
        select(
            func.date(Enrollment.enrolled_at).label('date'),
            func.count(Enrollment.id).label('count')
        )
        .where(
            and_(
                Enrollment.course_id == course_id,
                Enrollment.enrolled_at >= thirty_days_ago
            )
        )
        .group_by(func.date(Enrollment.enrolled_at))
        .order_by(func.date(Enrollment.enrolled_at))
    )
    enrollment_trend = [
        {"date": str(row.date), "count": row.count}
        for row in enrollments_result.all()
    ]
    
    # Progress distribution
    progress_result = await db.execute(
        select(Enrollment.progress_percentage)
        .where(Enrollment.course_id == course_id)
    )
    progress_values = [row[0] for row in progress_result.all()]
    
    # Calculate distribution
    distribution = {
        "0-25": len([p for p in progress_values if 0 <= p < 25]),
        "25-50": len([p for p in progress_values if 25 <= p < 50]),
        "50-75": len([p for p in progress_values if 50 <= p < 75]),
        "75-100": len([p for p in progress_values if 75 <= p <= 100]),
    }
    
    return {
        "course_id": str(course_id),
        "course_title": course.title,
        "enrollment_trend": enrollment_trend,
        "progress_distribution": distribution,
        "total_enrollments": len(progress_values),
        "average_progress": sum(progress_values) / len(progress_values) if progress_values else 0
    }
