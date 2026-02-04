"""Debug why ai_test user gets 0 recommendations"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.learning import LearningGoal
from app.services.recommendation_engine import RecommendationEngine

async def debug_recommendations():
    async with AsyncSessionLocal() as db:
        # Get ai_test user
        result = await db.execute(
            select(User).where(User.email == "ai_test@example.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ User: {user.email}")
        
        # Get their goals
        result = await db.execute(
            select(LearningGoal)
            .where(LearningGoal.user_id == user.id)
            .order_by(LearningGoal.created_at.desc())
            .limit(1)
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            print("❌ No goals found")
            return
        
        print(f"✅ Goal: {goal.goal_description}")
        print(f"   Target skills: {goal.target_skills}")
        
        # Generate learning path
        engine = RecommendationEngine(db)
        path, metadata = await engine.generate_learning_path(user.id, goal.id)
        
        print(f"\n📚 Generated path:")
        print(f"   Courses: {len(path)}")
        print(f"   Total hours: {metadata.get('total_hours', 0)}")
        print(f"   Covered skills: {metadata.get('skills_covered', [])}")
        print(f"   Remaining gaps: {metadata.get('remaining_gaps', [])}")
        
        for item in path:
            print(f"\n   {item['sequence']}. {item['title']}")
            print(f"      Skills: {item['skills_covered']}")

if __name__ == "__main__":
    asyncio.run(debug_recommendations())
