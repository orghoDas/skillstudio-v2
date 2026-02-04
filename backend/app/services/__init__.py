"""
AI Services Module

Core services for personalized learning:
- SkillAssessor: Analyzes assessments and updates learner profiles
- RecommendationEngine: Generates personalized learning paths
- LearningAnalytics: Performance tracking and insights
"""

from app.services.skill_assessment import SkillAssessor
from app.services.recommendation_engine import RecommendationEngine
from app.services.learning_analytics import LearningAnalytics

__all__ = [
    'SkillAssessor',
    'RecommendationEngine',
    'LearningAnalytics'
]
