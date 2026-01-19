"""
Complete setup verification
"""
import asyncio
from sqlalchemy import text
from app.core.config import settings
from app.core.database import engine

async def verify_async_driver():
    """Verify we're using asyncpg"""
    print("🔍 Checking database configuration...")
    
    # Check URL
    if "+asyncpg" in settings.DATABASE_URL:
        print("✅ Using asyncpg (async driver)")
    else:
        print("❌ ERROR: Not using asyncpg!")
        print(f"   Current URL starts with: {settings.DATABASE_URL[:30]}...")
        return False
    
    # Test connection
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 'Connection successful!' as message"))
            message = result.scalar()
            print(f"✅ Database connected: {message}")
            
            # Check driver
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ PostgreSQL version: {version[:50]}...")
            
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def verify_models():
    """Verify models are importable"""
    print("\n🔍 Checking models...")
    
    try:
        from app.models.user import User, UserRole
        from app.models.learner_profile import LearnerProfile
        
        print(f"✅ User model: {User.__tablename__}")
        print(f"✅ LearnerProfile model: {LearnerProfile.__tablename__}")
        print(f"✅ UserRole enum: {[r.value for r in UserRole]}")
        
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

async def main():
    print("="*60)
    print("LEARNING PLATFORM - SETUP VERIFICATION")
    print("="*60)
    print()
    
    driver_ok = await verify_async_driver()
    models_ok = await verify_models()
    
    print()
    print("="*60)
    if driver_ok and models_ok:
        print("✅ ALL CHECKS PASSED - Ready to create migrations!")
    else:
        print("❌ SOME CHECKS FAILED - Please fix errors above")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())