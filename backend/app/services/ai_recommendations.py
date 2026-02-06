"""
AI-Powered Recommendation Engine
Generates personalized course recommendations based on user profile, skills, goals, and progress.
"""
from typing import List, Dict, Optional, Tuple
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter
import math

from ..models.user import User
from ..models.learner_profile import LearnerProfile
from ..models.course import Course
from ..models.learning import Enrollment, LessonProgress, LearningGoal
from ..models.assessment import AssessmentAttempt


class RecommendationEngine:
    """AI-powered course recommendation system"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_personalized_recommendations(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """
        Generate personalized course recommendations for a user.
        
        Scoring factors:
        - Skill match (40%): How well course skills align with user's goals
        - Difficulty match (20%): Appropriate challenge level
        - Learning goal alignment (25%): Matches user's learning objectives
        - Popularity (10%): Courses with high enrollment/completion
        - Prerequisite readiness (5%): User has completed prerequisites
        """
        # Get user profile and context
        user_context = await self._get_user_context(user_id)
        
        # Get all available courses (not enrolled)
        available_courses = await self._get_available_courses(user_id)
        
        # Score each course
        scored_courses = []
        for course in available_courses:
            score = await self._calculate_recommendation_score(course, user_context)
            scored_courses.append({
                'course': course,
                'score': score,
                'reasons': await self._generate_recommendation_reasons(course, user_context, score)
            })
        
        # Sort by score and return top recommendations
        scored_courses.sort(key=lambda x: x['score']['total'], reverse=True)
        
        return [
            {
                'course_id': str(sc['course'].id),
                'title': sc['course'].title,
                'description': sc['course'].description,
                'difficulty_level': sc['course'].difficulty_level,
                'estimated_duration_hours': sc['course'].estimated_duration_hours,
                'skills_taught': sc['course'].skills_taught,
                'recommendation_score': round(sc['score']['total'], 2),
                'score_breakdown': {
                    'skill_match': round(sc['score']['skill_match'], 2),
                    'difficulty_match': round(sc['score']['difficulty_match'], 2),
                    'goal_alignment': round(sc['score']['goal_alignment'], 2),
                    'popularity': round(sc['score']['popularity'], 2),
                    'prerequisite_ready': round(sc['score']['prerequisite_ready'], 2)
                },
                'reasons': sc['reasons']
            }
            for sc in scored_courses[:limit]
        ]
    
    async def _get_user_context(self, user_id: str) -> Dict:
        """Gather comprehensive user context for recommendations"""
        # Get user and profile
        result = await self.db.execute(
            select(User, LearnerProfile)
            .join(LearnerProfile, User.id == LearnerProfile.user_id)
            .where(User.id == user_id)
        )
        row = result.first()
        if not row:
            return {}
        
        user, profile = row
        
        # Get learning goals
        goals_result = await self.db.execute(
            select(LearningGoal)
            .where(LearningGoal.user_id == user_id)
            .where(LearningGoal.current_status == 'ACTIVE')
        )
        goals = goals_result.scalars().all()
        
        # Get completed courses
        completed_result = await self.db.execute(
            select(Enrollment)
            .where(Enrollment.user_id == user_id)
            .where(Enrollment.progress_percentage == 100)
        )
        completed_enrollments = completed_result.scalars().all()
        
        # Get assessment performance
        assessments_result = await self.db.execute(
            select(AssessmentAttempt)
            .where(AssessmentAttempt.user_id == user_id)
            .order_by(AssessmentAttempt.attempted_at.desc())
            .limit(10)
        )
        recent_assessments = assessments_result.scalars().all()
        
        # Calculate average performance
        avg_score = 0
        if recent_assessments:
            avg_score = sum(float(a.score_percecntage) for a in recent_assessments) / len(recent_assessments)
        
        # Extract target skills from goals
        target_skills = []
        for goal in goals:
            if goal.target_skills:
                target_skills.extend(goal.target_skills)
        
        return {
            'user': user,
            'profile': profile,
            'current_skills': profile.skill_levels or {},
            'target_skills': list(set(target_skills)),
            'learning_goals': goals,
            'completed_course_ids': [str(e.course_id) for e in completed_enrollments],
            'avg_assessment_score': avg_score,
            'preferred_difficulty': 'INTERMEDIATE',  # Default since not in profile
            'learning_style': profile.learning_style or 'VISUAL'
        }
    
    async def _get_available_courses(self, user_id: str) -> List[Course]:
        """Get courses user hasn't enrolled in yet"""
        # Get enrolled course IDs
        enrolled_result = await self.db.execute(
            select(Enrollment.course_id)
            .where(Enrollment.user_id == user_id)
        )
        enrolled_ids = [str(row[0]) for row in enrolled_result.all()]
        
        # Get all published courses not enrolled
        courses_result = await self.db.execute(
            select(Course)
            .where(Course.is_published == True)
            .where(~Course.id.in_(enrolled_ids) if enrolled_ids else True)
        )
        
        return courses_result.scalars().all()
    
    async def _calculate_recommendation_score(self, course: Course, context: Dict) -> Dict:
        """Calculate multi-factor recommendation score"""
        scores = {
            'skill_match': 0,
            'difficulty_match': 0,
            'goal_alignment': 0,
            'popularity': 0,
            'prerequisite_ready': 0
        }
        
        # 1. Skill Match (40% weight)
        if context.get('target_skills'):
            course_skills = set(course.skills_taught or [])
            target_skills = set(context['target_skills'])
            
            if course_skills and target_skills:
                skill_overlap = len(course_skills & target_skills)
                skill_union = len(course_skills | target_skills)
                scores['skill_match'] = (skill_overlap / skill_union) * 40 if skill_union > 0 else 0
        
        # 2. Difficulty Match (20% weight)
        preferred_difficulty = context.get('preferred_difficulty', 'INTERMEDIATE')
        difficulty_map = {'BEGINNER': 1, 'INTERMEDIATE': 2, 'ADVANCED': 3, 'EXPERT': 4}
        
        course_level = difficulty_map.get(course.difficulty_level, 2)
        preferred_level = difficulty_map.get(preferred_difficulty, 2)
        
        # Score higher if difficulty is appropriate (same or one level higher)
        diff = abs(course_level - preferred_level)
        if diff == 0:
            scores['difficulty_match'] = 20
        elif diff == 1 and course_level > preferred_level:
            scores['difficulty_match'] = 15  # Slightly challenging is good
        elif diff == 1:
            scores['difficulty_match'] = 10
        else:
            scores['difficulty_match'] = max(0, 20 - (diff * 5))
        
        # 3. Learning Goal Alignment (25% weight)
        for goal in context.get('learning_goals', []):
            # Check if course skills match goal target skills
            goal_skills = set(goal.target_skills or [])
            course_skills = set(course.skills_taught or [])
            
            if goal_skills & course_skills:
                scores['goal_alignment'] += 15
            
            # Check if course title/description mentions target role
            if goal.target_role:
                role_keywords = goal.target_role.lower().split()
                course_text = f"{course.title} {course.description}".lower()
                if any(keyword in course_text for keyword in role_keywords):
                    scores['goal_alignment'] += 10
        
        scores['goal_alignment'] = min(scores['goal_alignment'], 25)
        
        # 4. Popularity (10% weight)
        # Normalize enrollment count (assuming max 1000 enrollments)
        enrollments = course.total_enrollments or 0
        scores['popularity'] = min((enrollments / 100) * 10, 10)
        
        # 5. Prerequisite Readiness (5% weight)
        prerequisites = set(course.prerequisites or [])
        current_skills = set(context.get('current_skills', {}).keys())
        completed_courses = context.get('completed_course_ids', [])
        
        if not prerequisites:
            scores['prerequisite_ready'] = 5  # No prerequisites = ready
        else:
            # Check if user has the prerequisite skills
            met_prereqs = len(prerequisites & current_skills)
            total_prereqs = len(prerequisites)
            scores['prerequisite_ready'] = (met_prereqs / total_prereqs) * 5 if total_prereqs > 0 else 0
        
        # Calculate total
        scores['total'] = sum(scores.values())
        
        return scores
    
    async def _generate_recommendation_reasons(
        self, 
        course: Course, 
        context: Dict, 
        scores: Dict
    ) -> List[str]:
        """Generate human-readable reasons for recommendation"""
        reasons = []
        
        # Skill match reasons
        if scores['skill_match'] > 20:
            course_skills = set(course.skills_taught or [])
            target_skills = set(context.get('target_skills', []))
            matching_skills = list(course_skills & target_skills)
            if matching_skills:
                reasons.append(f"Teaches {', '.join(matching_skills[:3])} - skills you're targeting")
        
        # Difficulty reasons
        if scores['difficulty_match'] >= 15:
            reasons.append(f"Perfect difficulty level for your current expertise")
        
        # Goal alignment
        if scores['goal_alignment'] > 15:
            for goal in context.get('learning_goals', []):
                if goal.target_role and goal.target_role.lower() in course.title.lower():
                    reasons.append(f"Aligns with your goal: {goal.goal_description}")
                    break
        
        # Popularity
        if scores['popularity'] > 5:
            reasons.append(f"Popular course with {course.total_enrollments}+ students")
        
        # Quick win
        if course.estimated_duration_hours and course.estimated_duration_hours <= 10:
            reasons.append("Quick to complete - great for building momentum")
        
        # Trending
        if course.difficulty_level == 'BEGINNER' and context.get('current_skills', {}):
            if len(context['current_skills']) < 3:
                reasons.append("Great foundation course for beginners")
        
        return reasons[:4]  # Return top 4 reasons


class LearningPathGenerator:
    """Generate personalized learning paths"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_learning_path(
        self, 
        user_id: str, 
        goal_id: Optional[str] = None
    ) -> Dict:
        """
        Generate a sequential learning path to achieve a goal.
        
        Returns a structured path with:
        - Current skill level assessment
        - Ordered sequence of courses
        - Estimated timeline
        - Milestones
        """
        # Get user context
        user_result = await self.db.execute(
            select(User, LearnerProfile)
            .join(LearnerProfile, User.id == LearnerProfile.user_id)
            .where(User.id == user_id)
        )
        row = user_result.first()
        if not row:
            return {"error": "User not found"}
        
        user, profile = row
        
        # Get specific goal or primary goal
        if goal_id:
            goal_result = await self.db.execute(
                select(LearningGoal)
                .where(LearningGoal.id == goal_id)
                .where(LearningGoal.user_id == user_id)
            )
            goal = goal_result.scalar_one_or_none()
        else:
            goal_result = await self.db.execute(
                select(LearningGoal)
                .where(LearningGoal.user_id == user_id)
                .where(LearningGoal.current_status == 'ACTIVE')
                .order_by(LearningGoal.created_at.desc())
                .limit(1)
            )
            goal = goal_result.scalar_one_or_none()
        
        if not goal:
            return {"error": "No active learning goal found"}
        
        # Get current skills
        current_skills = set((profile.skill_levels or {}).keys())
        target_skills = set(goal.target_skills or [])
        
        # Identify skill gaps
        skill_gaps = target_skills - current_skills
        
        # Find courses that teach missing skills
        courses_result = await self.db.execute(
            select(Course)
            .where(Course.is_published == True)
        )
        all_courses = courses_result.scalars().all()
        
        # Build learning path
        path_courses = []
        learned_skills = current_skills.copy()
        
        # Iteratively add courses that teach new required skills
        max_iterations = 20
        iteration = 0
        
        while skill_gaps and iteration < max_iterations:
            iteration += 1
            best_course = None
            best_score = 0
            
            for course in all_courses:
                if course in [pc['course'] for pc in path_courses]:
                    continue
                
                course_skills = set(course.skills_taught or [])
                prerequisites = set(course.prerequisites or [])
                
                # Check if prerequisites are met
                if prerequisites and not prerequisites.issubset(learned_skills):
                    continue
                
                # Calculate how many gap skills this course teaches
                new_skills = course_skills & skill_gaps
                score = len(new_skills)
                
                # Bonus for teaching multiple gap skills
                score += len(new_skills) * 0.5
                
                # Prefer shorter courses early
                if course.estimated_duration_hours:
                    score += (1 / course.estimated_duration_hours) * 2
                
                if score > best_score:
                    best_score = score
                    best_course = course
            
            if best_course:
                path_courses.append({
                    'course': best_course,
                    'skills_to_learn': list(set(best_course.skills_taught or []) & skill_gaps),
                    'sequence_number': len(path_courses) + 1
                })
                learned_skills.update(best_course.skills_taught or [])
                skill_gaps = target_skills - learned_skills
            else:
                break
        
        # Calculate timeline
        total_hours = sum(
            pc['course'].estimated_duration_hours or 0 
            for pc in path_courses
        )
        
        # Estimate weeks based on study hours per week
        study_hours_per_week = profile.study_hours_per_week or 5
        estimated_weeks = math.ceil(total_hours / study_hours_per_week) if study_hours_per_week > 0 else 0
        
        return {
            'goal': {
                'id': str(goal.id),
                'description': goal.goal_description,
                'target_role': goal.target_role,
                'target_skills': goal.target_skills,
                'target_date': goal.target_completion_date.isoformat() if goal.target_completion_date else None
            },
            'current_skills': list(current_skills),
            'skills_to_learn': list(target_skills - current_skills),
            'learning_path': [
                {
                    'sequence': pc['sequence_number'],
                    'course_id': str(pc['course'].id),
                    'title': pc['course'].title,
                    'difficulty': pc['course'].difficulty_level,
                    'duration_hours': pc['course'].estimated_duration_hours,
                    'skills_gained': pc['skills_to_learn'],
                    'prerequisites': pc['course'].prerequisites
                }
                for pc in path_courses
            ],
            'timeline': {
                'total_hours': total_hours,
                'estimated_weeks': estimated_weeks,
                'study_hours_per_week': study_hours_per_week
            },
            'completion_percentage': int((len(learned_skills & target_skills) / len(target_skills)) * 100) if target_skills else 0
        }


class SkillGapAnalyzer:
    """Analyze skill gaps and provide insights"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_skill_gaps(self, user_id: str) -> Dict:
        """
        Comprehensive skill gap analysis.
        
        Returns:
        - Current skill proficiency levels
        - Target skills from goals
        - Identified gaps
        - Recommended focus areas
        - Strength areas
        """
        # Get user and profile
        user_result = await self.db.execute(
            select(User, LearnerProfile)
            .join(LearnerProfile, User.id == LearnerProfile.user_id)
            .where(User.id == user_id)
        )
        row = user_result.first()
        if not row:
            return {"error": "User not found"}
        
        user, profile = row
        
        # Get all learning goals
        goals_result = await self.db.execute(
            select(LearningGoal)
            .where(LearningGoal.user_id == user_id)
            .where(LearningGoal.current_status == 'ACTIVE')
        )
        goals = goals_result.scalars().all()
        
        # Get assessment results to gauge proficiency
        assessments_result = await self.db.execute(
            select(AssessmentAttempt)
            .where(AssessmentAttempt.user_id == user_id)
            .order_by(AssessmentAttempt.attempted_at.desc())
        )
        assessments = assessments_result.scalars().all()
        
        # Analyze current skills
        current_skills = profile.skill_levels or {}
        
        # Aggregate target skills from all goals
        all_target_skills = set()
        for goal in goals:
            if goal.target_skills:
                all_target_skills.update(goal.target_skills)
        
        # Identify gaps
        skill_gaps = []
        for target_skill in all_target_skills:
            current_level = current_skills.get(target_skill, 0)
            gap = {
                'skill': target_skill,
                'current_level': current_level,
                'target_level': 'proficient',
                'gap_size': 'large' if current_level < 3 else 'medium' if current_level < 7 else 'small',
                'priority': 'high' if current_level < 3 else 'medium' if current_level < 7 else 'low'
            }
            skill_gaps.append(gap)
        
        # Identify strengths
        strengths = [
            {'skill': skill, 'level': level}
            for skill, level in current_skills.items()
            if level >= 7
        ]
        
        # Recommendations
        recommendations = []
        
        # High priority gaps
        high_priority = [gap for gap in skill_gaps if gap['priority'] == 'high']
        if high_priority:
            recommendations.append({
                'type': 'focus_area',
                'message': f"Focus on foundational skills: {', '.join([g['skill'] for g in high_priority[:3]])}",
                'skills': [g['skill'] for g in high_priority]
            })
        
        # Leverage strengths
        if strengths:
            recommendations.append({
                'type': 'leverage_strength',
                'message': f"Build on your strengths in {', '.join([s['skill'] for s in strengths[:2]])}",
                'skills': [s['skill'] for s in strengths]
            })
        
        return {
            'user_id': str(user_id),
            'current_skills': current_skills,
            'target_skills': list(all_target_skills),
            'skill_gaps': sorted(skill_gaps, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']]),
            'strengths': strengths,
            'recommendations': recommendations,
            'overall_readiness': self._calculate_readiness(current_skills, all_target_skills)
        }
    
    def _calculate_readiness(self, current_skills: Dict, target_skills: set) -> Dict:
        """Calculate overall readiness percentage"""
        if not target_skills:
            return {'percentage': 100, 'status': 'ready'}
        
        total_target_skills = len(target_skills)
        acquired_skills = sum(1 for skill in target_skills if current_skills.get(skill, 0) >= 7)
        
        percentage = int((acquired_skills / total_target_skills) * 100)
        
        if percentage >= 80:
            status = 'ready'
        elif percentage >= 50:
            status = 'progressing'
        else:
            status = 'building_foundation'
        
        return {
            'percentage': percentage,
            'status': status,
            'acquired_skills': acquired_skills,
            'total_target_skills': total_target_skills
        }
