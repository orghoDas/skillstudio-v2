from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_instructor
from app.models.user import User
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentAttempt
from app.models.learner_profile import LearnerProfile
from app.schemas.assessment import AssessmentCreate, AssessmentResponse, QuestionCreate, QuestionResponse, QuestionWithAnswer, SubmitAnswerRequest, AssessmentAttemptResponse, DiagnosticResultResponse


router = APIRouter()


# assessment crud (instructor only)
@router.post('/', response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # create a new assessment (instructor only)
    new_assessment = Assessment(
        title=assessment_data.title,
        description=assessment_data.description,
        is_diagnostic=assessment_data.is_diagnostic,
        skills_assessed=assessment_data.skills_assessed,
        time_limit_minutes=assessment_data.time_limit_minutes,
        passing_score=assessment_data.passing_score,
    )

    db.add(new_assessment)
    await db.commit()
    await db.refresh(new_assessment)

    return new_assessment


@router.get('/', response_model=List[AssessmentResponse])
async def list_assessments(
    diagnostic_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    
    # list all assessments
    query = select(Assessment)

    if diagnostic_only:
        query = query.where(Assessment.is_diagnostic == True)

    query = query.order_by(Assessment.created_at.desc())
    result = await db.execute(query)
    assessments = result.scalars().all()

    return assessments


@router.get('/{assessment_id}', response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    
    # get assessments details
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    
    return assessment


# questions
@router.post('/{assessment_id}/questions', response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def add_question(
    assessment_id: UUID,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    
    # add a question to an assessment

    # verify assessment exists
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    
    new_question = AssessmentQuestion(
        assessment_id=assessment_id,
        question_text=question_data.question_text,
        question_type=question_data.question_type,
        options=question_data.options,
        correct_answer=question_data.correct_answer,
        explanation=question_data.explanation,
        difficulty_level=question_data.difficulty_level,
        points=question_data.points,
        skill_tags=question_data.skill_tags,
        sequence_order=question_data.sequence_order
    )

    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)

    return new_question


@router.get('/{assessment_id}/questions', response_model=List[QuestionResponse])
async def get_questions(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    # get all questions for an assessment (without answers for learners)
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    questions = result.scalars().all()

    return questions


# taking assessments
@router.post('/{assessment_id}/submit', response_model=AssessmentAttemptResponse)
async def submit_assessment(
    assessment_id: UUID,
    submission: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    # submit answer for an assessment
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    
    result = await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == current_user.id))
    questions = result.scalars().all()

    # grade the assessment
    grading_result = grade_assessment(assessment, submission.answers)
    
    # calculate attempt number
    result = await db.execute(
        select(AssessmentAttempt)
        .where(AssessmentAttempt.assessment_id == assessment_id)
        .where(AssessmentAttempt.user_id == current_user.id))
    
    previous_attempts = result.scalars().all()
    attempt_number = len(previous_attempts) + 1

    # create attempt record
    new_attempt = AssessmentAttempt(
        user_id=current_user.id,
        assessment_id=assessment_id,
        score_percentage=grading_result['score_percentage'],
        points_earned=grading_result['points_earned'],
        points_possible=grading_result['points_possible'],
        time_taken_seconds=submission.time_taken_seconds,
        answers = grading_result['detailed_answers'],
        skill_scores = grading_result['skill_scores'],
        attempt_number=attempt_number,
        passed=grading_result['scored_percentage'] >= assessment.passing_score
        feedback = generate_feedback(grading_result)
    )

    db.add(new_attempt)
    await db.commit()
    await db.refresh(new_attempt)

    # if diagnostic assessment, update learner porfile
    if assessment.is_diagnostic:
        await update_learner_profile_from_diagnostic(current_user.id, grading_result['skill_scores'], db)

    return new_attempt


@router.post('/{assessment_id}/diagnostic-result', response_model=DiagnosticResultResponse)
async def get_diagnostic_result(
    assessment_id: UUID,
    submission: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    # submit diagnostic assessment and get full profiling results

    # submit assessments
    attempt = await submit_assessment(assessment_id, submission, current_user, db)

    # generate skill levels 
    skill_levels = {}
    for skill, score in attempt.skill_scores.items():
        skill_levels[skill] = int(score * 10)

    # identify knowledge gaps (below 5)
    knowledge_gaps = [skill for skill, score in attempt.skill_scores.items() if score < 5]

    # get course recommendations
    recommended_courses = await recommend_courses_for_skills(knowledge_gaps, db)

    # generate learning path
    learning_path = generate_initial_learning_path(skill_levels, knowledge_gaps)

    return DiagnosticResultResponse(
        attempt = attempt,
        skill_levels = skill_levels,
        knowledge_gaps = knowledge_gaps,
        recommended_courses = recommended_courses,
        suggested_learning_path= learning_path
    )


# helper functions
