"""
Seed database with sample courses, modules, lessons, and assessments
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.course import Course, Module, Lesson, DifficultyLevel, ContentType


async def create_python_fundamentals_course(db: AsyncSession, user_id):
    """Create Python Fundamentals course with modules and lessons"""
    print("📚 Creating Python Fundamentals Course...")
    
    course = Course(
        title="Python Fundamentals",
        short_description="Learn Python programming from scratch",
        description="Master the basics of Python programming from variables to functions",
        difficulty_level=DifficultyLevel.BEGINNER,
        estimated_duration_hours=20,
        skills_taught=["python", "programming", "variables", "functions", "loops", "classes"],
        prerequisites=[],
        is_published=True,
        created_by=user_id
    )
    db.add(course)
    await db.flush()
    
    # Module 1: Python Basics
    module1 = Module(
        course_id=course.id,
        title="Python Basics",
        description="Introduction to Python and basic concepts",
        sequence_order=1
    )
    db.add(module1)
    await db.flush()
    
    # Lessons for Module 1
    lessons1 = [
        Lesson(
            module_id=module1.id,
            title="Introduction to Python",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/python-intro.mp4",
            content_body="What is Python and why learn it? Python is a versatile programming language.",
            estimated_minutes=15,
            sequence_order=1,
            skill_tags=["python-basics"],
            learning_objectives=["Understand what Python is", "Learn Python's use cases"],
            is_published=True
        ),
        Lesson(
            module_id=module1.id,
            title="Variables and Data Types",
            content_type=ContentType.ARTICLE,
            content_body="Understanding variables, strings, numbers, and booleans in Python.",
            estimated_minutes=20,
            sequence_order=2,
            skill_tags=["variables", "data-types"],
            learning_objectives=["Declare variables", "Use different data types"],
            is_published=True
        ),
        Lesson(
            module_id=module1.id,
            title="Python Operators",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/operators.mp4",
            content_body="Arithmetic, comparison, and logical operators in Python.",
            estimated_minutes=25,
            sequence_order=3,
            skill_tags=["operators", "expressions"],
            learning_objectives=["Use arithmetic operators", "Apply logical operators"],
            is_published=True
        )
    ]
    for lesson in lessons1:
        db.add(lesson)
    
    # Module 2: Control Flow
    module2 = Module(
        course_id=course.id,
        title="Control Flow & Functions",
        description="Learn if statements, loops, and functions",
        sequence_order=2
    )
    db.add(module2)
    await db.flush()
    
    # Lessons for Module 2
    lessons2 = [
        Lesson(
            module_id=module2.id,
            title="If Statements & Conditionals",
            content_type=ContentType.ARTICLE,
            content_body="Making decisions in your code with if/elif/else statements.",
            estimated_minutes=30,
            sequence_order=1,
            skill_tags=["conditionals", "control-flow"],
            learning_objectives=["Write if/elif/else statements", "Use boolean logic"],
            is_published=True
        ),
        Lesson(
            module_id=module2.id,
            title="Loops: For and While",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/loops.mp4",
            content_body="Repeating actions with for and while loops.",
            estimated_minutes=35,
            sequence_order=2,
            skill_tags=["loops", "iteration"],
            learning_objectives=["Write for loops", "Write while loops", "Use break/continue"],
            is_published=True
        ),
        Lesson(
            module_id=module2.id,
            title="Functions in Python",
            content_type=ContentType.ARTICLE,
            content_body="Creating reusable code with functions, parameters, and return values.",
            estimated_minutes=40,
            sequence_order=3,
            skill_tags=["functions", "code-reuse"],
            learning_objectives=["Define functions", "Use parameters and return values"],
            is_published=True
        )
    ]
    for lesson in lessons2:
        db.add(lesson)
    
    await db.commit()
    print(f"✅ Created Python Fundamentals course with {len(lessons1) + len(lessons2)} lessons")
    return course


async def create_fastapi_course(db: AsyncSession, user_id):
    """Create FastAPI Web Development course"""
    print("📚 Creating FastAPI Web Development Course...")
    
    course = Course(
        title="FastAPI Web Development",
        short_description="Master FastAPI framework for building APIs",
        description="Build modern REST APIs with FastAPI and async Python",
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        estimated_duration_hours=15,
        skills_taught=["fastapi", "rest-api", "async-python", "pydantic", "web-development"],
        prerequisites=["python", "functions", "classes"],
        is_published=True,
        created_by=user_id
    )
    db.add(course)
    await db.flush()
    
    # Module 1: FastAPI Basics
    module = Module(
        course_id=course.id,
        title="FastAPI Basics",
        description="Introduction to FastAPI framework",
        sequence_order=1
    )
    db.add(module)
    await db.flush()
    
    lessons = [
        Lesson(
            module_id=module.id,
            title="What is FastAPI?",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/fastapi-intro.mp4",
            content_body="Introduction to FastAPI and its advantages over other frameworks.",
            estimated_minutes=20,
            sequence_order=1,
            skill_tags=["fastapi", "web-apis"],
            learning_objectives=["Understand FastAPI basics", "Compare with other frameworks"],
            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Your First FastAPI App",
            content_type=ContentType.ARTICLE,
            content_body="Creating a simple Hello World API with FastAPI.",
            estimated_minutes=30,
            sequence_order=2,
            skill_tags=["fastapi", "endpoints"],
            learning_objectives=["Create API endpoints", "Run FastAPI server"],
            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Path Parameters and Query Params",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/fastapi-params.mp4",
            content_body="Handling URL parameters and query parameters in FastAPI.",
            estimated_minutes=35,
            sequence_order=3,
            skill_tags=["fastapi", "routing", "parameters"],
            learning_objectives=["Use path parameters", "Use query parameters"],
            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Request Body and Pydantic Models",
            content_type=ContentType.ARTICLE,
            content_body="Using Pydantic models for request validation and serialization.",
            estimated_minutes=40,
            sequence_order=4,
            skill_tags=["pydantic", "validation", "models"],
            learning_objectives=["Create Pydantic models", "Validate request data"],
            is_published=True
        )
    ]
    for lesson in lessons:
        db.add(lesson)
    
    await db.commit()
    print(f"✅ Created FastAPI course with {len(lessons)} lessons")
    return course


async def create_database_course(db: AsyncSession, user_id):
    """Create PostgreSQL & Databases course"""
    print("📚 Creating PostgreSQL & Databases Course...")
    
    course = Course(
        title="PostgreSQL & Databases",
        short_description="Master relational databases with PostgreSQL",
        description="Learn SQL, database design, and PostgreSQL administration",
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        estimated_duration_hours=18,
        skills_taught=["sql", "postgresql", "database-design", "queries", "joins"],
        prerequisites=["python"],
        is_published=True,
        created_by=user_id
    )
    db.add(course)
    await db.flush()
    
    # Module 1: SQL Basics
    module = Module(
        course_id=course.id,
        title="SQL Basics",
        description="Learn SQL query language",
        sequence_order=1
    )
    db.add(module)
    await db.flush()
    
    lessons = [
        Lesson(
            module_id=module.id,
            title="Database Fundamentals",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/db-fundamentals.mp4",
            content_body="What are databases and why use them? Understanding relational databases.",
            estimated_minutes=25,
            sequence_order=1,
            skill_tags=["databases", "sql-basics"],
            learning_objectives=["Understand database concepts", "Learn about relational databases"],
            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="SELECT Queries",
            content_type=ContentType.ARTICLE,
            content_body="Querying data with SELECT statements, filtering with WHERE.",
            estimated_minutes=30,
            sequence_order=2,
            skill_tags=["sql", "queries", "select"],
            learning_objectives=["Write SELECT queries", "Use WHERE clauses"],
            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="SQL Joins",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/sql-joins.mp4",
            content_body="Combining data from multiple tables with INNER, LEFT, and RIGHT joins.",
            estimated_minutes=45,
            sequence_order=3,
            skill_tags=["sql", "joins", "relationships"],
            learning_objectives=["Use INNER JOIN", "Use LEFT/RIGHT JOIN", "Understand relationships"],
            is_published=True
        )
    ]
    for lesson in lessons:
        db.add(lesson)
    
    await db.commit()
    print(f"✅ Created Database course with {len(lessons)} lessons")
    return course


async def create_advanced_python_course(db: AsyncSession, user_id):
    """Create Advanced Python course"""
    print("📚 Creating Advanced Python Course...")
    
    course = Course(
        title="Advanced Python",
        short_description="Advanced Python concepts and patterns",
        description="Deep dive into decorators, generators, async/await, and more",
        difficulty_level=DifficultyLevel.ADVANCED,
        estimated_duration_hours=25,
        skills_taught=["decorators", "generators", "async-programming", "context-managers", "metaclasses"],
        prerequisites=["python", "functions", "classes", "oop"],
        is_published=True,
        created_by=user_id
    )
    db.add(course)
    await db.flush()
    
    # Module 1: Advanced Concepts
    module = Module(
        course_id=course.id,
        title="Advanced Concepts",
        description="Decorators, generators, and context managers",
        sequence_order=1
    )
    db.add(module)
    await db.flush()
    
    lessons = [
        Lesson(
            module_id=module.id,
            title="Decorators",
            content_type=ContentType.ARTICLE,
            content_body="Understanding and creating decorators for function modification.",
            estimated_minutes=50,
            sequence_order=1,
            skill_tags=["decorators", "python-advanced", "functions"],
            learning_objectives=["Understand decorators", "Create custom decorators"],
            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Generators",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/generators.mp4",
            content_body="Lazy evaluation with generators and the yield keyword.",
            estimated_minutes=45,
            sequence_order=2,
            skill_tags=["generators", "iterators", "yield"],
            learning_objectives=["Create generators", "Use yield", "Understand lazy evaluation"],
            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Async/Await",
            content_type=ContentType.ARTICLE,
            content_body="Asynchronous programming with asyncio, async/await syntax.",
            estimated_minutes=60,
            sequence_order=3,
            skill_tags=["async", "concurrency", "asyncio"],
            learning_objectives=["Write async functions", "Use await", "Understand event loops"],
            is_published=True
        )
    ]
    for lesson in lessons:
        db.add(lesson)
    
    await db.commit()
    print(f"✅ Created Advanced Python course with {len(lessons)} lessons")
    return course


async def create_data_science_course(db: AsyncSession, user_id):
    """Create Data Science course"""
    print("📚 Creating Data Science Course...")
    
    course = Course(
        title="Data Science with Python",
        short_description="Introduction to data science and ML",
        description="Learn data analysis, visualization, and machine learning basics",
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        estimated_duration_hours=30,
        skills_taught=["numpy", "pandas", "matplotlib", "data-analysis", "machine-learning"],
        prerequisites=["python", "functions", "classes"],
        is_published=True,
        created_by=user_id
    )
    db.add(course)
    await db.flush()
    
    # Module 1: Data Analysis
    module = Module(
        course_id=course.id,
        title="Data Analysis Basics",
        description="Working with data using Pandas and NumPy",
        sequence_order=1
    )
    db.add(module)
    await db.flush()
    
    lessons = [
        Lesson(
            module_id=module.id,
            title="NumPy Basics",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/numpy.mp4",
            content_body="Arrays and numerical computing with NumPy.",
            estimated_minutes=35,
            sequence_order=1,
            skill_tags=["numpy", "data-science", "arrays"],
            learning_objectives=["Create NumPy arrays", "Perform array operations"],
            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Pandas DataFrames",
            content_type=ContentType.ARTICLE,
            content_body="Working with tabular data using Pandas DataFrames.",
            estimated_minutes=40,
            sequence_order=2,
            skill_tags=["pandas", "data-analysis", "dataframes"],
            learning_objectives=["Create DataFrames", "Filter and transform data"],
            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Data Visualization",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/visualization.mp4",
            content_body="Creating charts with Matplotlib and Seaborn libraries.",
            estimated_minutes=45,
            sequence_order=3,
            skill_tags=["visualization", "matplotlib", "seaborn"],
            learning_objectives=["Create line charts", "Create bar charts", "Customize plots"],
            is_published=True
        )
    ]
    for lesson in lessons:
        db.add(lesson)
    
    await db.commit()
    print(f"✅ Created Data Science course with {len(lessons)} lessons")
    return course


async def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    
    async with AsyncSessionLocal() as db:
        # Find test user
        result = await db.execute(select(User).where(User.email == "demo@learningplatform.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Demo user not found. Please run create_test_user.py first.")
            return
        
        print(f"✅ Found test user: {user.email}")
        
        # Create courses
        await create_python_fundamentals_course(db, user.id)
        await create_fastapi_course(db, user.id)
        await create_database_course(db, user.id)
        await create_advanced_python_course(db, user.id)
        await create_data_science_course(db, user.id)
        
        print("\n🎉 Database seeding completed successfully!")
        print("📊 Summary:")
        print("  - 5 courses created")
        print("  - Multiple modules per course")
        print("  - Multiple lessons per module")


if __name__ == "__main__":
    asyncio.run(main())
