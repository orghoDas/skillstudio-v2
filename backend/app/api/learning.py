from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List 
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_learner
from app.models.user import User
from app.models.learning import LessonProgress, Enrollment, LearningGoal
from app.models.course import Course, Lesson
from app.models.learner_profile import LearnerProfile
from app.schemas.learning import LearningGoalCreate, LearningGoalUpdate, LearningGoalResponse, EnrollmentCreate, EnrollmentResponse, LessonProgressUpdate, LessonProgressResponse


router = APIRouter()


# learning goals
@router.post('/goals', response_model=LearningGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_goal(
    goal_data: LearningGoalCreate,
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    
    # create a new learning goal
    result = await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    skill_snapshot = profile.skill_levels if profile else {}

    new_goal = LearningGoal(
        user_id=current_user.id,
        goal_description=goal_data.goal_description,
        target_role=goal_data.target_role,
        target_skills=goal_data.target_skills,
        initial_skill_snapshot=skill_snapshot,
    )

    db.add(new_goal)
    await db.commit()
    await db.refresh(new_goal)

    return new_goal


@router.get('/goals', response_model=List[LearningGoalResponse])
async def list_my_goals(
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    
    # list all my learning goals
    result = await db.execute(select(LearningGoal).where(LearningGoal.user_id == current_user.id))
    goals = result.scalars().all()

    return goals


@router.get('/goals/{goal_id}', response_model=LearningGoalResponse)
async def get_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    
    # get a specific learning goal
    result = await db.execute(
        select(LearningGoal).where(
            LearningGoal.id == goal_id,
        )
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found")
    
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this learning goal")
    
    return goal


@router.put('/goals/{goal_id}', response_model=LearningGoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_data: LearningGoalUpdate,
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)  
):
    
    # update a learning goal
    result = await db.execute(
        select(LearningGoal).where(
            LearningGoal.id == goal_id,
        )
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found")
    
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this learning goal")
    
    update_data = goal_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    await db.commit()
    await db.refresh(goal)

    return goal


# enrollments
@router.post('/enrollments', response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    enrollment_data: EnrollmentCreate,
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    
    # enroll in a course
    # check if course exists
    result = await db.execute(select(Course).where(Course.id == enrollment_data.course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    # check if already enrolled
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == enrollment_data.course_id
        )
    )
    existing_enrollment = result.scalar_one_or_none()
    if existing_enrollment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled in this course")
    
    # Get instructor details for email
    instructor_result = await db.execute(select(User).where(User.id == course.created_by))
    instructor = instructor_result.scalar_one()
    
    new_enrollment = Enrollment(
        user_id=current_user.id,
        course_id=enrollment_data.course_id,
        learning_goal_id=enrollment_data.learning_goal_id,
        status='active'
    )

    db.add(new_enrollment)

    # update course enrollment count
    course.total_enrollments += 1
    await db.commit()
    await db.refresh(new_enrollment)
    
    # Send enrollment confirmation email
    try:
        await email_service.send_enrollment_confirmation(
            user_email=current_user.email,
            user_name=current_user.full_name,
            course_title=course.title,
            course_description=course.short_description or course.description[:200],
            instructor_name=instructor.full_name,
            start_date=datetime.utcnow().strftime("%B %d, %Y")
        )
    except Exception as e:
        print(f"Failed to send enrollment confirmation email: {e}")

    return new_enrollment


@router.get('/enrollments', response_model=List[EnrollmentResponse])
async def list_my_enrollments(
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    
    # list all my enrollments
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id
        ).order_by(Enrollment.enrolled_at.desc())
    )
    enrollments = result.scalars().all()

    return enrollments


# progress tracking
@router.put('/progress/lessons/{lesson_id}', response_model=LessonProgressResponse)
async def update_lesson_progress(
    lesson_id: UUID,
    progress_data: LessonProgressUpdate,
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    
    # update progress on a lesson
    result = await db.execute(
        select(Lesson).where(
            Lesson.id == lesson_id
        )
    )
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    
    # get or create progress record
    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            first_accessed = datetime.utcnow()
        )
        db.add(progress)

    # update fields
    update_data = progress_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'time_spent_seconds' and value is not None:
            if progress.time_spent_seconds is None:
                progress.time_spent_seconds = 0
            progress.time_spent_seconds += value

        else:
            setattr(progress, field, value)

    progress.last_accessed = datetime.utcnow()

    # mark as completed if progress is 100%
    if progress.completion_percentage == 100:
        progress.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(progress)

    return progress


@router.get('/progress/lessons/{lesson_id}', response_model=LessonProgressResponse)
async def get_lesson_progress(
    lesson_id: UUID,
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    
    # get progress on a lesson
    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No progress found for this lesson")
    
    return progress


