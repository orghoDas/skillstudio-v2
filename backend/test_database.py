"""
Test database CRUD operations
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.learner_profile import LearnerProfile
from app.core.security import get_password_hash


async def test_create_user():
    """Test creating a user and profile"""
    print("🧪 Testing user creation...")
    
    async with AsyncSessionLocal() as session:
        # Create a test user
        test_user = User(
            email="testuser@example.com",
            password_hash=get_password_hash("testpass123"),
            full_name="Test User",
            role=UserRole.LEARNER
        )
        
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        
        print(f"✅ Created user: {test_user.email} (ID: {test_user.id})")
        
        # Create learner profile
        profile = LearnerProfile(
            user_id=test_user.id,
            learning_style="visual",
            preferred_pace="medium",
            study_hours_per_week=10,
            skill_levels={"python": 5, "sql": 3},
            knowledge_gaps=["async programming", "design patterns"]
        )
        
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        
        print(f"✅ Created profile with skills: {profile.skill_levels}")
        
        return test_user.id


async def test_read_user(user_id):
    """Test reading user with relationship"""
    print("\n🧪 Testing user retrieval...")
    
    async with AsyncSessionLocal() as session:
        # Query user
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        
        print(f"✅ Retrieved user: {user.email}")
        print(f"   Full name: {user.full_name}")
        print(f"   Role: {user.role.value}")
        print(f"   Active: {user.is_active}")
        
        # Access relationship (lazy loading)
        await session.refresh(user, ['learner_profile'])
        
        if user.learner_profile:
            print(f"✅ Has profile with:")
            print(f"   Learning style: {user.learner_profile.learning_style}")
            print(f"   Skills: {user.learner_profile.skill_levels}")
            print(f"   Gaps: {user.learner_profile.knowledge_gaps}")


async def test_update_profile(user_id):
    """Test updating JSONB fields"""
    print("\n🧪 Testing profile update...")
    
    async with AsyncSessionLocal() as session:
        # Get profile
        result = await session.execute(
            select(LearnerProfile).where(LearnerProfile.user_id == user_id)
        )
        profile = result.scalar_one()
        
        # Update skill levels (JSONB)
        old_skills = profile.skill_levels.copy()
        profile.skill_levels = {**profile.skill_levels, "python": 7, "docker": 4}
        
        await session.commit()
        await session.refresh(profile)
        
        print(f"✅ Updated skills:")
        print(f"   Before: {old_skills}")
        print(f"   After: {profile.skill_levels}")


async def test_delete_user(user_id):
    """Test cascade delete"""
    print("\n🧪 Testing cascade delete...")
    
    async with AsyncSessionLocal() as session:
        # Get user
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        
        # Delete user
        await session.delete(user)
        await session.commit()
        
        print(f"✅ Deleted user: {user.email}")
        
        # Check if profile was also deleted (cascade)
        result = await session.execute(
            select(LearnerProfile).where(LearnerProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if profile is None:
            print(f"✅ Profile was automatically deleted (cascade worked!)")
        else:
            print(f"❌ Profile still exists (cascade failed)")


async def main():
    print("="*60)
    print("DATABASE OPERATIONS TEST")
    print("="*60)
    print()
    
    try:
        # Create
        user_id = await test_create_user()
        
        # Read
        await test_read_user(user_id)
        
        # Update
        await test_update_profile(user_id)
        
        # Delete
        await test_delete_user(user_id)
        
        print()
        print("="*60)
        print("✅ ALL DATABASE TESTS PASSED!")
        print("="*60)
        
    except Exception as e:
        print()
        print("="*60)
        print(f"❌ TEST FAILED: {e}")
        print("="*60)
        raise


if __name__ == "__main__":
    asyncio.run(main())