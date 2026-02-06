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
from app.services.adaptive_assessment import AdaptiveAssessmentEngine, AIFeedbackGenerator


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
        passed=grading_result['scored_percentage'] >= assessment.passing_score,
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
def grade_assessment(questions: List[AssessmentQuestion], user_answers: List[dict]) -> dict:
    # grading logic here
    total_points = sum(q.points for q in questions)
    points_earned = 0
    skill_points = {}
    skill_totals = {}

    graded_answers = []

    # create lookup dict for user answers
    answer_dict = {ans['question_id']: ans for ans in user_answers}

    for question in questions:
        user_answer = answer_dict.get(str(question.id), {}).get('answer')

        # check if answer is correct
        correct = user_answer(user_answer, question.correct_answer, question.question_type)

        if correct:
            points_earned += question.points

        # track by skill
        for skill in question.skill_tags:
            if skill not in skill_points:
                skill_points[skill] = 0
                skill_totals[skill] = 0

            skill_totals[skill] += question.points
            if correct:
                skill_points[skill] += question.points

        graded_answers.append({
            'question_id': str(question.id),
            'user_answer': user_answer,
            'correct_answer': question.correct_answer,
            'correct': correct,
            'points_earned': question.points if correct else 0,
            'explanation': question.explanation
        })

    # calculate skill scores (0-1 scale)
    skill_scores = {}
    for skill, points in skill_points.items():
        if skill_totals[skill] > 0:
            skill_scores[skill] = round(points / skill_totals[skill], 2)

    return {
        'score_percentage': round((points_earned / total_points * 100), 2) if total_points > 0 else 0,
        'points_earned': points_earned,
        'points_possible': total_points,
        'answers': graded_answers,
        'skill_scores': skill_scores
    }


def check_answer(user_answer, correct_answer: dict, question_type: str) -> bool:
    # check if user's answer is correct
    if user_answer is None:
        return False
    
    if question_type == 'mcq':
        return user_answer == correct_answer.get('answer')
    
    elif question_type == 'true_false':
        return user_answer == correct_answer.get('answer')
    
    elif question_type == 'code':
        # for code questions, we run tests, simplified here
        return True
    
    return False


def generate_feedback(grading_result: dict) -> str:
    # generate ai powered feedback based on results
    score = grading_result['score_percentage']
    skill_scores = grading_result['skill_scores']

    feedback_parts = []

    # overall performance
    if score >= 90:
        feedback_parts.append("Excellent work! You have a strong understanding of the material.")
    elif score >= 75:
        feedback_parts.append("Good job! You have a solid grasp but there's room for improvement.")
    elif score >= 50:
        feedback_parts.append("Fair effort. Consider reviewing the material to strengthen your understanding.")
    else:
        feedback_parts.append("Needs improvement. Focus on the areas where you struggled the most.")

    # skill-specific feedback 
    weak_skills = [skill for skill, score in skill_scores.items() if score < 0.6]
    strong_skills = [skill for skill, score in skill_scores.items() if score >= 0.8]

    if strong_skills:
        feedback_parts.append(f"Your strengths are in: {', '.join(strong_skills)}.")

    if weak_skills:
        feedback_parts.append(f"Consider focusing on improving: {', '.join(weak_skills)}.")

    return " ".join(feedback_parts)


async def update_learner_profile_from_diagnostic(
        user_id: UUID,
        skill_scores: dict,
        db: AsyncSession):
    
    # update leaner profile based on diagnostic results
    result = await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = LearnerProfile(user_id=user_id)
        db.add(profile)

    # convert skill score to 1-10 scale
    skill_levels = {skill: int(score * 10) for skill, score in skill_scores.items()}

    # identify knowledge gaps
    knowledge_gaps = [skill for skill, score in skill_scores.items() if score < 5]

    profile.skill_levels = skill_levels
    profile.knowledge_gaps = knowledge_gaps

    await db.commit()


async def recommend_courses_for_skills(skills: List[str], db: AsyncSession) -> List[UUID]:
    # recommend courses based on skills
    from app.models.course import Course
    from sqlalchemy import or_

    if not skills:
        return []
    
    # find courses that teach any of the needed skills
    result = await db.execute(
        select(Course)
        .where(Course.is_published == True,
               #check if any skill in skills_taught matches our needed skills
               Course.skills_taught.op('?|')(skills)).limit(5))
    
    courses = result.scalars().all()
    return [course.id for course in courses]


def generate_initial_learning_path(skill_levels: dict, knowledge_gaps: List[str]) -> List[dict]:
    # generate a suggested learning path based on assessments
    path = []

    # start with foundational skills (lowest scores)
    sorted_skills = sorted(skill_levels.items(), key=lambda x: x[1])

    for skill, level in sorted_skills[:3]:
        path.append({
            'skill': skill,
            'current_level': level,
            'target_level': 7,
            'priority': 'high' if level < 3 else 'medium',
            'recommended__actions': f'take beginner courses on {skill}' if level < 5 else f'practice intermediate {skill} concepts'
        })

    return path


# Adaptive Assessment Endpoints
@router.post('/adaptive/{assessment_id}/next-question')
async def get_adaptive_next_question(
    assessment_id: str,
    previous_answers: List[dict] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the next question with adaptive difficulty based on previous performance.
    Questions adjust dynamically to the learner's skill level.
    """
    engine = AdaptiveAssessmentEngine(db)
    next_question = await engine.get_next_question(
        user_id=str(current_user.id),
        assessment_id=assessment_id,
        previous_answers=previous_answers or []
    )
    
    if not next_question:
        return {"message": "No more questions available", "completed": True}
    
    return next_question


@router.post('/attempts/{attempt_id}/ai-feedback')
async def get_ai_feedback(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive AI-generated feedback for an assessment attempt.
    
    Includes:
    - Performance analysis
    - Strengths and improvement areas
    - Personalized recommendations
    - Progress comparison with previous attempts
    - Suggested next steps
    """
    # Verify the attempt belongs to the current user
    attempt_result = await db.execute(
        select(AssessmentAttempt)
        .where(AssessmentAttempt.id == attempt_id)
    )
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    if str(attempt.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this feedback")
    
    feedback_generator = AIFeedbackGenerator(db)
    feedback = await feedback_generator.generate_comprehensive_feedback(
        user_id=str(current_user.id),
        attempt_id=attempt_id
    )
    
    if "error" in feedback:
        raise HTTPException(status_code=404, detail=feedback["error"])
    
    return feedback


@router.post('/adaptive/{assessment_id}/calculate-score')
async def calculate_adaptive_score(
    assessment_id: str,
    answers: List[dict],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate difficulty-weighted score for adaptive assessment.
    Harder questions are worth more points.
    """
    engine = AdaptiveAssessmentEngine(db)
    score_data = await engine.calculate_adaptive_score(
        answers=answers,
        assessment_id=assessment_id
    )
    
    return {
        "user_id": str(current_user.id),
        "assessment_id": assessment_id,
        **score_data
    }
