"""Clear all courses from the database"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.course import Course
from sqlalchemy import delete

async def clear_courses():
    async with AsyncSessionLocal() as db:
        # Delete all courses (cascades to modules, lessons, etc.)
        await db.execute(delete(Course))
        await db.commit()
        print("✅ All courses deleted!")

if __name__ == "__main__":
    asyncio.run(clear_courses())
