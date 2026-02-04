"""Debug script to test course recommendations"""
import asyncio
from sqlalchemy import select, and_, cast, ARRAY, String
from app.core.database import AsyncSessionLocal
from app.models.course import Course

async def test_recommendations():
    async with AsyncSessionLocal() as db:
        # Test skills (lowercase)
        skill_gaps = ["python", "fastapi", "postgresql"]
        
        print(f"🔍 Searching for courses with skills: {skill_gaps}")
        
        # Query all courses first
        result = await db.execute(select(Course))
        all_courses = result.scalars().all()
        print(f"\n📚 Total courses in database: {len(all_courses)}")
        for course in all_courses:
            print(f"   - {course.title}: {course.skills_taught} (published: {course.is_published})")
        
        # Now test the filtered query
        result = await db.execute(
            select(Course)
            .where(
                and_(
                    Course.is_published == True,
                    Course.skills_taught.op('?|')(cast(skill_gaps, ARRAY(String)))
                )
            )
        )
        matching_courses = result.scalars().all()
        
        print(f"\n✅ Matching courses: {len(matching_courses)}")
        for course in matching_courses:
            print(f"   - {course.title}: {course.skills_taught}")

if __name__ == "__main__":
    asyncio.run(test_recommendations())
