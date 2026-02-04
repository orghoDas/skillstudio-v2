"""
AI Dashboard API

Provides personalized learning insights and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_active_learner
from app.models.user import User
from app.models.learning import LearningGoal, Enrollment
from app.models.ai_models import LearningPathSnapshot, Recommendation
from app.services.recommendation_engine import RecommendationEngine
from app.services.learning_analytics import LearningAnalytics
from app.services.skill_assessment import SkillAssessor


router = APIRouter()


@router.get('/dashboard')
async def get_learner_dashboard(
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive learner dashboard with AI-powered insights
    
    Returns:
        {
            "performance_summary": {...},
            "current_goals": [...],
            "recommended_next_lessons": [...],
            "revision_recommendations": [...],
            "engagement_insights": {...},
            "ai_insights": {
                "learning_pace": "on_track",
                "predicted_completion": "2026-03-15",
                "performance_trend": "improving",
                "personalized_message": "..."
            }
        }
    """
    
    # Initialize services
    analytics = LearningAnalytics(db)
    recommender = RecommendationEngine(db)
    
    # Get performance summary
    performance = await analytics.get_learner_performance_summary(current_user.id, days=30)
    
    # Get active learning goals
    result = await db.execute(
        select(LearningGoal)
        .where(LearningGoal.user_id == current_user.id)
        .where(LearningGoal.current_status == 'active')
        .order_by(LearningGoal.created_at.desc())
    )
    active_goals = result.scalars().all()
    
    # Get active enrollments
    result = await db.execute(
        select(Enrollment)
        .where(Enrollment.user_id == current_user.id)
        .where(Enrollment.completed_at.is_(None))
        .limit(5)
    )
    enrollments = result.scalars().all()
    
    # Get next lesson recommendations for each enrollment
    recommended_lessons = []
    for enrollment in enrollments:
        next_lesson = await recommender.recommend_next_lesson(
            current_user.id,
            enrollment.id
        )
        if next_lesson:
            next_lesson['enrollment_id'] = str(enrollment.id)
            recommended_lessons.append(next_lesson)
    
    # Get revision recommendations
    revision_recs = await recommender.recommend_revision_content(
        current_user.id,
        limit=5
    )
    
    # Get engagement patterns
    engagement = await analytics.get_engagement_patterns(current_user.id)
    
    # Get struggling topics
    struggling_topics = await analytics.identify_struggling_topics(
        current_user.id,
        threshold=60.0
    )
    
    # Generate AI insights
    ai_insights = await _generate_ai_insights(
        current_user.id,
        performance,
        engagement,
        struggling_topics,
        active_goals,
        db
    )
    
    return {
        'performance_summary': performance,
        'current_goals': [
            {
                'id': str(goal.id),
                'description': goal.goal_description,
                'target_role': goal.target_role,
                'target_skills': goal.target_skills,
                'completion_percentage': goal.completion_percentage,
                'created_at': goal.created_at.isoformat()
            }
            for goal in active_goals
        ],
        'recommended_next_lessons': recommended_lessons,
        'revision_recommendations': revision_recs,
        'struggling_topics': struggling_topics,
        'engagement_insights': engagement,
        'ai_insights': ai_insights
    }


@router.get('/recommendations')
async def get_active_recommendations(
    limit: int = 10,
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active AI recommendations for the user
    """
    
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.user_id == current_user.id)
        .where(Recommendation.user_action.is_(None))
        .where(
            (Recommendation.expires_at.is_(None)) |
            (Recommendation.expires_at > datetime.now())
        )
        .order_by(Recommendation.priority, Recommendation.created_at.desc())
        .limit(limit)
    )
    recommendations = result.scalars().all()
    
    return [
        {
            'id': str(rec.id),
            'type': rec.recommendation_type.value,
            'content_id': str(rec.recommended_content_id) if rec.recommended_content_id else None,
            'content_type': rec.recommended_content_type,
            'reason': rec.reason,
            'confidence': float(rec.confidence_score) if rec.confidence_score else None,
            'priority': rec.priority,
            'created_at': rec.created_at.isoformat(),
            'expires_at': rec.expires_at.isoformat() if rec.expires_at else None
        }
        for rec in recommendations
    ]


@router.post('/recommendations/{recommendation_id}/action')
async def action_on_recommendation(
    recommendation_id: UUID,
    action: str,  # 'accepted', 'skipped', 'ignored'
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    """
    Record user action on a recommendation
    """
    
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.id == recommendation_id)
        .where(Recommendation.user_id == current_user.id)
    )
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Update action
    from app.models.ai_models import RecommendationAction
    
    try:
        recommendation.user_action = RecommendationAction(action.lower())
        recommendation.actioned_at = datetime.now()
        
        await db.commit()
        await db.refresh(recommendation)
        
        return {
            'success': True,
            'message': f'Marked recommendation as {action}',
            'recommendation_id': str(recommendation.id)
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: accepted, skipped, modified, ignored"
        )


@router.get('/learning-path')
async def get_current_learning_path(
    goal_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current active learning path for a goal
    """
    
    query = select(LearningPathSnapshot).where(
        LearningPathSnapshot.user_id == current_user.id
    ).where(
        LearningPathSnapshot.active == True
    ).order_by(LearningPathSnapshot.created_at.desc())
    
    if goal_id:
        query = query.where(LearningPathSnapshot.learning_goal_id == goal_id)
    
    result = await db.execute(query)
    path_snapshot = result.scalar_one_or_none()
    
    if not path_snapshot:
        return {
            'has_path': False,
            'message': 'No active learning path found. Create a goal to generate one.'
        }
    
    return {
        'has_path': True,
        'snapshot_id': str(path_snapshot.id),
        'snapshot_type': path_snapshot.snapshot_type.value,
        'recommended_path': path_snapshot.recommended_path,
        'estimated_total_hours': path_snapshot.estimated_total_hours,
        'estimated_completion_date': (
            path_snapshot.estimated_completion_date.isoformat()
            if path_snapshot.estimated_completion_date else None
        ),
        'confidence_score': float(path_snapshot.confidence_score) if path_snapshot.confidence_score else None,
        'created_at': path_snapshot.created_at.isoformat(),
        'adjustment_reasons': path_snapshot.adjustment_reasons
    }


@router.post('/generate-learning-path')
async def generate_learning_path(
    goal_id: UUID,
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new AI-powered learning path for a goal
    """
    
    # Verify goal exists and belongs to user
    result = await db.execute(
        select(LearningGoal)
        .where(LearningGoal.id == goal_id)
        .where(LearningGoal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Learning goal not found")
    
    # Generate path using AI
    recommender = RecommendationEngine(db)
    learning_path, metadata = await recommender.generate_learning_path(
        current_user.id,
        goal_id
    )
    
    # Deactivate old paths for this goal
    await db.execute(
        select(LearningPathSnapshot)
        .where(LearningPathSnapshot.user_id == current_user.id)
        .where(LearningPathSnapshot.learning_goal_id == goal_id)
        .where(LearningPathSnapshot.active == True)
    )
    old_paths = (await db.execute(
        select(LearningPathSnapshot)
        .where(LearningPathSnapshot.user_id == current_user.id)
        .where(LearningPathSnapshot.learning_goal_id == goal_id)
        .where(LearningPathSnapshot.active == True)
    )).scalars().all()
    
    for path in old_paths:
        path.active = False
    
    # Create new path snapshot
    from app.models.ai_models import SnapshotType
    from datetime import datetime as dt
    
    new_snapshot = LearningPathSnapshot(
        user_id=current_user.id,
        learning_goal_id=goal_id,
        snapshot_type="initial",  # Use string directly for PostgreSQL enum
        recommended_path=learning_path,
        estimated_total_hours=metadata.get('total_hours'),
        estimated_completion_date=dt.fromisoformat(metadata['estimated_completion_date']),
        confidence_score=0.75,
        active=True
    )
    
    db.add(new_snapshot)
    await db.commit()
    await db.refresh(new_snapshot)
    
    return {
        'success': True,
        'snapshot_id': str(new_snapshot.id),
        'learning_path': learning_path,
        'metadata': metadata
    }


async def _generate_ai_insights(
    user_id: UUID,
    performance: Dict,
    engagement: Dict,
    struggling_topics: List[Dict],
    active_goals: List,
    db: AsyncSession
) -> Dict:
    """
    Generate personalized AI insights and messages
    """
    
    # Determine learning pace status
    pace = performance.get('performance_trend', 'stable')
    
    # Generate personalized message
    message_parts = []
    
    if performance['current_streak'] > 0:
        if performance['current_streak'] >= 7:
            message_parts.append(f"🔥 Amazing {performance['current_streak']}-day streak!")
        elif performance['current_streak'] >= 3:
            message_parts.append(f"Great {performance['current_streak']}-day streak! Keep it up!")
    
    if performance['performance_trend'] == 'improving':
        message_parts.append("Your performance is improving - you're mastering the material!")
    elif performance['performance_trend'] == 'declining':
        message_parts.append("Consider reviewing recent topics to strengthen your foundation.")
    
    if struggling_topics:
        top_struggle = struggling_topics[0]['skill']
        message_parts.append(f"Focus on {top_struggle} - we've prepared revision content for you.")
    
    if performance['completion_rate'] > 0.8:
        message_parts.append("Excellent completion rate! You're very consistent.")
    
    personalized_message = " ".join(message_parts) if message_parts else "Keep up the good work!"
    
    # Predicted completion (simple estimate)
    if active_goals:
        # Use first active goal
        goal = active_goals[0]
        predicted_completion = "Based on your pace, estimated completion in 8-12 weeks"
    else:
        predicted_completion = None
    
    return {
        'learning_pace': pace,
        'predicted_completion': predicted_completion,
        'performance_trend': performance['performance_trend'],
        'personalized_message': personalized_message,
        'strengths': _identify_strengths(performance),
        'areas_for_improvement': [t['skill'] for t in struggling_topics[:3]],
        'study_recommendation': _generate_study_recommendation(engagement)
    }


def _identify_strengths(performance: Dict) -> List[str]:
    """Identify learner's strengths based on performance"""
    strengths = []
    
    if performance['avg_quiz_score'] >= 85:
        strengths.append("Strong quiz performance")
    
    if performance['completion_rate'] >= 0.75:
        strengths.append("Consistent lesson completion")
    
    if performance['current_streak'] >= 5:
        strengths.append("Excellent study discipline")
    
    if performance['total_study_hours'] >= 15:
        strengths.append("High engagement")
    
    return strengths


def _generate_study_recommendation(engagement: Dict) -> str:
    """Generate study schedule recommendation"""
    
    peak_hours = engagement.get('peak_hours', [])
    peak_days = engagement.get('peak_days', [])
    
    if peak_hours and peak_days:
        hour_str = f"{peak_hours[0]:02d}:00" if peak_hours else "evening"
        day_str = ', '.join(peak_days) if peak_days else "weekdays"
        return f"You learn best on {day_str} around {hour_str}. Schedule important lessons then!"
    
    return "Try to maintain a consistent study schedule for best results."
