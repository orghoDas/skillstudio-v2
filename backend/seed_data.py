"""
Seed the database with sample courses, lessons, and assessments
Run: python seed_data.py
"""
import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.course import Course, Module, Lesson, DifficultyLevel, ContentType
from app.models.assessment import Assessment, AssessmentQuestion
from app.models.learning import LearningGoal, Enrollment, LessonProgress, GoalStatus, ProgressStatus


async def clear_existing_data(db: AsyncSession):
    """Clear existing course data (optional - be careful!)"""
    print("⚠️  Clearing existing course data...")
    
    # Delete in order of dependencies
    await db.execute("DELETE FROM lesson_progress")
    await db.execute("DELETE FROM enrollments")
    await db.execute("DELETE FROM assessment_questions")
    await db.execute("DELETE FROM assessment_attempts")
    await db.execute("DELETE FROM assessments")
    await db.execute("DELETE FROM lessons")
    await db.execute("DELETE FROM modules")
    await db.execute("DELETE FROM courses")
    
    await db.commit()
    print("✅ Existing data cleared")


async def create_python_fundamentals_course(db: AsyncSession, instructor_id: uuid.UUID):
    """Create Python Fundamentals course"""
    print("\n📚 Creating Python Fundamentals Course...")
    
    course = Course(
        title="Python Fundamentals",
        content_body="Master the basics of Python programming from variables to functions",
        short_content_body="Learn Python programming from scratch",
        difficulty_level=DifficultyLevel.BEGINNER,
        estimated_duration_hours=20,
        skills_taught=["Python", "Programming Basics", "Data Types", "Functions"],
        prerequisites=[],
        created_by=instructor_id,
        is_published=True
    )
    db.add(course)
    await db.flush()
    
    # Module 1: Python Basics
    module1 = Module(
        course_id=course.id,
        title="Getting Started with Python",
        content_body="Introduction to Python and basic concepts",
        sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
    )
    db.add(module1)
    await db.flush()
    
    # Lessons for Module 1
    lessons = [
        Lesson(
            module_id=module1.id,
            title="Introduction to Python",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/python-intro.mp4",
            content_body="What is Python and why learn it?",
            estimated_minutes=15,
            sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True,
            skill_tags=["python-basics"],
            learning_objectives=["Understand what Python is", "Learn Python's use cases"],
            is_published=True
        ),
        Lesson(
            module_id=module1.id,
            title="Variables and Data Types",
            content_type=ContentType.ARTICLE,
            content_body="Understanding variables, strings, numbers, and booleans",
            estimated_minutes=20,
            sequence_order=2,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True,
            skill_tags=["variables", "data-types"],
            learning_objectives=["Declare variables", "Use different data types"],
            is_published=True
        ),
        Lesson(
            module_id=module1.id,
            title="Python Operators",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/operators.mp4",
            content_body="Arithmetic, comparison, and logical operators",
            estimated_minutes=25,
            sequence_order=3,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True,
            skill_tags=["operators", "expressions"],
            learning_objectives=["Use arithmetic operators", "Apply logical operators"],
            is_published=True
        )
    ]
    
    for lesson in lessons:
        db.add(lesson)
    
    # Module 2: Control Flow
    module2 = Module(
        course_id=course.id,
        title="Control Flow & Functions",
        content_body="Learn if statements, loops, and functions",
        sequence_order=2,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
    )
    db.add(module2)
    await db.flush()
    
    # Lessons for Module 2
    lessons2 = [
        Lesson(
            module_id=module2.id,
            title="If Statements & Conditionals",
            content_type=ContentType.ARTICLE,
            content_body="Making decisions in your code",
            estimated_minutes=30,
            sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True,
            skill_tags=["conditionals", "control-flow"],
            learning_objectives=["Write if/elif/else statements", "Use boolean logic"],
            is_published=True
        ),
        Lesson(
            module_id=module2.id,
            title="Loops: For and While",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/loops.mp4",
            content_body="Repeating actions with loops",
            estimated_minutes=35,
            sequence_order=2,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True,
            skill_tags=["loops", "iteration"],
            learning_objectives=["Write for loops", "Write while loops", "Use break/continue"],
            is_published=True
        ),
        Lesson(
            module_id=module2.id,
            title="Functions in Python",
            content_type=ContentType.ARTICLE,
            content_body="Creating reusable code with functions",
            estimated_minutes=40,
            sequence_order=3,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True,
            skill_tags=["functions", "code-reuse"],
            learning_objectives=["Define functions", "Use parameters and return values"],
            is_published=True
        )
    ]
    
    for lesson in lessons2:
        db.add(lesson)
    
    # Create assessment
    assessment = Assessment(
        title="Python Fundamentals Quiz",
        content_body="Test your knowledge of Python basics",
        is_diagnostic=True,
        skills_assessed=["Python", "Programming Basics"],
        time_limit_minutes=30,
        passing_score=70
    )
    db.add(assessment)
    await db.flush()
    
    # Assessment questions
    questions = [
        AssessmentQuestion(
            assessment_id=assessment.id,
            question_text="What is the correct way to declare a variable in Python?",
            question_type="multiple_choice",
            options=["var x = 5", "x = 5", "int x = 5", "declare x = 5"],
            correct_answer="x = 5",
            explanation="Python uses dynamic typing, so you just assign a value",
            difficulty_level=2,
            points=10,
            skill_tags=["Python", "Variables"],
            sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        AssessmentQuestion(
            assessment_id=assessment.id,
            question_text="Which data type would you use to store text in Python?",
            question_type="multiple_choice",
            options=["int", "str", "text", "char"],
            correct_answer="str",
            explanation="Strings (str) are used for text in Python",
            difficulty_level=1,
            points=10,
            skill_tags=["Python", "Data Types"],
            sequence_order=2,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        AssessmentQuestion(
            assessment_id=assessment.id,
            question_text="What does the 'def' keyword do in Python?",
            question_type="multiple_choice",
            options=["Defines a variable", "Defines a function", "Defines a class", "Deletes a function"],
            correct_answer="Defines a function",
            explanation="'def' is used to define functions in Python",
            difficulty_level=3,
            points=10,
            skill_tags=["Python", "Functions"],
            sequence_order=3,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        )
    ]
    
    for q in questions:
        db.add(q)
    
    await db.commit()
    print(f"✅ Created: {course.title} with {len(lessons) + len(lessons2)} lessons")
    return course.id


async def create_fastapi_course(db: AsyncSession, instructor_id: uuid.UUID):
    """Create FastAPI Web Development course"""
    print("\n📚 Creating FastAPI Web Development Course...")
    
    course = Course(
        title="FastAPI Web Development",
        content_body="Build modern REST APIs with FastAPI and async Python",
        short_content_body="Master FastAPI framework for building APIs",
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        estimated_duration_hours=30,
        skills_taught=["FastAPI", "REST APIs", "Python", "Async Programming"],
        prerequisites=["Python"],
        created_by=instructor_id,
        is_published=True
    )
    db.add(course)
    await db.flush()
    
    # Module 1
    module = Module(
        course_id=course.id,
        title="FastAPI Basics",
        content_body="Introduction to FastAPI framework",
        sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
    )
    db.add(module)
    await db.flush()
    
    lessons = [
        Lesson(
            module_id=module.id,
            title="What is FastAPI?",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/fastapi-intro.mp4",
            content_body="Introduction to FastAPI and its advantages",
            estimated_minutes=20,
            sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Your First FastAPI App",
            content_type=ContentType.ARTICLE,
            content_body="Creating a simple Hello World API",
            estimated_minutes=30,
            sequence_order=2,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Path Parameters and Query Params",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/fastapi-params.mp4",
            content_body="Handling URL parameters in FastAPI",
            estimated_minutes=35,
            sequence_order=3,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Request Body and Pydantic Models",
            content_type=ContentType.ARTICLE,
            content_body="Using Pydantic for data validation",
            estimated_minutes=40,
            sequence_order=4,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        )
    ]
    
    for lesson in lessons:
        db.add(lesson)
    
    # Assessment
    assessment = Assessment(
        title="FastAPI Fundamentals Quiz",
        content_body="Test your FastAPI knowledge",
        is_diagnostic=False,
        skills_assessed=["FastAPI", "REST APIs"],
        time_limit_minutes=25,
        passing_score=75
    )
    db.add(assessment)
    await db.flush()
    
    questions = [
        AssessmentQuestion(
            assessment_id=assessment.id,
            question_text="What decorator is used to create a GET endpoint in FastAPI?",
            question_type="multiple_choice",
            options=["@app.get()", "@get()", "@router.get()", "@endpoint.get()"],
            correct_answer="@app.get()",
            explanation="@app.get() is the standard decorator for GET routes",
            difficulty_level=2,
            points=10,
            skill_tags=["FastAPI"],
            sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        AssessmentQuestion(
            assessment_id=assessment.id,
            question_text="Which library does FastAPI use for data validation?",
            question_type="multiple_choice",
            options=["Marshmallow", "Pydantic", "Cerberus", "Voluptuous"],
            correct_answer="Pydantic",
            explanation="FastAPI uses Pydantic for automatic data validation",
            difficulty_level=3,
            points=10,
            skill_tags=["FastAPI", "Pydantic"],
            sequence_order=2,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        )
    ]
    
    for q in questions:
        db.add(q)
    
    await db.commit()
    print(f"✅ Created: {course.title} with {len(lessons)} lessons")
    return course.id


async def create_database_course(db: AsyncSession, instructor_id: uuid.UUID):
    """Create PostgreSQL & Databases course"""
    print("\n📚 Creating PostgreSQL & Databases Course...")
    
    course = Course(
        title="PostgreSQL & Database Design",
        content_body="Learn SQL, database design, and PostgreSQL administration",
        short_content_body="Master relational databases with PostgreSQL",
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        estimated_duration_hours=25,
        skills_taught=["PostgreSQL", "SQL", "Database Design"],
        prerequisites=["Programming Basics"],
        created_by=instructor_id,
        is_published=True
    )
    db.add(course)
    await db.flush()
    
    module = Module(
        course_id=course.id,
        title="SQL Fundamentals",
        content_body="Learn SQL query language",
        sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
    )
    db.add(module)
    await db.flush()
    
    lessons = [
        Lesson(
            module_id=module.id,
            title="Introduction to Databases",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/db-intro.mp4",
            content_body="What are databases and why use them?",
            estimated_minutes=25,
            sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="SELECT Queries",
            content_type=ContentType.ARTICLE,
            content_body="Querying data with SELECT statements",
            estimated_minutes=30,
            sequence_order=2,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Joins and Relationships",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/joins.mp4",
            content_body="Combining data from multiple tables",
            estimated_minutes=45,
            sequence_order=3,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        )
    ]
    
    for lesson in lessons:
        db.add(lesson)
    
    await db.commit()
    print(f"✅ Created: {course.title} with {len(lessons)} lessons")
    return course.id


async def create_advanced_python_course(db: AsyncSession, instructor_id: uuid.UUID):
    """Create Advanced Python course"""
    print("\n📚 Creating Advanced Python Course...")
    
    course = Course(
        title="Advanced Python Programming",
        content_body="Deep dive into decorators, generators, async/await, and more",
        short_content_body="Advanced Python concepts and patterns",
        difficulty_level=DifficultyLevel.ADVANCED,
        estimated_duration_hours=35,
        skills_taught=["Python", "Async Programming", "Design Patterns"],
        prerequisites=["Python", "Programming Basics"],
        created_by=instructor_id,
        is_published=True
    )
    db.add(course)
    await db.flush()
    
    module = Module(
        course_id=course.id,
        title="Advanced Python Concepts",
        content_body="Decorators, generators, and context managers",
        sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
    )
    db.add(module)
    await db.flush()
    
    lessons = [
        Lesson(
            module_id=module.id,
            title="Python Decorators",
            content_type=ContentType.ARTICLE,
            content_body="Understanding and creating decorators",
            estimated_minutes=50,
            sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Generators and Iterators",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/generators.mp4",
            content_body="Lazy evaluation with generators",
            estimated_minutes=45,
            sequence_order=2,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Async/Await in Python",
            content_type=ContentType.ARTICLE,
            content_body="Asynchronous programming with asyncio",
            estimated_minutes=60,
            sequence_order=3,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        )
    ]
    
    for lesson in lessons:
        db.add(lesson)
    
    await db.commit()
    print(f"✅ Created: {course.title} with {len(lessons)} lessons")
    return course.id


async def create_data_science_course(db: AsyncSession, instructor_id: uuid.UUID):
    """Create Data Science with Python course"""
    print("\n📚 Creating Data Science Course...")
    
    course = Course(
        title="Data Science with Python",
        content_body="Learn data analysis, visualization, and machine learning basics",
        short_content_body="Introduction to data science and ML",
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        estimated_duration_hours=40,
        skills_taught=["Python", "Data Analysis", "Machine Learning", "Pandas"],
        prerequisites=["Python"],
        created_by=instructor_id,
        is_published=True
    )
    db.add(course)
    await db.flush()
    
    module = Module(
        course_id=course.id,
        title="Data Analysis Basics",
        content_body="Working with data using Pandas",
        sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
    )
    db.add(module)
    await db.flush()
    
    lessons = [
        Lesson(
            module_id=module.id,
            title="Introduction to NumPy",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/numpy.mp4",
            content_body="Arrays and numerical computing",
            estimated_minutes=35,
            sequence_order=1,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Pandas DataFrames",
            content_type=ContentType.ARTICLE,
            content_body="Working with tabular data",
            estimated_minutes=40,
            sequence_order=2,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        ),
        Lesson(
            module_id=module.id,
            title="Data Visualization",
            content_type=ContentType.VIDEO,
            content_url="https://example.com/viz.mp4",
            content_body="Creating charts with Matplotlib and Seaborn",
            estimated_minutes=45,
            sequence_order=3,`n            skill_tags=[],`n            learning_objectives=[],`n            is_published=True
        )
    ]
    
    for lesson in lessons:
        db.add(lesson)
    
    await db.commit()
    print(f"✅ Created: {course.title} with {len(lessons)} lessons")
    return course.id


async def create_sample_progress(db: AsyncSession, user_id: uuid.UUID, course_ids: list):
    """Create sample learning progress for the test user"""
    print("\n📊 Creating sample learning progress...")
    
    # Enroll in Python Fundamentals and complete some lessons
    if len(course_ids) > 0:
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_ids[0],  # Python Fundamentals
            progress_percentage=60
        )
        db.add(enrollment)
        await db.flush()
        
        # Get lessons from first course
        result = await db.execute(
            select(Lesson)
            .join(Module)
            .where(Module.course_id == course_ids[0])
            .limit(3)
        )
        lessons = result.scalars().all()
        
        # Mark first 2 lessons as completed
        for i, lesson in enumerate(lessons[:2]):
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson.id,
                status=ProgressStatus.COMPLETED,
                time_spent_seconds=lesson.estimated_duration_minutes * 60,
                completion_percentage=100
            )
            db.add(progress)
        
        # Mark 3rd lesson as in progress
        if len(lessons) > 2:
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lessons[2].id,
                status=ProgressStatus.IN_PROGRESS,
                time_spent_seconds=300,
                completion_percentage=40
            )
            db.add(progress)
    
    await db.commit()
    print("✅ Sample progress created")


async def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # Optional: Clear existing data (comment out if you want to keep existing data)
            # await clear_existing_data(db)
            
            # Get or create instructor user
            result = await db.execute(
                select(User).where(User.email == "ai_test@example.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ Test user not found. Please run test_ai_features.py first to create a user.")
                sys.exit(1)
            
            instructor_id = user.id
            
            # Create courses
            course_ids = []
            course_ids.append(await create_python_fundamentals_course(db, instructor_id))
            course_ids.append(await create_fastapi_course(db, instructor_id))
            course_ids.append(await create_database_course(db, instructor_id))
            course_ids.append(await create_advanced_python_course(db, instructor_id))
            course_ids.append(await create_data_science_course(db, instructor_id))
            
            # Create sample progress for test user
            await create_sample_progress(db, user.id, course_ids)
            
            print("\n" + "="*60)
            print("🎉 Database seeding completed successfully!")
            print("="*60)
            print(f"\n📚 Created {len(course_ids)} courses")
            print("📝 Created lessons, modules, and assessments")
            print("📊 Created sample learning progress")
            print("\n💡 Next steps:")
            print("   1. Run: python test_ai_features.py")
            print("   2. Open: http://127.0.0.1:8000/docs")
            print("   3. Test AI recommendations with real data!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(main())
