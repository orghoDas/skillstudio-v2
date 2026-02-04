"""Debug script to test the full learning path generation"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.recommendation_engine import RecommendationEngine
from app.models.learner_profile import LearnerProfile
from app.models.learning import LearningGoal
from sqlalchemy import select
import uuid

async def test_learning_path():
    async with AsyncSessionLocal() as db:
        # Get the test user
        from app.models.user import User
        result = await db.execute(
            select(User).where(User.email == "demo@learningplatform.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User not found!")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Create a learning goal
        goal = LearningGoal(
            id=uuid.uuid4(),
            user_id=user.id,
            goal_description="Master Python Web Development",
            target_role="Full Stack Developer",
            target_skills=["Python", "FastAPI", "PostgreSQL"]
        )
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
        
        print(f"✅ Created goal: {goal.id}")
        print(f"   Target skills: {goal.target_skills}")
        
        # Generate learning path
        engine = RecommendationEngine(db)
        path, metadata = await engine.generate_learning_path(user.id, goal.id)
        
        print(f"\n📚 Learning Path Generated:")
        print(f"   Total courses: {len(path)}")
        print(f"   Total hours: {metadata.get('total_hours', 0)}")
        print(f"   Estimated weeks: {metadata.get('estimated_weeks', 0)}")
        
        for item in path:
            print(f"\n   {item['sequence']}. {item['title']}")
            print(f"      Skills: {item['skills_covered']}")
            print(f"      Hours: {item['estimated_hours']}")
            print(f"      Reason: {item['reason']}")

if __name__ == "__main__":
    asyncio.run(test_learning_path())
