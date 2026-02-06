"""
AI Features API Endpoints
Course recommendations, learning paths, skill gap analysis
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..models.user import User
from ..services.ai_recommendations import (
    RecommendationEngine,
    LearningPathGenerator,
    SkillGapAnalyzer
)

router = APIRouter(prefix="/ai", tags=["AI Features"])


@router.get("/recommendations")
async def get_course_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized course recommendations powered by AI.
    
    Returns courses ranked by:
    - Skill match with learning goals
    - Appropriate difficulty level
    - Goal alignment
    - Popularity
    - Prerequisite readiness
    """
    engine = RecommendationEngine(db)
    recommendations = await engine.get_personalized_recommendations(
        user_id=str(current_user.id),
        limit=limit
    )
    
    return {
        "user_id": str(current_user.id),
        "recommendations": recommendations,
        "total_recommended": len(recommendations)
    }


@router.get("/learning-path")
async def generate_learning_path(
    goal_id: Optional[str] = Query(None, description="Specific learning goal ID (optional)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a personalized learning path to achieve your goals.
    
    Creates an ordered sequence of courses that:
    - Build on your current skills
    - Fill skill gaps systematically
    - Account for prerequisites
    - Estimate realistic timeline
    """
    generator = LearningPathGenerator(db)
    learning_path = await generator.generate_learning_path(
        user_id=str(current_user.id),
        goal_id=goal_id
    )
    
    if "error" in learning_path:
        raise HTTPException(status_code=404, detail=learning_path["error"])
    
    return learning_path


@router.get("/skill-gap-analysis")
async def analyze_skill_gaps(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Comprehensive skill gap analysis.
    
    Provides:
    - Current skill proficiency levels
    - Target skills from your learning goals
    - Identified skill gaps with priority levels
    - Strength areas to leverage
    - Actionable recommendations
    """
    analyzer = SkillGapAnalyzer(db)
    analysis = await analyzer.analyze_skill_gaps(user_id=str(current_user.id))
    
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
    
    return analysis


@router.get("/next-best-action")
async def get_next_best_action(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AI-powered suggestion for what to do next in your learning journey.
    
    Analyzes:
    - Current progress
    - Upcoming goals
    - Skill gaps
    - Time availability
    
    Returns a single actionable recommendation.
    """
    from sqlalchemy import select
    from ..models.learning import Enrollment, LearningGoal
    
    # Get active enrollments with incomplete progress
    enrollments_result = await db.execute(
        select(Enrollment)
        .where(Enrollment.user_id == current_user.id)
        .where(Enrollment.progress_percentage < 100)
        .order_by(Enrollment.last_accessed.desc())
    )
    active_enrollments = enrollments_result.scalars().all()
    
    # Get active learning goals
    goals_result = await db.execute(
        select(LearningGoal)
        .where(LearningGoal.user_id == current_user.id)
        .where(LearningGoal.current_status == 'ACTIVE')
        .order_by(LearningGoal.created_at.desc())
    )
    active_goals = goals_result.scalars().all()
    
    # Decision logic
    recommendation = {
        "action": "",
        "reason": "",
        "details": {}
    }
    
    # Priority 1: Continue in-progress courses
    if active_enrollments:
        most_recent = active_enrollments[0]
        recommendation["action"] = "continue_course"
        recommendation["reason"] = f"You're {int(most_recent.progress_percentage)}% through this course. Maintain momentum!"
        recommendation["details"] = {
            "enrollment_id": str(most_recent.id),
            "course_id": str(most_recent.course_id),
            "progress": int(most_recent.progress_percentage)
        }
        return recommendation
    
    # Priority 2: Start a recommended course aligned with goals
    if active_goals:
        engine = RecommendationEngine(db)
        recommendations = await engine.get_personalized_recommendations(
            user_id=str(current_user.id),
            limit=1
        )
        
        if recommendations:
            top_rec = recommendations[0]
            recommendation["action"] = "start_new_course"
            recommendation["reason"] = f"This course aligns with your goal: {active_goals[0].goal_description}"
            recommendation["details"] = {
                "course_id": top_rec['course_id'],
                "course_title": top_rec['title'],
                "reasons": top_rec['reasons']
            }
            return recommendation
    
    # Priority 3: Take a skill assessment
    from ..models.assessment import Assessment, AssessmentAttempt
    
    assessments_result = await db.execute(
        select(Assessment)
        .where(Assessment.is_diagnostic == True)
    )
    assessments = assessments_result.scalars().all()
    
    # Find assessments user hasn't taken
    if assessments:
        attempts_result = await db.execute(
            select(AssessmentAttempt.assessment_id)
            .where(AssessmentAttempt.user_id == current_user.id)
        )
        attempted_ids = [str(row[0]) for row in attempts_result.all()]
        
        untaken = [a for a in assessments if str(a.id) not in attempted_ids]
        if untaken:
            recommendation["action"] = "take_assessment"
            recommendation["reason"] = "Assess your skills to get personalized recommendations"
            recommendation["details"] = {
                "assessment_id": str(untaken[0].id),
                "assessment_title": untaken[0].title
            }
            return recommendation
    
    # Priority 4: Set a learning goal
    if not active_goals:
        recommendation["action"] = "set_goal"
        recommendation["reason"] = "Define your learning objectives to get personalized course recommendations"
        recommendation["details"] = {}
        return recommendation
    
    # Default: Explore courses
    recommendation["action"] = "explore_courses"
    recommendation["reason"] = "Discover new courses to expand your skills"
    recommendation["details"] = {}
    
    return recommendation
