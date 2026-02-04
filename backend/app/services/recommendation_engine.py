"""
Recommendation Engine

Generates personalized recommendations for:
- Learning paths based on goals
- Next lessons to complete
- Revision content for struggling topics
- Difficulty adjustments
"""

from typing import List, Dict, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
import json
import math

from app.models.user import User
from app.models.course import Course, Module, Lesson, DifficultyLevel
from app.models.learning import LearningGoal, Enrollment, LessonProgress, ProgressStatus
from app.models.learner_profile import LearnerProfile
from app.models.assessment import AssessmentAttempt


class RecommendationEngine:
    """Rule-based recommendation engine for personalized learning paths"""
    
    # Skill proficiency thresholds
    PROFICIENT_THRESHOLD = 7.0  # 7/10 considered proficient
    STRUGGLING_THRESHOLD = 5.0  # Below 5/10 needs help
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_learning_path(
        self,
        user_id: UUID,
        goal_id: UUID
    ) -> List[Dict]:
        """
        Generate initial personalized learning path for a goal
        
        Returns:
            List of recommended items in sequence:
            [
                {
                    "type": "course",
                    "id": "uuid",
                    "title": "...",
                    "skills_covered": ["python", "flask"],
                    "estimated_hours": 20,
                    "reason": "Builds Python foundation",
                    "sequence": 1
                },
                ...
            ]
        """
        
        # Get learner profile
        result = await self.db.execute(
            select(LearnerProfile).where(LearnerProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            # Create default profile if none exists
            profile = LearnerProfile(user_id=user_id)
        
        # Get goal requirements
        result = await self.db.execute(
            select(LearningGoal).where(LearningGoal.id == goal_id)
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            return []
        
        # Identify skill gaps
        current_skills = profile.skill_levels or {}
        target_skills = goal.target_skills or []
        
        # Normalize skills to lowercase for case-insensitive matching
        skill_gaps = [
            skill.lower() for skill in target_skills
            if current_skills.get(skill, 0) < self.PROFICIENT_THRESHOLD
        ]
        
        # Find courses that cover gap skills
        # Using PostgreSQL JSONB overlap operator (?|)
        from sqlalchemy.dialects.postgresql import array as pg_array
        from sqlalchemy import cast, ARRAY, String
        
        result = await self.db.execute(
            select(Course)
            .where(
                and_(
                    Course.is_published == True,
                    # Check if skills_taught overlaps with skill_gaps
                    Course.skills_taught.op('?|')(cast(skill_gaps, ARRAY(String)))
                )
            )
            .order_by(
                # Order by difficulty: beginner first
                Course.difficulty_level,
                Course.created_at
            )
        )
        courses = result.scalars().all()
        
        # Build learning path with dependency resolution
        learning_path = []
        covered_skills = set(
            skill for skill, level in current_skills.items()
            if level >= self.PROFICIENT_THRESHOLD
        )
        
        for course in courses:
            course_skills = set(course.skills_taught or [])
            prerequisites = set(course.prerequisites or [])
            
            # Check if prerequisites are met
            if not prerequisites.issubset(covered_skills):
                continue  # Skip courses with unmet prerequisites
            
            # Check if course teaches something new
            new_skills = course_skills - covered_skills
            
            if new_skills:
                reason = self._generate_course_reason(
                    course,
                    new_skills,
                    current_skills
                )
                
                learning_path.append({
                    'type': 'course',
                    'id': str(course.id),
                    'title': course.title,
                    'difficulty_level': course.difficulty_level.value,
                    'skills_covered': list(new_skills),
                    'estimated_hours': course.estimated_duration_hours or 0,
                    'reason': reason,
                    'sequence': len(learning_path) + 1
                })
                
                # Update covered skills
                covered_skills.update(new_skills)
        
        # Calculate timeline
        total_hours = sum(item['estimated_hours'] for item in learning_path)
        study_hours_per_week = profile.study_hours_per_week or 10
        estimated_weeks = math.ceil(total_hours / study_hours_per_week)
        
        # Add metadata
        path_metadata = {
            'total_courses': len(learning_path),
            'total_hours': total_hours,
            'estimated_weeks': estimated_weeks,
            'estimated_completion_date': (
                datetime.now() + timedelta(weeks=estimated_weeks)
            ).isoformat(),
            'skills_covered': list(covered_skills),
            'remaining_gaps': [s for s in skill_gaps if s not in covered_skills]
        }
        
        return learning_path, path_metadata
    
    def _generate_course_reason(
        self,
        course: Course,
        new_skills: set,
        current_skills: Dict[str, float]
    ) -> str:
        """Generate human-readable explanation for course recommendation"""
        
        skill_list = ', '.join(list(new_skills)[:3])
        
        if course.difficulty_level == DifficultyLevel.BEGINNER:
            return f"Builds foundation in {skill_list}"
        elif course.difficulty_level == DifficultyLevel.INTERMEDIATE:
            return f"Strengthens your {skill_list} skills"
        else:  # Advanced
            return f"Advanced mastery of {skill_list}"
    
    async def recommend_next_lesson(
        self,
        user_id: UUID,
        enrollment_id: UUID
    ) -> Optional[Dict]:
        """
        Recommend next lesson for an enrolled course
        
        Returns:
            {
                "lesson_id": "uuid",
                "title": "...",
                "reason": "...",
                "estimated_minutes": 30
            }
        """
        
        # Get enrollment details
        result = await self.db.execute(
            select(Enrollment).where(Enrollment.id == enrollment_id)
        )
        enrollment = result.scalar_one_or_none()
        
        if not enrollment:
            return None
        
        # Get completed lesson IDs
        result = await self.db.execute(
            select(LessonProgress.lesson_id)
            .where(
                and_(
                    LessonProgress.user_id == user_id,
                    LessonProgress.status == ProgressStatus.COMPLETED
                )
            )
        )
        completed_lesson_ids = {row[0] for row in result.all()}
        
        # Get all lessons in course order
        result = await self.db.execute(
            select(Lesson, Module)
            .join(Module, Lesson.module_id == Module.id)
            .where(Module.course_id == enrollment.course_id)
            .order_by(Module.sequence_order, Lesson.sequence_order)
        )
        lessons_with_modules = result.all()
        
        # Find first incomplete lesson
        for lesson, module in lessons_with_modules:
            if lesson.id not in completed_lesson_ids:
                # Check prerequisites
                prereqs = lesson.prerequisites or []
                prereqs_met = all(
                    UUID(prereq) in completed_lesson_ids 
                    for prereq in prereqs
                )
                
                if prereqs_met:
                    return {
                        'lesson_id': str(lesson.id),
                        'title': lesson.title,
                        'module_title': module.title,
                        'content_type': lesson.content_type.value,
                        'estimated_minutes': lesson.estimated_minutes,
                        'reason': f"Next in sequence: {module.title}",
                        'difficulty_score': lesson.difficulty_score
                    }
        
        return None  # Course complete
    
    async def recommend_revision_content(
        self,
        user_id: UUID,
        limit: int = 5
    ) -> List[Dict]:
        """
        Recommend lessons for revision based on poor quiz performance
        
        Returns:
            List of lessons to review
        """
        
        # Get recent poor assessment results
        result = await self.db.execute(
            select(AssessmentAttempt)
            .where(
                and_(
                    AssessmentAttempt.user_id == user_id,
                    AssessmentAttempt.score_percecntage < 70.0,
                    AssessmentAttempt.attempted_at >= datetime.now() - timedelta(days=14)
                )
            )
            .order_by(AssessmentAttempt.attempted_at.desc())
        )
        poor_attempts = result.scalars().all()
        
        # Extract weak skills
        weak_skills = {}
        for attempt in poor_attempts:
            if attempt.skill_scores:
                for skill, score in attempt.skill_scores.items():
                    if score < 0.7:  # 70% threshold
                        weak_skills[skill] = min(
                            weak_skills.get(skill, 1.0),
                            score
                        )
        
        if not weak_skills:
            return []
        
        # Find lessons covering weak skills
        weak_skill_list = list(weak_skills.keys())
        
        result = await self.db.execute(
            select(Lesson)
            .where(
                and_(
                    Lesson.is_published == True,
                    text("skill_tags ?| ARRAY[:weak_skills]")
                )
            )
            .params(weak_skills=weak_skill_list)
            .limit(limit)
        )
        revision_lessons = result.scalars().all()
        
        recommendations = []
        for lesson in revision_lessons:
            matching_skills = set(lesson.skill_tags or []) & set(weak_skill_list)
            
            recommendations.append({
                'lesson_id': str(lesson.id),
                'title': lesson.title,
                'content_type': lesson.content_type.value,
                'estimated_minutes': lesson.estimated_minutes,
                'reason': f"Review {', '.join(matching_skills)} - recent quiz score: {int(weak_skills[list(matching_skills)[0]] * 100)}%",
                'skills_to_review': list(matching_skills)
            })
        
        return recommendations
    
    async def detect_struggling_learner(
        self,
        user_id: UUID,
        lesson_id: UUID
    ) -> Tuple[bool, List[str]]:
        """
        Detect if learner is struggling with current lesson
        
        Returns:
            (is_struggling, reasons)
        """
        
        # Get lesson progress
        result = await self.db.execute(
            select(LessonProgress, Lesson)
            .join(Lesson, LessonProgress.lesson_id == Lesson.id)
            .where(
                and_(
                    LessonProgress.user_id == user_id,
                    LessonProgress.lesson_id == lesson_id
                )
            )
        )
        row = result.first()
        
        if not row:
            return False, []
        
        progress, lesson = row
        
        struggling = False
        reasons = []
        
        # Check time spent vs expected
        if lesson.estimated_minutes:
            expected_seconds = lesson.estimated_minutes * 60
            if progress.time_spent_seconds > expected_seconds * 2:
                struggling = True
                reasons.append(
                    f"Taking {progress.time_spent_seconds // 60}min vs expected {lesson.estimated_minutes}min"
                )
        
        # Check engagement signals
        interactions = progress.interactions or {}
        
        if interactions.get('pauses', 0) > 10:
            struggling = True
            reasons.append(f"High pause count: {interactions['pauses']}")
        
        if interactions.get('rewinds', 0) > 8:
            struggling = True
            reasons.append(f"Frequent rewinds: {interactions['rewinds']}")
        
        # Check completion progress
        if progress.completion_percentage < 50 and progress.time_spent_seconds > expected_seconds:
            struggling = True
            reasons.append("Low completion despite time investment")
        
        return struggling, reasons
    
    async def adjust_difficulty(
        self,
        user_id: UUID,
        current_difficulty: int
    ) -> Tuple[int, str]:
        """
        Recommend difficulty adjustment based on recent performance
        
        Args:
            current_difficulty: Current difficulty level (1-10)
            
        Returns:
            (new_difficulty, reason)
        """
        
        # Get recent assessment performance
        result = await self.db.execute(
            select(
                func.avg(AssessmentAttempt.score_percecntage).label('avg_score'),
                func.count(AssessmentAttempt.id).label('attempt_count')
            )
            .where(
                and_(
                    AssessmentAttempt.user_id == user_id,
                    AssessmentAttempt.attempted_at >= datetime.now() - timedelta(days=7)
                )
            )
        )
        stats = result.first()
        
        if not stats or not stats.attempt_count or stats.attempt_count < 3:
            return current_difficulty, "Not enough data"
        
        avg_score = stats.avg_score
        
        # Adjustment logic
        if avg_score >= 90:
            new_difficulty = min(10, current_difficulty + 1)
            reason = f"Excellent performance ({avg_score:.0f}%) - increasing challenge"
        elif avg_score >= 75:
            new_difficulty = current_difficulty
            reason = f"Good performance ({avg_score:.0f}%) - maintaining level"
        elif avg_score >= 60:
            new_difficulty = current_difficulty
            reason = f"Adequate performance ({avg_score:.0f}%) - stay at current level"
        else:
            new_difficulty = max(1, current_difficulty - 1)
            reason = f"Struggling ({avg_score:.0f}%) - reducing difficulty for mastery"
        
        return new_difficulty, reason
