from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseResponse

router = APIRouter()


@router.get("/courses")
async def search_courses(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    level: Optional[str] = Query(None, description="Filter by level (beginner, intermediate, advanced)"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    min_rating: Optional[float] = Query(None, description="Minimum average rating"),
    min_duration: Optional[int] = Query(None, description="Minimum duration in hours"),
    max_duration: Optional[int] = Query(None, description="Maximum duration in hours"),
    is_free: Optional[bool] = Query(None, description="Filter for free courses"),
    is_certified: Optional[bool] = Query(None, description="Filter for certified courses"),
    instructor_id: Optional[str] = Query(None, description="Filter by instructor ID"),
    sort_by: Optional[str] = Query("relevance", description="Sort by: relevance, popular, rating, newest, price_low, price_high"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Search courses with advanced filters and sorting
    """
    # Base query
    stmt = select(Course).where(Course.is_published == True)
    
    # Search query filter
    if query:
        search_filter = or_(
            Course.title.ilike(f"%{query}%"),
            Course.description.ilike(f"%{query}%"),
            Course.what_you_will_learn.ilike(f"%{query}%"),
            Course.requirements.ilike(f"%{query}%"),
        )
        stmt = stmt.where(search_filter)
    
    # Category filter
    if category:
        stmt = stmt.where(Course.category == category)
    
    # Level filter
    if level:
        stmt = stmt.where(Course.level == level)
    
    # Price filters
    if is_free is not None:
        if is_free:
            # Free courses (assuming pricing relationship exists)
            stmt = stmt.join(Course.pricing, isouter=True).where(
                or_(
                    Course.pricing == None,
                    Course.pricing.has(is_free=True)
                )
            )
        else:
            # Paid courses
            stmt = stmt.join(Course.pricing).where(
                Course.pricing.has(is_free=False)
            )
    
    # Instructor filter
    if instructor_id:
        stmt = stmt.where(Course.instructor_id == instructor_id)
    
    # Rating filter
    if min_rating is not None:
        stmt = stmt.where(Course.average_rating >= min_rating)
    
    # Certified filter
    if is_certified is not None:
        stmt = stmt.where(Course.is_certified == is_certified)
    
    # Sorting
    if sort_by == "popular":
        stmt = stmt.order_by(Course.enrollment_count.desc())
    elif sort_by == "rating":
        stmt = stmt.order_by(Course.average_rating.desc(), Course.enrollment_count.desc())
    elif sort_by == "newest":
        stmt = stmt.order_by(Course.created_at.desc())
    elif sort_by == "price_low":
        stmt = stmt.join(Course.pricing, isouter=True).order_by(
            Course.pricing.has(base_price=0),
            Course.pricing.has(base_price=None)
        )
    elif sort_by == "price_high":
        stmt = stmt.join(Course.pricing, isouter=True).order_by(
            Course.pricing.has(base_price=None),
            func.coalesce(Course.pricing.has(base_price=0), 0).desc()
        )
    else:  # relevance (default)
        if query:
            # Order by title match first, then enrollment count
            stmt = stmt.order_by(
                Course.title.ilike(f"%{query}%").desc(),
                Course.enrollment_count.desc()
            )
        else:
            stmt = stmt.order_by(Course.enrollment_count.desc())
    
    # Count total results
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Apply pagination
    stmt = stmt.limit(limit).offset(offset)
    
    # Execute query
    result = await db.execute(stmt)
    courses = result.scalars().all()
    
    return {
        "courses": [CourseResponse.model_validate(course) for course in courses],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(courses) < total,
    }


@router.get("/instructors")
async def search_instructors(
    query: Optional[str] = Query(None, description="Search query"),
    min_rating: Optional[float] = Query(None, description="Minimum average rating"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Search instructors
    """
    stmt = select(User).where(User.role == "instructor")
    
    if query:
        search_filter = or_(
            User.full_name.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%"),
        )
        stmt = stmt.where(search_filter)
    
    stmt = stmt.order_by(User.created_at.desc())
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Pagination
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    instructors = result.scalars().all()
    
    return {
        "instructors": [
            {
                "id": str(instructor.id),
                "full_name": instructor.full_name,
                "email": instructor.email,
                "created_at": instructor.created_at.isoformat() if instructor.created_at else None,
            }
            for instructor in instructors
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(instructors) < total,
    }


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get search suggestions/autocomplete
    """
    # Search for course titles
    stmt = select(Course.title, Course.id).where(
        and_(
            Course.is_published == True,
            Course.title.ilike(f"%{query}%")
        )
    ).limit(limit)
    
    result = await db.execute(stmt)
    courses = result.all()
    
    return {
        "suggestions": [
            {
                "type": "course",
                "title": course.title,
                "id": str(course.id),
            }
            for course in courses
        ]
    }


@router.get("/categories")
async def get_popular_categories(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get popular categories with course counts
    """
    stmt = select(
        Course.category,
        func.count(Course.id).label("course_count")
    ).where(
        and_(
            Course.is_published == True,
            Course.category.isnot(None)
        )
    ).group_by(Course.category).order_by(func.count(Course.id).desc()).limit(limit)
    
    result = await db.execute(stmt)
    categories = result.all()
    
    return {
        "categories": [
            {
                "name": cat.category,
                "course_count": cat.course_count,
            }
            for cat in categories
        ]
    }
