"""
Skill Assessment Service

Analyzes assessment attempts to:
- Calculate skill proficiency levels (1-10 scale)
- Identify knowledge gaps
- Update learner profiles
- Provide diagnostic insights
"""

from typing import Dict, List, Tuple, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import json

from app.models.assessment import Assessment, AssessmentQuestion, AssessmentAttempt
from app.models.learner_profile import LearnerProfile
from app.models.user import User


class SkillAssessor:
    """Analyzes assessments and updates learner skill profiles"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def process_diagnostic_assessment(
        self,
        user_id: UUID,
        assessment_id: UUID,
        answers: Dict[str, any]
    ) -> Tuple[Dict[str, float], List[str]]:
        """
        Process diagnostic assessment results and update learner profile
        
        Args:
            user_id: User taking the assessment
            assessment_id: Assessment being taken
            answers: Dict mapping question_id to user's answer
            
        Returns:
            Tuple of (skill_levels, knowledge_gaps)
            - skill_levels: {"python": 7.5, "sql": 4.0, ...}
            - knowledge_gaps: ["async_programming", "design_patterns", ...]
        """
        
        # Get all questions for this assessment
        result = await self.db.execute(
            select(AssessmentQuestion)
            .where(AssessmentQuestion.assessment_id == assessment_id)
            .order_by(AssessmentQuestion.sequence_order)
        )
        questions = result.scalars().all()
        
        # Track skill performance
        skill_scores: Dict[str, Dict[str, any]] = {}
        
        for question in questions:
            user_answer = answers.get(str(question.id))
            is_correct = self._check_answer(user_answer, question.correct_answer)
            
            # Process each skill tag
            for skill in question.skill_tags:
                if skill not in skill_scores:
                    skill_scores[skill] = {
                        'correct': 0,
                        'total': 0,
                        'difficulty_sum': 0,
                        'max_difficulty_attempted': 0
                    }
                
                skill_scores[skill]['total'] += 1
                
                if is_correct:
                    skill_scores[skill]['correct'] += 1
                
                skill_scores[skill]['difficulty_sum'] += question.difficulty_level
                skill_scores[skill]['max_difficulty_attempted'] = max(
                    skill_scores[skill]['max_difficulty_attempted'],
                    question.difficulty_level
                )
        
        # Calculate skill levels (1-10 scale)
        skill_levels = {}
        knowledge_gaps = []
        
        for skill, stats in skill_scores.items():
            if stats['total'] == 0:
                continue
                
            accuracy = stats['correct'] / stats['total']
            avg_difficulty = stats['difficulty_sum'] / stats['total']
            
            # Skill level formula:
            # accuracy * difficulty_attempted * confidence_factor
            # Confidence factor increases with more questions answered
            confidence_factor = min(1.0, stats['total'] / 5)  # Full confidence at 5+ questions
            
            raw_score = accuracy * avg_difficulty * confidence_factor
            skill_level = min(10.0, round(raw_score, 1))
            
            skill_levels[skill] = skill_level
            
            # Identify knowledge gaps (skill level < 5 OR low accuracy on easy questions)
            if skill_level < 5.0 or (avg_difficulty <= 3 and accuracy < 0.6):
                knowledge_gaps.append(skill)
        
        # Update learner profile
        await self._update_learner_profile(user_id, skill_levels, knowledge_gaps)
        
        return skill_levels, knowledge_gaps
    
    def _check_answer(self, user_answer: any, correct_answer: Dict) -> bool:
        """
        Check if user's answer is correct
        
        Args:
            user_answer: User's submitted answer
            correct_answer: JSONB from database
            
        Returns:
            True if correct, False otherwise
        """
        if not user_answer:
            return False
        
        answer_type = correct_answer.get('type', 'mcq')
        
        if answer_type == 'mcq':
            # Single choice
            return str(user_answer).strip().lower() == str(correct_answer.get('answer', '')).strip().lower()
        
        elif answer_type == 'multiple_select':
            # Multiple correct answers
            correct_options = set(correct_answer.get('answers', []))
            user_options = set(user_answer if isinstance(user_answer, list) else [user_answer])
            return correct_options == user_options
        
        elif answer_type == 'true_false':
            return bool(user_answer) == bool(correct_answer.get('answer'))
        
        elif answer_type == 'short_answer':
            # Case-insensitive match
            user_text = str(user_answer).strip().lower()
            accepted_answers = correct_answer.get('accepted_answers', [])
            return user_text in [ans.lower() for ans in accepted_answers]
        
        # Default to false for unknown types
        return False
    
    async def _update_learner_profile(
        self,
        user_id: UUID,
        skill_levels: Dict[str, float],
        knowledge_gaps: List[str]
    ):
        """Update learner profile with new skill data"""
        
        # Get existing profile
        result = await self.db.execute(
            select(LearnerProfile).where(LearnerProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            # Create new profile if doesn't exist
            profile = LearnerProfile(
                user_id=user_id,
                skill_levels=skill_levels,
                knowledge_gaps=knowledge_gaps
            )
            self.db.add(profile)
        else:
            # Merge new skill levels with existing (take max)
            existing_skills = profile.skill_levels or {}
            
            for skill, level in skill_levels.items():
                existing_level = existing_skills.get(skill, 0)
                existing_skills[skill] = max(existing_level, level)
            
            profile.skill_levels = existing_skills
            profile.knowledge_gaps = knowledge_gaps
        
        await self.db.commit()
        await self.db.refresh(profile)
    
    async def calculate_skill_from_history(
        self,
        user_id: UUID,
        skill: str
    ) -> Optional[float]:
        """
        Calculate current skill level based on historical assessment performance
        
        Args:
            user_id: User to analyze
            skill: Skill to calculate level for
            
        Returns:
            Skill level (1-10) or None if no data
        """
        
        # Get recent assessment attempts for this skill
        result = await self.db.execute(
            select(AssessmentAttempt)
            .where(AssessmentAttempt.user_id == user_id)
            .order_by(AssessmentAttempt.attempted_at.desc())
            .limit(10)
        )
        attempts = result.scalars().all()
        
        if not attempts:
            return None
        
        # Extract skill scores from attempts
        skill_scores = []
        for attempt in attempts:
            if attempt.skill_scores and skill in attempt.skill_scores:
                skill_scores.append(attempt.skill_scores[skill])
        
        if not skill_scores:
            return None
        
        # Weight recent attempts more heavily
        weighted_sum = 0
        weight_sum = 0
        
        for i, score in enumerate(skill_scores):
            # More recent = higher weight
            weight = 1.0 / (i + 1)
            weighted_sum += score * weight
            weight_sum += weight
        
        return round(weighted_sum / weight_sum * 10, 1)
    
    async def get_skill_breakdown(
        self,
        assessment_attempt_id: UUID
    ) -> Dict[str, Dict[str, any]]:
        """
        Get detailed skill breakdown for an assessment attempt
        
        Returns:
            {
                "skill_name": {
                    "correct": 3,
                    "total": 5,
                    "accuracy": 0.6,
                    "avg_difficulty": 5.2
                },
                ...
            }
        """
        
        result = await self.db.execute(
            select(AssessmentAttempt)
            .where(AssessmentAttempt.id == assessment_attempt_id)
        )
        attempt = result.scalar_one_or_none()
        
        if not attempt:
            return {}
        
        # Get questions for this assessment
        result = await self.db.execute(
            select(AssessmentQuestion)
            .where(AssessmentQuestion.assessment_id == attempt.assessment_id)
        )
        questions = result.scalars().all()
        
        skill_breakdown = {}
        
        for question in questions:
            user_answer = attempt.answers.get(str(question.id))
            is_correct = self._check_answer(user_answer, question.correct_answer)
            
            for skill in question.skill_tags:
                if skill not in skill_breakdown:
                    skill_breakdown[skill] = {
                        'correct': 0,
                        'total': 0,
                        'difficulty_sum': 0
                    }
                
                skill_breakdown[skill]['total'] += 1
                if is_correct:
                    skill_breakdown[skill]['correct'] += 1
                skill_breakdown[skill]['difficulty_sum'] += question.difficulty_level
        
        # Calculate percentages
        for skill, stats in skill_breakdown.items():
            stats['accuracy'] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            stats['avg_difficulty'] = stats['difficulty_sum'] / stats['total'] if stats['total'] > 0 else 0
        
        return skill_breakdown
