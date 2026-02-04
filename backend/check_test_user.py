"""Check ai_test user's profile"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.learner_profile import LearnerProfile

async def check_test_user():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == "ai_test@example.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ User: {user.email} (ID: {user.id})")
        
        result = await db.execute(
            select(LearnerProfile).where(LearnerProfile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            print(f"✅ Profile exists")
            print(f"   Skill levels: {profile.skill_levels}")
            print(f"   Knowledge gaps: {profile.knowledge_gaps}")
        else:
            print("❌ No profile found")

if __name__ == "__main__":
    asyncio.run(check_test_user())
