"""
Create a test user that stays in the database
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.learner_profile import LearnerProfile
from app.core.security import get_password_hash


async def create_test_user():
    async with AsyncSessionLocal() as session:
        # Create user
        user = User(
            email="demo@learningplatform.com",
            password_hash=get_password_hash("demo1234"),
            full_name="Demo User",
            role=UserRole.LEARNER
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        # Create profile
        profile = LearnerProfile(
            user_id=user.id,
            learning_style="visual",
            preferred_pace="medium",
            study_hours_per_week=15,
            skill_levels={
                "python": 6,
                "javascript": 4,
                "sql": 5,
                "git": 7
            },
            knowledge_gaps=[
                "async programming",
                "microservices",
                "docker orchestration"
            ],
            preferred_study_times=[
                {"day": "monday", "hour": 20},
                {"day": "wednesday", "hour": 19},
                {"day": "saturday", "hour": 10}
            ]
        )
        
        session.add(profile)
        await session.commit()
        
        print(f"✅ Created demo user: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Password: demo1234")
        print(f"   Skills: {profile.skill_levels}")


if __name__ == "__main__":
    asyncio.run(create_test_user())