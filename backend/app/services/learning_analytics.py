"""
Learning Analytics Service

Provides analytics and insights:
- Performance trends
- Engagement patterns
- Weekly path adjustments
- Learner cohort analysis
"""

from typing import Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text, case
from decimal import Decimal

from app.models.user import User
from app.models.learning import LessonProgress, Enrollment, ProgressStatus
from app.models.assessment import AssessmentAttempt
from app.models.learner_profile import LearnerProfile
from app.models.course import Lesson


class LearningAnalytics:
    """Analytics service for learner performance and engagement"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_learner_performance_summary(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict:
        """
        Get comprehensive performance summary for a learner
        
        Returns:
            {
                "lessons_completed": 15,
                "avg_quiz_score": 78.5,
                "completion_rate": 0.75,
                "active_days": 18,
                "total_study_hours": 23.5,
                "current_streak": 5,
                "performance_trend": "improving"
            }
        """
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Lessons completed
        result = await self.db.execute(
            select(func.count(LessonProgress.id))
            .where(
                and_(
                    LessonProgress.user_id == user_id,
                    LessonProgress.status == ProgressStatus.COMPLETED,
                    LessonProgress.completed_at >= cutoff_date
                )
            )
        )
        lessons_completed = result.scalar() or 0
        
        # Quiz performance
        result = await self.db.execute(
            select(
                func.avg(AssessmentAttempt.score_percecntage).label('avg_score'),
                func.count(AssessmentAttempt.id).label('total_attempts')
            )
            .where(
                and_(
                    AssessmentAttempt.user_id == user_id,
                    AssessmentAttempt.attempted_at >= cutoff_date
                )
            )
        )
        quiz_stats = result.first()
        
        # Total study time
        result = await self.db.execute(
            select(func.sum(LessonProgress.time_spent_seconds))
            .where(
                and_(
                    LessonProgress.user_id == user_id,
                    LessonProgress.last_accessed >= cutoff_date
                )
            )
        )
        total_seconds = result.scalar() or 0
        total_study_hours = round(total_seconds / 3600, 1)
        
        # Active days (unique dates with activity)
        result = await self.db.execute(
            select(func.count(func.distinct(func.date(LessonProgress.last_accessed))))
            .where(
                and_(
                    LessonProgress.user_id == user_id,
                    LessonProgress.last_accessed >= cutoff_date
                )
            )
        )
        active_days = result.scalar() or 0
        
        # Current streak
        streak = await self._calculate_streak(user_id)
        
        # Completion rate (completed vs started)
        result = await self.db.execute(
            select(
                func.count(LessonProgress.id).filter(
                    LessonProgress.status == ProgressStatus.COMPLETED
                ).label('completed'),
                func.count(LessonProgress.id).label('total')
            )
            .where(
                and_(
                    LessonProgress.user_id == user_id,
                    LessonProgress.first_accessed >= cutoff_date
                )
            )
        )
        completion_stats = result.first()
        completion_rate = (
            completion_stats.completed / completion_stats.total
            if completion_stats.total > 0 else 0
        )
        
        # Performance trend
        trend = await self._calculate_performance_trend(user_id, days)
        
        return {
            'lessons_completed': lessons_completed,
            'avg_quiz_score': float(quiz_stats.avg_score) if quiz_stats.avg_score else 0,
            'total_quiz_attempts': quiz_stats.total_attempts or 0,
            'completion_rate': round(completion_rate, 2),
            'active_days': active_days,
            'total_study_hours': total_study_hours,
            'current_streak': streak,
            'performance_trend': trend
        }
    
    async def _calculate_streak(self, user_id: UUID) -> int:
        """Calculate current consecutive day streak"""
        
        # Get last 60 days of activity dates
        result = await self.db.execute(
            select(
                func.distinct(func.date(LessonProgress.last_accessed)).label('activity_date')
            )
            .where(
                and_(
                    LessonProgress.user_id == user_id,
                    LessonProgress.last_accessed >= datetime.now() - timedelta(days=60)
                )
            )
            .order_by(text('activity_date DESC'))
        )
        activity_dates = [row[0] for row in result.all()]
        
        if not activity_dates:
            return 0
        
        # Count consecutive days from most recent
        streak = 0
        expected_date = datetime.now().date()
        
        for activity_date in activity_dates:
            if activity_date == expected_date or activity_date == expected_date - timedelta(days=1):
                streak += 1
                expected_date = activity_date - timedelta(days=1)
            else:
                break
        
        return streak
    
    async def _calculate_performance_trend(
        self,
        user_id: UUID,
        days: int
    ) -> str:
        """
        Analyze if performance is improving, declining, or stable
        
        Returns: "improving", "declining", "stable", or "insufficient_data"
        """
        
        # Split period in half
        midpoint = datetime.now() - timedelta(days=days // 2)
        
        # Recent half performance
        result = await self.db.execute(
            select(func.avg(AssessmentAttempt.score_percecntage))
            .where(
                and_(
                    AssessmentAttempt.user_id == user_id,
                    AssessmentAttempt.attempted_at >= midpoint
                )
            )
        )
        recent_avg = result.scalar()
        
        # Older half performance
        result = await self.db.execute(
            select(func.avg(AssessmentAttempt.score_percecntage))
            .where(
                and_(
                    AssessmentAttempt.user_id == user_id,
                    AssessmentAttempt.attempted_at < midpoint,
                    AssessmentAttempt.attempted_at >= datetime.now() - timedelta(days=days)
                )
            )
        )
        older_avg = result.scalar()
        
        if not recent_avg or not older_avg:
            return "insufficient_data"
        
        difference = float(recent_avg - older_avg)
        
        if difference >= 5.0:
            return "improving"
        elif difference <= -5.0:
            return "declining"
        else:
            return "stable"
    
    async def get_engagement_patterns(
        self,
        user_id: UUID
    ) -> Dict:
        """
        Analyze when and how learner engages with content
        
        Returns:
            {
                "peak_hours": [20, 21, 14],
                "peak_days": ["monday", "wednesday"],
                "avg_session_duration": 45.2,
                "preferred_content_type": "video"
            }
        """
        
        # Get lesson progress with timestamps
        result = await self.db.execute(
            select(LessonProgress, Lesson)
            .join(Lesson, LessonProgress.lesson_id == Lesson.id)
            .where(
                and_(
                    LessonProgress.user_id == user_id,
                    LessonProgress.last_accessed >= datetime.now() - timedelta(days=60)
                )
            )
        )
        sessions = result.all()
        
        if not sessions:
            return {
                'peak_hours': [],
                'peak_days': [],
                'avg_session_duration': 0,
                'preferred_content_type': None
            }
        
        # Analyze hour of day
        hour_counts = {}
        day_counts = {}
        durations = []
        content_type_counts = {}
        
        for progress, lesson in sessions:
            if progress.last_accessed:
                hour = progress.last_accessed.hour
                day = progress.last_accessed.strftime('%A').lower()
                
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
                day_counts[day] = day_counts.get(day, 0) + 1
            
            if progress.time_spent_seconds:
                durations.append(progress.time_spent_seconds)
            
            if lesson.content_type:
                content_type = lesson.content_type.value
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        
        # Get top 3 hours
        peak_hours = sorted(
            hour_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Get top 2 days
        peak_days = sorted(
            day_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:2]
        
        # Average session duration
        avg_duration = sum(durations) / len(durations) / 60 if durations else 0
        
        # Preferred content type
        preferred_content = max(
            content_type_counts.items(),
            key=lambda x: x[1]
        )[0] if content_type_counts else None
        
        return {
            'peak_hours': [h for h, _ in peak_hours],
            'peak_days': [d for d, _ in peak_days],
            'avg_session_duration': round(avg_duration, 1),
            'preferred_content_type': preferred_content
        }
    
    async def identify_struggling_topics(
        self,
        user_id: UUID,
        threshold: float = 60.0
    ) -> List[Dict]:
        """
        Identify topics where learner is struggling
        
        Returns:
            [
                {
                    "skill": "async_programming",
                    "avg_score": 45.0,
                    "attempts": 3,
                    "difficulty": "needs_help"
                },
                ...
            ]
        """
        
        # Get recent assessment attempts
        result = await self.db.execute(
            select(AssessmentAttempt)
            .where(
                and_(
                    AssessmentAttempt.user_id == user_id,
                    AssessmentAttempt.attempted_at >= datetime.now() - timedelta(days=30)
                )
            )
        )
        attempts = result.scalars().all()
        
        # Aggregate by skill
        skill_performance = {}
        
        for attempt in attempts:
            if not attempt.skill_scores:
                continue
            
            for skill, score in attempt.skill_scores.items():
                if skill not in skill_performance:
                    skill_performance[skill] = {
                        'scores': [],
                        'attempts': 0
                    }
                
                skill_performance[skill]['scores'].append(float(score) * 100)
                skill_performance[skill]['attempts'] += 1
        
        # Calculate averages and identify struggles
        struggling_topics = []
        
        for skill, data in skill_performance.items():
            avg_score = sum(data['scores']) / len(data['scores'])
            
            if avg_score < threshold:
                # Categorize difficulty
                if avg_score < 40:
                    difficulty = "critical"
                elif avg_score < 50:
                    difficulty = "needs_help"
                else:
                    difficulty = "review_recommended"
                
                struggling_topics.append({
                    'skill': skill,
                    'avg_score': round(avg_score, 1),
                    'attempts': data['attempts'],
                    'difficulty': difficulty
                })
        
        # Sort by worst performance first
        struggling_topics.sort(key=lambda x: x['avg_score'])
        
        return struggling_topics
    
    async def weekly_path_adjustment(
        self,
        user_id: UUID
    ) -> Dict:
        """
        Analyze weekly performance and suggest path adjustments
        
        Returns:
            {
                "adjustments_needed": True,
                "recommendations": [
                    {
                        "type": "add_revision",
                        "reason": "Low quiz scores in async programming",
                        "action": "Insert 2 revision lessons"
                    }
                ],
                "pace_adjustment": {
                    "current_pace": 1.2,
                    "recommended_pace": 1.0,
                    "timeline_change": "+1 week"
                }
            }
        """
        
        # Get 7-day performance
        performance = await self.get_learner_performance_summary(user_id, days=7)
        
        recommendations = []
        adjustments_needed = False
        
        # Check quiz performance
        if performance['avg_quiz_score'] < 60:
            adjustments_needed = True
            recommendations.append({
                'type': 'add_revision',
                'reason': f"Quiz scores below 60% (current: {performance['avg_quiz_score']:.0f}%)",
                'action': 'Add revision content for weak topics',
                'priority': 'high'
            })
        
        # Check completion rate
        if performance['completion_rate'] < 0.5:
            adjustments_needed = True
            recommendations.append({
                'type': 'reduce_load',
                'reason': f"Low completion rate: {performance['completion_rate']:.0%}",
                'action': 'Reduce weekly lesson recommendations',
                'priority': 'medium'
            })
        
        # Check engagement
        if performance['active_days'] < 3:
            adjustments_needed = True
            recommendations.append({
                'type': 'engagement_boost',
                'reason': f"Only {performance['active_days']} active days this week",
                'action': 'Send engagement notifications, suggest shorter sessions',
                'priority': 'medium'
            })
        
        # Excellent performance - accelerate
        if (performance['avg_quiz_score'] > 85 and 
            performance['completion_rate'] > 0.8 and
            performance['lessons_completed'] > 5):
            adjustments_needed = True
            recommendations.append({
                'type': 'accelerate',
                'reason': 'Excellent performance across all metrics',
                'action': 'Add advanced content, skip basic lessons',
                'priority': 'low'
            })
        
        # Pace analysis
        pace_data = await self._analyze_learning_pace(user_id)
        
        return {
            'adjustments_needed': adjustments_needed,
            'recommendations': recommendations,
            'pace_adjustment': pace_data,
            'performance_summary': performance
        }
    
    async def _analyze_learning_pace(
        self,
        user_id: UUID
    ) -> Dict:
        """Analyze if learner is on track with their pace"""
        
        # Get learner profile
        result = await self.db.execute(
            select(LearnerProfile).where(LearnerProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        expected_hours_per_week = profile.study_hours_per_week if profile else 10
        
        # Get actual study hours last week
        result = await self.db.execute(
            select(func.sum(LessonProgress.time_spent_seconds))
            .where(
                and_(
                    LessonProgress.user_id == user_id,
                    LessonProgress.last_accessed >= datetime.now() - timedelta(days=7)
                )
            )
        )
        actual_seconds = result.scalar() or 0
        actual_hours = actual_seconds / 3600
        
        pace_ratio = actual_hours / expected_hours_per_week if expected_hours_per_week > 0 else 0
        
        if pace_ratio > 1.2:
            pace_status = "ahead"
            timeline_change = "-1 week"
        elif pace_ratio < 0.8:
            pace_status = "behind"
            timeline_change = "+1 week"
        else:
            pace_status = "on_track"
            timeline_change = "no change"
        
        return {
            'current_pace': round(pace_ratio, 2),
            'expected_hours_per_week': expected_hours_per_week,
            'actual_hours_this_week': round(actual_hours, 1),
            'pace_status': pace_status,
            'timeline_change': timeline_change
        }
