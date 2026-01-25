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
@router.post('/{course_id}/modules', response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    course_id: UUID,
    module_data: ModuleCreate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # create a new module within a course (instructor only)
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add modules to this course")
    
    new_module = Module(
        course_id = course_id,
        title = module_data.title,
        description = module_data.description,
        sequence_order = module_data.sequence_order,
        est_duration_minutes = module_data.est_duration_minutes
    )

    db.add(new_module)
    await db.commit()
    await db.refresh(new_module)

    return new_module


@router.get('/{course_id}/modules', response_model=List[ModuleResponse])
async def list_modules(
    course_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    
    # list all modules within a course
    result = await db.execute(select(Module).where(Module.course_id == course_id).order_by(Module.sequence_order))
    modules = result.scalars().all()

    return modules


@router.put('/modules/{module_id}', response_model=ModuleResponse)
async def update_module(
    module_id: UUID,
    module_data: ModuleUpdate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # update a module (only by course creator)
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()

    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    
    # check ownership via course
    result = await db.execute(select(Course).where(Course.id == module.course_id))
    course = result.scalar_one_or_none()

    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this module")
    
    update_data = module_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)

    await db.commit()
    await db.refresh(module)

    return module


@router.delete('/modules/{module_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: UUID,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # delete a module (only by course creator)
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()

    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    
    # check ownership via course
    result = await db.execute(select(Course).where(Course.id == module.course_id))
    course = result.scalar_one_or_none()

    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this module")
    
    await db.delete(module)
    await db.commit()


# lesson endpoints
@router.post('/modules/{module_id}/lessons', response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    module_id: UUID,
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # create a new lesson within a module (instructor only)
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()

    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    
    # check ownership via course
    result = await db.execute(select(Course).where(Course.id == module.course_id))
    course = result.scalar_one_or_none()

    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add lessons to this module")
    
    new_lesson = Lesson(
        module_id = module_id,
        title = lesson_data.title,
        content_type = lesson_data.content_type,
        content_url = lesson_data.content_url,
        content_body = lesson_data.content_body,
        content_metadata = lesson_data.content_metadata,
        est_minutes = lesson_data.est_minutes,
        difficulty_score = lesson_data.difficulty_score,
        prerequisites = lesson_data.prerequisites,
        skill_tags = lesson_data.skill_tags,
        learning_objectives = lesson_data.learning_objectives,
        sequence_order = lesson_data.sequence_order
    )

    db.add(new_lesson)
    await db.commit()
    await db.refresh(new_lesson)

    return new_lesson


@router.get('/modules/{module_id}/lessons', response_model=List[LessonResponse])
async def list_lessons(
    module_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    
    # list all lessons within a module
    result = await db.execute(select(Lesson).where(Lesson.module_id == module_id).order_by(Lesson.sequence_order))
    lessons = result.scalars().all()

    return lessons


@router.get('/lessons/{lesson_id}', response_model=LessonResponse)
async def get_lesson(
    lesson_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    
    # get a specific lesson by ID
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    
    return lesson


@router.put('/lessons/{lesson_id}', response_model=LessonResponse)
async def update_lesson(
    lesson_id: UUID,
    lesson_data: LessonUpdate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # update a lesson (only by course creator)
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    
    # check ownership via module and course
    result = await db.execute(select(Module).where(Module.id == lesson.module_id))
    module = result.scalar_one_or_none()

    result = await db.execute(select(Course).where(Course.id == module.course_id))
    course = result.scalar_one_or_none()

    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this lesson")
    
    update_data = lesson_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lesson, field, value)

    await db.commit()
    await db.refresh(lesson)

    return lesson


@router.delete('/lessons/{lesson_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: UUID,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # delete a lesson (only by course creator)
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    
    # check ownership via module and course
    result = await db.execute(select(Module).where(Module.id == lesson.module_id))
    module = result.scalar_one_or_none()

    result = await db.execute(select(Course).where(Course.id == module.course_id))
    course = result.scalar_one_or_none()

    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this lesson")
    
    await db.delete(lesson)
    await db.commit()

