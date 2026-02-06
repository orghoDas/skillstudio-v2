"""
Adaptive Assessment System with AI-Powered Feedback
Adjusts question difficulty based on user performance and generates personalized feedback.
"""
from typing import List, Dict, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import random

from ..models.assessment import Assessment, AssessmentQuestion, AssessmentAttempt
from ..models.user import User
from ..models.learner_profile import LearnerProfile


class AdaptiveAssessmentEngine:
    """Adaptive assessment system that adjusts difficulty dynamically"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_next_question(
        self,
        user_id: str,
        assessment_id: str,
        previous_answers: List[Dict] = None
    ) -> Optional[Dict]:
        """
        Get the next question with adaptive difficulty.
        
        Analyzes previous answers to determine user's performance level
        and selects an appropriately challenging next question.
        """
        # Get assessment
        assessment_result = await self.db.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        assessment = assessment_result.scalar_one_or_none()
        
        if not assessment:
            return None
        
        # Get all questions for this assessment
        questions_result = await self.db.execute(
            select(AssessmentQuestion)
            .where(AssessmentQuestion.assessment_id == assessment_id)
            .order_by(AssessmentQuestion.order)
        )
        all_questions = questions_result.scalars().all()
        
        if not all_questions:
            return None
        
        # If no previous answers, start with medium difficulty
        if not previous_answers:
            # Find first question or random medium difficulty question
            medium_questions = [q for q in all_questions if q.difficulty_level == 'MEDIUM']
            if medium_questions:
                question = random.choice(medium_questions)
            else:
                question = all_questions[0]
        else:
            # Calculate user's current performance
            correct_count = sum(1 for ans in previous_answers if ans.get('is_correct', False))
            total_answered = len(previous_answers)
            accuracy = correct_count / total_answered if total_answered > 0 else 0
            
            # Get IDs of answered questions
            answered_ids = [ans['question_id'] for ans in previous_answers]
            
            # Filter unanswered questions
            unanswered = [q for q in all_questions if str(q.id) not in answered_ids]
            
            if not unanswered:
                return None  # All questions answered
            
            # Select difficulty based on performance
            if accuracy >= 0.8:
                # High accuracy - give harder questions
                target_difficulty = 'HARD'
            elif accuracy >= 0.5:
                # Medium accuracy - maintain medium difficulty
                target_difficulty = 'MEDIUM'
            else:
                # Low accuracy - give easier questions
                target_difficulty = 'EASY'
            
            # Find question matching target difficulty
            matching_difficulty = [q for q in unanswered if q.difficulty_level == target_difficulty]
            
            if matching_difficulty:
                question = random.choice(matching_difficulty)
            else:
                # Fallback to any unanswered question
                question = unanswered[0]
        
        return {
            'question_id': str(question.id),
            'question_text': question.question_text,
            'options': question.options,
            'difficulty_level': question.difficulty_level,
            'points': question.points,
            'question_number': len(previous_answers) + 1 if previous_answers else 1,
            'total_questions': len(all_questions)
        }
    
    async def calculate_adaptive_score(
        self,
        answers: List[Dict],
        assessment_id: str
    ) -> Dict:
        """
        Calculate score with difficulty-weighted points.
        Harder questions earn more points.
        """
        # Get all questions
        questions_result = await self.db.execute(
            select(AssessmentQuestion)
            .where(AssessmentQuestion.assessment_id == assessment_id)
        )
        questions = {str(q.id): q for q in questions_result.scalars().all()}
        
        # Difficulty multipliers
        difficulty_multipliers = {
            'EASY': 1.0,
            'MEDIUM': 1.5,
            'HARD': 2.0
        }
        
        total_points_earned = 0
        max_possible_points = 0
        
        for answer in answers:
            question_id = answer.get('question_id')
            is_correct = answer.get('is_correct', False)
            
            if question_id in questions:
                question = questions[question_id]
                base_points = question.points or 10
                multiplier = difficulty_multipliers.get(question.difficulty_level, 1.0)
                
                weighted_points = base_points * multiplier
                max_possible_points += weighted_points
                
                if is_correct:
                    total_points_earned += weighted_points
        
        percentage = (total_points_earned / max_possible_points * 100) if max_possible_points > 0 else 0
        
        return {
            'points_earned': int(total_points_earned),
            'points_possible': int(max_possible_points),
            'percentage': round(percentage, 2),
            'difficulty_breakdown': self._analyze_difficulty_performance(answers, questions)
        }
    
    def _analyze_difficulty_performance(
        self,
        answers: List[Dict],
        questions: Dict
    ) -> Dict:
        """Analyze performance by difficulty level"""
        performance = {
            'EASY': {'correct': 0, 'total': 0},
            'MEDIUM': {'correct': 0, 'total': 0},
            'HARD': {'correct': 0, 'total': 0}
        }
        
        for answer in answers:
            question_id = answer.get('question_id')
            is_correct = answer.get('is_correct', False)
            
            if question_id in questions:
                difficulty = questions[question_id].difficulty_level
                performance[difficulty]['total'] += 1
                if is_correct:
                    performance[difficulty]['correct'] += 1
        
        # Calculate percentages
        for difficulty in performance:
            total = performance[difficulty]['total']
            correct = performance[difficulty]['correct']
            performance[difficulty]['percentage'] = (correct / total * 100) if total > 0 else 0
        
        return performance


class AIFeedbackGenerator:
    """Generate personalized feedback based on assessment performance"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_comprehensive_feedback(
        self,
        user_id: str,
        attempt_id: str
    ) -> Dict:
        """
        Generate AI-powered feedback for an assessment attempt.
        
        Includes:
        - Overall performance analysis
        - Strength areas
        - Improvement areas
        - Personalized recommendations
        - Next steps
        """
        # Get the attempt
        attempt_result = await self.db.execute(
            select(AssessmentAttempt)
            .where(AssessmentAttempt.id == attempt_id)
        )
        attempt = attempt_result.scalar_one_or_none()
        
        if not attempt:
            return {"error": "Attempt not found"}
        
        # Get assessment details
        assessment_result = await self.db.execute(
            select(Assessment)
            .where(Assessment.id == attempt.assessment_id)
        )
        assessment = assessment_result.scalar_one_or_none()
        
        # Get user profile
        profile_result = await self.db.execute(
            select(LearnerProfile)
            .where(LearnerProfile.user_id == user_id)
        )
        profile = profile_result.scalar_one_or_none()
        
        # Get user's other attempts for comparison
        previous_attempts_result = await self.db.execute(
            select(AssessmentAttempt)
            .where(AssessmentAttempt.user_id == user_id)
            .where(AssessmentAttempt.assessment_id == attempt.assessment_id)
            .where(AssessmentAttempt.id != attempt_id)
            .order_by(AssessmentAttempt.attempted_at.desc())
        )
        previous_attempts = previous_attempts_result.scalars().all()
        
        # Analyze performance
        score = float(attempt.score_percecntage)
        passed = attempt.passed
        
        # Generate feedback sections
        feedback = {
            'attempt_id': str(attempt_id),
            'score': score,
            'passed': passed,
            'overall_analysis': self._generate_overall_analysis(score, passed),
            'performance_level': self._determine_performance_level(score),
            'strengths': self._identify_strengths(score, assessment),
            'improvement_areas': self._identify_improvement_areas(score, assessment),
            'recommendations': await self._generate_recommendations(
                score, assessment, profile
            ),
            'progress_comparison': self._compare_with_previous(attempt, previous_attempts),
            'next_steps': self._suggest_next_steps(score, passed, assessment)
        }
        
        return feedback
    
    def _generate_overall_analysis(self, score: float, passed: bool) -> str:
        """Generate overall performance analysis"""
        if score >= 90:
            return f"Outstanding performance! You scored {score:.1f}%, demonstrating excellent mastery of the material. Your understanding of the concepts is exceptional."
        elif score >= 80:
            return f"Great work! You scored {score:.1f}%, showing strong comprehension of the key concepts. You're on the right track."
        elif score >= 70:
            return f"Good effort! You scored {score:.1f}%, indicating solid understanding with room for improvement in some areas."
        elif score >= 60:
            return f"You passed with {score:.1f}%. While you've met the minimum requirements, there are several areas where additional study would be beneficial."
        else:
            return f"You scored {score:.1f}%, which is below the passing threshold. Don't be discouraged - this assessment helps identify areas where you can focus your learning efforts."
    
    def _determine_performance_level(self, score: float) -> str:
        """Categorize performance level"""
        if score >= 90:
            return "EXPERT"
        elif score >= 80:
            return "PROFICIENT"
        elif score >= 70:
            return "COMPETENT"
        elif score >= 60:
            return "DEVELOPING"
        else:
            return "BEGINNER"
    
    def _identify_strengths(self, score: float, assessment: Assessment) -> List[str]:
        """Identify strength areas"""
        strengths = []
        
        if score >= 70:
            skills = assessment.skills_assessed or []
            if skills:
                # Randomly select some skills as strengths (in real implementation, 
                # would analyze individual question performance)
                num_strengths = min(2, len(skills))
                sample_skills = random.sample(skills, num_strengths)
                strengths.extend([
                    f"Strong grasp of {skill}" for skill in sample_skills
                ])
        
        if score >= 80:
            strengths.append("Consistent accuracy across different question types")
        
        if score >= 90:
            strengths.append("Exceptional problem-solving abilities")
        
        return strengths or ["Completed the assessment - this is your baseline for improvement"]
    
    def _identify_improvement_areas(self, score: float, assessment: Assessment) -> List[str]:
        """Identify areas needing improvement"""
        improvement_areas = []
        
        if score < 90:
            skills = assessment.skills_assessed or []
            if skills and score < 70:
                # Suggest reviewing core concepts
                num_areas = min(2, len(skills))
                sample_skills = random.sample(skills, num_areas)
                improvement_areas.extend([
                    f"Review foundational concepts in {skill}" for skill in sample_skills
                ])
        
        if score < 60:
            improvement_areas.append("Focus on building stronger foundations before advancing")
        
        if score < 80:
            improvement_areas.append("Practice applying concepts to different scenarios")
        
        return improvement_areas or ["Continue practicing to maintain your expertise"]
    
    async def _generate_recommendations(
        self,
        score: float,
        assessment: Assessment,
        profile: Optional[LearnerProfile]
    ) -> List[Dict]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Course recommendations based on skills assessed
        skills = assessment.skills_assessed or []
        
        if score < 80 and skills:
            from ..models.course import Course
            
            # Find courses teaching these skills
            courses_result = await self.db.execute(
                select(Course)
                .where(Course.is_published == True)
                .limit(3)
            )
            courses = courses_result.scalars().all()
            
            # Filter courses teaching relevant skills
            relevant_courses = [
                c for c in courses 
                if any(skill in (c.skills_taught or []) for skill in skills)
            ]
            
            for course in relevant_courses[:2]:
                recommendations.append({
                    'type': 'course',
                    'title': f"Study: {course.title}",
                    'description': f"This course covers {', '.join(course.skills_taught or [])}",
                    'course_id': str(course.id)
                })
        
        # Practice recommendation
        if score < 70:
            recommendations.append({
                'type': 'practice',
                'title': 'Practice with hands-on exercises',
                'description': 'Strengthen your understanding through practical application'
            })
        
        # Retake recommendation
        if score < 60:
            recommendations.append({
                'type': 'retake',
                'title': 'Retake this assessment after studying',
                'description': 'Use this as a learning tool to track your progress'
            })
        
        # Advanced learning
        if score >= 85:
            recommendations.append({
                'type': 'advance',
                'title': 'Explore advanced topics',
                'description': 'You\'re ready for more challenging material in this area'
            })
        
        return recommendations
    
    def _compare_with_previous(
        self,
        current_attempt: AssessmentAttempt,
        previous_attempts: List[AssessmentAttempt]
    ) -> Optional[Dict]:
        """Compare with previous attempts"""
        if not previous_attempts:
            return None
        
        latest_previous = previous_attempts[0]
        score_diff = float(current_attempt.score_percecntage) - float(latest_previous.score_percecntage)
        
        if score_diff > 5:
            trend = "improving"
            message = f"Great progress! You improved by {score_diff:.1f}% since your last attempt."
        elif score_diff < -5:
            trend = "declining"
            message = f"Your score decreased by {abs(score_diff):.1f}%. Review the material and try again."
        else:
            trend = "stable"
            message = "Your performance is consistent with your previous attempt."
        
        return {
            'trend': trend,
            'score_change': round(score_diff, 2),
            'previous_score': float(latest_previous.score_percecntage),
            'current_score': float(current_attempt.score_percecntage),
            'message': message,
            'total_attempts': len(previous_attempts) + 1
        }
    
    def _suggest_next_steps(
        self,
        score: float,
        passed: bool,
        assessment: Assessment
    ) -> List[str]:
        """Suggest concrete next steps"""
        next_steps = []
        
        if passed and score >= 80:
            next_steps.append("Apply your knowledge in real-world projects")
            next_steps.append("Share your expertise by helping others learn")
        elif passed:
            next_steps.append("Review areas where you lost points")
            next_steps.append("Take practice quizzes to reinforce learning")
        else:
            next_steps.append("Review the course material thoroughly")
            next_steps.append("Focus on one concept at a time")
            next_steps.append("Retake the assessment when you feel ready")
        
        # Always suggest practical application
        skills = assessment.skills_assessed or []
        if skills:
            next_steps.append(f"Build a project using {skills[0]} to reinforce your learning")
        
        return next_steps
