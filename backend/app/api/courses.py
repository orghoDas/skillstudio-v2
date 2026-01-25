from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_instructor
from app.models.user import User
from app.models.course import Course, Module, Lesson
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseListResponse, ModuleCreate, ModuleUpdate, ModuleResponse, LessonCreate, LessonUpdate, LessonResponse


router = APIRouter()


# course endpoints
@router.post('/', response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # create a new course (instructor only)
    new_course = Course(
        title = course_data.title,
        description = course_data.description,
        short_description = course_data.short_description,
        difficulty_level = course_data.difficulty_level,
        est_duration_hours = course_data.est_duration_hours,
        skills_taught = course_data.skills_taught,
        prerequisites = course_data.prerequisites,
        thumbnail_url = course_data.thumbnail_url,
        created_by = current_user.id
    )

    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)

    return new_course


@router.get('/', response_model=List[CourseListResponse])
async def list_courses(
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100),
    difficulty: Optional[str] = None,
    published_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    
    # list all courses with optional filters/
    query = select(Course)

    if published_only:
        query = query.where(Course.is_published == True)

    if difficulty:
        query = query.where(Course.difficulty_level == difficulty)

    query = query.offset(skip).limit(limit).order_by(Course.created_at.desc())

    result = await db.execute(query)
    courses = result.scalars().all()

    return courses


@router.get('/{course_id}', response_model=CourseResponse)
async def get_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    
    # get a specific course by ID
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    return course


@router.put('/{course_id}', response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # update a course (only by course creator)
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    

    # check ownership
    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this course")
    
    # update fields
    update_data = course_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    await db.commit()
    await db.refresh(course)

    return course


@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # delete a course (only by course creator)
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this course")
    

    await db.delete(course)
    await db.commit()


# module endpoints
