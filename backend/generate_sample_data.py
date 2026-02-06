"""
Generate comprehensive sample data for AI demo
Creates users, courses, progress, and assessments
"""
import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.learner_profile import LearnerProfile
from app.models.course import Course, Module, Lesson, DifficultyLevel, ContentType
from app.models.learning import LearningGoal, Enrollment, LessonProgress, ProgressStatus
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentAttempt
from sqlalchemy import select


async def create_sample_users(db):
    """Create diverse sample users with profiles"""
    print("👥 Creating sample users...")
    
    users_data = [
        {
            "email": "sarah.developer@demo.com",
            "name": "Sarah Chen",
            "password": "demo1234",
            "skills": {"python": 4, "javascript": 6, "react": 5, "sql": 3},
            "gaps": ["fastapi", "async-programming", "docker"],
            "style": "visual",
            "pace": "fast",
            "hours_per_week": 20
        },
        {
            "email": "michael.student@demo.com",
            "name": "Michael Rodriguez",
            "password": "demo1234",
            "skills": {"python": 2, "git": 3},
            "gaps": ["web-development", "databases", "testing"],
            "style": "hands-on",
            "pace": "medium",
            "hours_per_week": 10
        },
        {
            "email": "emily.analyst@demo.com",
            "name": "Emily Watson",
            "password": "demo1234",
            "skills": {"python": 7, "pandas": 6, "sql": 8, "excel": 9},
            "gaps": ["machine-learning", "data-visualization", "big-data"],
            "style": "reading",
            "pace": "medium",
            "hours_per_week": 15
        },
        {
            "email": "david.beginner@demo.com",
            "name": "David Kim",
            "password": "demo1234",
            "skills": {},
            "gaps": ["programming-basics", "python", "web-development"],
            "style": "visual",
            "pace": "slow",
            "hours_per_week": 8
        },
        {
            "email": "lisa.engineer@demo.com",
            "name": "Lisa Johnson",
            "password": "demo1234",
            "skills": {"python": 8, "django": 7, "postgresql": 6, "docker": 5, "aws": 4},
            "gaps": ["kubernetes", "microservices", "fastapi"],
            "style": "hands-on",
            "pace": "fast",
            "hours_per_week": 25
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == user_data["email"])
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"  ⏭️  Skipping {user_data['email']} (already exists)")
            created_users.append(existing_user)
            continue
        
        # Create user
        user = User(
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            full_name=user_data["name"],
            role=UserRole.LEARNER
        )
        db.add(user)
        await db.flush()
        
        # Create profile
        profile = LearnerProfile(
            user_id=user.id,
            learning_style=user_data["style"],
            preferred_pace=user_data["pace"],
            study_hours_per_week=user_data["hours_per_week"],
            skill_levels=user_data["skills"],
            knowledge_gaps=user_data["gaps"]
        )
        db.add(profile)
        created_users.append(user)
    
    await db.commit()
    print(f"✅ Created {len(created_users)} sample users")
    return created_users


async def create_additional_courses(db, instructor_id):
    """Create diverse courses across multiple domains"""
    print("📚 Creating additional courses...")
    
    courses_data = [
        {
            "title": "Docker & Containerization",
            "description": "Master Docker containers, images, and orchestration basics",
            "short_description": "Learn Docker from basics to deployment",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "hours": 12,
            "skills": ["docker", "containers", "devops", "deployment"],
            "prerequisites": ["python", "linux-basics"],
            "modules": [
                {
                    "title": "Docker Fundamentals",
                    "lessons": [
                        {"title": "What is Docker?", "type": ContentType.VIDEO, "minutes": 15},
                        {"title": "Docker Images & Containers", "type": ContentType.ARTICLE, "minutes": 20},
                        {"title": "Dockerfile Basics", "type": ContentType.CODE_EXERCISE, "minutes": 30}
                    ]
                },
                {
                    "title": "Docker Compose",
                    "lessons": [
                        {"title": "Multi-Container Apps", "type": ContentType.VIDEO, "minutes": 25},
                        {"title": "Docker Compose Files", "type": ContentType.ARTICLE, "minutes": 20}
                    ]
                }
            ]
        },
        {
            "title": "Machine Learning Fundamentals",
            "description": "Introduction to ML algorithms, model training, and evaluation",
            "short_description": "Start your ML journey with scikit-learn",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "hours": 35,
            "skills": ["machine-learning", "scikit-learn", "model-training", "algorithms"],
            "prerequisites": ["python", "numpy", "pandas"],
            "modules": [
                {
                    "title": "ML Basics",
                    "lessons": [
                        {"title": "What is Machine Learning?", "type": ContentType.VIDEO, "minutes": 20},
                        {"title": "Supervised vs Unsupervised", "type": ContentType.ARTICLE, "minutes": 25},
                        {"title": "Train-Test Split", "type": ContentType.CODE_EXERCISE, "minutes": 30}
                    ]
                },
                {
                    "title": "Classification Algorithms",
                    "lessons": [
                        {"title": "Logistic Regression", "type": ContentType.VIDEO, "minutes": 35},
                        {"title": "Decision Trees", "type": ContentType.ARTICLE, "minutes": 30},
                        {"title": "Random Forests", "type": ContentType.CODE_EXERCISE, "minutes": 40}
                    ]
                }
            ]
        },
        {
            "title": "React for Beginners",
            "description": "Build modern web apps with React, hooks, and component architecture",
            "short_description": "Master React fundamentals",
            "difficulty": DifficultyLevel.BEGINNER,
            "hours": 22,
            "skills": ["react", "jsx", "components", "hooks", "frontend"],
            "prerequisites": ["javascript", "html", "css"],
            "modules": [
                {
                    "title": "React Basics",
                    "lessons": [
                        {"title": "Introduction to React", "type": ContentType.VIDEO, "minutes": 18},
                        {"title": "JSX Syntax", "type": ContentType.ARTICLE, "minutes": 22},
                        {"title": "Your First Component", "type": ContentType.CODE_EXERCISE, "minutes": 35}
                    ]
                },
                {
                    "title": "React Hooks",
                    "lessons": [
                        {"title": "useState Hook", "type": ContentType.VIDEO, "minutes": 28},
                        {"title": "useEffect Hook", "type": ContentType.ARTICLE, "minutes": 25},
                        {"title": "Custom Hooks", "type": ContentType.CODE_EXERCISE, "minutes": 40}
                    ]
                }
            ]
        },
        {
            "title": "Git & Version Control",
            "description": "Master Git workflows, branching strategies, and collaboration",
            "short_description": "Essential Git for developers",
            "difficulty": DifficultyLevel.BEGINNER,
            "hours": 10,
            "skills": ["git", "version-control", "github", "collaboration"],
            "prerequisites": [],
            "modules": [
                {
                    "title": "Git Basics",
                    "lessons": [
                        {"title": "What is Version Control?", "type": ContentType.VIDEO, "minutes": 15},
                        {"title": "Git Setup & Config", "type": ContentType.ARTICLE, "minutes": 18},
                        {"title": "First Commits", "type": ContentType.CODE_EXERCISE, "minutes": 25}
                    ]
                },
                {
                    "title": "Branching & Merging",
                    "lessons": [
                        {"title": "Git Branches", "type": ContentType.VIDEO, "minutes": 22},
                        {"title": "Merge Strategies", "type": ContentType.ARTICLE, "minutes": 20},
                        {"title": "Resolving Conflicts", "type": ContentType.CODE_EXERCISE, "minutes": 30}
                    ]
                }
            ]
        },
        {
            "title": "AWS Cloud Essentials",
            "description": "Learn AWS fundamentals: EC2, S3, RDS, and cloud architecture",
            "short_description": "Get started with AWS cloud",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "hours": 28,
            "skills": ["aws", "cloud", "ec2", "s3", "devops"],
            "prerequisites": ["linux-basics", "networking"],
            "modules": [
                {
                    "title": "AWS Fundamentals",
                    "lessons": [
                        {"title": "Cloud Computing Basics", "type": ContentType.VIDEO, "minutes": 20},
                        {"title": "AWS Account Setup", "type": ContentType.ARTICLE, "minutes": 15},
                        {"title": "EC2 Instances", "type": ContentType.CODE_EXERCISE, "minutes": 35}
                    ]
                },
                {
                    "title": "Storage & Databases",
                    "lessons": [
                        {"title": "S3 Object Storage", "type": ContentType.VIDEO, "minutes": 25},
                        {"title": "RDS Databases", "type": ContentType.ARTICLE, "minutes": 30}
                    ]
                }
            ]
        },
        {
            "title": "RESTful API Design",
            "description": "Design scalable, maintainable REST APIs with best practices",
            "short_description": "Build better APIs",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "hours": 16,
            "skills": ["rest-api", "api-design", "http", "web-services"],
            "prerequisites": ["python", "web-development"],
            "modules": [
                {
                    "title": "REST Principles",
                    "lessons": [
                        {"title": "What is REST?", "type": ContentType.VIDEO, "minutes": 18},
                        {"title": "HTTP Methods", "type": ContentType.ARTICLE, "minutes": 20},
                        {"title": "Resource Design", "type": ContentType.ARTICLE, "minutes": 25}
                    ]
                },
                {
                    "title": "API Best Practices",
                    "lessons": [
                        {"title": "Versioning", "type": ContentType.VIDEO, "minutes": 22},
                        {"title": "Error Handling", "type": ContentType.ARTICLE, "minutes": 20},
                        {"title": "Authentication", "type": ContentType.CODE_EXERCISE, "minutes": 35}
                    ]
                }
            ]
        },
        {
            "title": "Testing in Python",
            "description": "Master pytest, unit testing, integration tests, and TDD",
            "short_description": "Write better tests",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "hours": 18,
            "skills": ["testing", "pytest", "tdd", "quality-assurance"],
            "prerequisites": ["python", "functions", "classes"],
            "modules": [
                {
                    "title": "Testing Fundamentals",
                    "lessons": [
                        {"title": "Why Test?", "type": ContentType.VIDEO, "minutes": 15},
                        {"title": "Unit vs Integration", "type": ContentType.ARTICLE, "minutes": 20},
                        {"title": "First Pytest Test", "type": ContentType.CODE_EXERCISE, "minutes": 30}
                    ]
                },
                {
                    "title": "Advanced Testing",
                    "lessons": [
                        {"title": "Fixtures & Mocking", "type": ContentType.VIDEO, "minutes": 28},
                        {"title": "Test Coverage", "type": ContentType.ARTICLE, "minutes": 22},
                        {"title": "TDD Workflow", "type": ContentType.CODE_EXERCISE, "minutes": 35}
                    ]
                }
            ]
        },
        {
            "title": "JavaScript ES6+ Features",
            "description": "Modern JavaScript: arrow functions, promises, async/await, modules",
            "short_description": "Master modern JavaScript",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "hours": 14,
            "skills": ["javascript", "es6", "async", "modern-js"],
            "prerequisites": ["javascript-basics"],
            "modules": [
                {
                    "title": "ES6 Syntax",
                    "lessons": [
                        {"title": "Let, Const, Arrow Functions", "type": ContentType.VIDEO, "minutes": 20},
                        {"title": "Destructuring", "type": ContentType.ARTICLE, "minutes": 18},
                        {"title": "Template Literals", "type": ContentType.CODE_EXERCISE, "minutes": 15}
                    ]
                },
                {
                    "title": "Async JavaScript",
                    "lessons": [
                        {"title": "Promises", "type": ContentType.VIDEO, "minutes": 25},
                        {"title": "Async/Await", "type": ContentType.ARTICLE, "minutes": 22},
                        {"title": "Fetch API", "type": ContentType.CODE_EXERCISE, "minutes": 30}
                    ]
                }
            ]
        }
    ]
    
    created_courses = []
    for course_data in courses_data:
        # Create course
        course = Course(
            title=course_data["title"],
            description=course_data["description"],
            short_description=course_data["short_description"],
            difficulty_level=course_data["difficulty"],
            estimated_duration_hours=course_data["hours"],
            skills_taught=course_data["skills"],
            prerequisites=course_data["prerequisites"],
            is_published=True,
            created_by=instructor_id
        )
        db.add(course)
        await db.flush()
        
        # Create modules and lessons
        for mod_idx, module_data in enumerate(course_data["modules"], 1):
            module = Module(
                course_id=course.id,
                title=module_data["title"],
                description=f"Learn {module_data['title'].lower()}",
                sequence_order=mod_idx
            )
            db.add(module)
            await db.flush()
            
            for lesson_idx, lesson_data in enumerate(module_data["lessons"], 1):
                lesson = Lesson(
                    module_id=module.id,
                    title=lesson_data["title"],
                    content_type=lesson_data["type"],
                    content_body=f"Content for {lesson_data['title']}",
                    estimated_minutes=lesson_data["minutes"],
                    sequence_order=lesson_idx,
                    skill_tags=course_data["skills"][:2],
                    learning_objectives=[f"Understand {lesson_data['title']}"],
                    is_published=True
                )
                if lesson_data["type"] == ContentType.VIDEO:
                    lesson.content_url = f"https://example.com/video-{uuid4().hex[:8]}.mp4"
                db.add(lesson)
        
        created_courses.append(course)
    
    await db.commit()
    print(f"✅ Created {len(created_courses)} additional courses")
    return created_courses


async def generate_user_progress(db, users, all_courses):
    """Generate realistic learning progress for users"""
    print("📈 Generating user progress...")
    
    progress_count = 0
    
    for user in users:
        # Each user enrolls in 2-4 courses based on their interests
        num_enrollments = random.randint(2, 4)
        enrolled_courses = random.sample(all_courses, min(num_enrollments, len(all_courses)))
        
        for course in enrolled_courses:
            # Create enrollment
            enrollment = Enrollment(
                user_id=user.id,
                course_id=course.id,
                enrolled_at=datetime.now() - timedelta(days=random.randint(1, 60))
            )
            db.add(enrollment)
            await db.flush()
            
            # Get all lessons in this course
            result = await db.execute(
                select(Lesson)
                .join(Module)
                .where(Module.course_id == course.id)
                .order_by(Module.sequence_order, Lesson.sequence_order)
            )
            lessons = result.scalars().all()
            
            # Complete 30-90% of lessons
            completion_rate = random.uniform(0.3, 0.9)
            lessons_to_complete = int(len(lessons) * completion_rate)
            
            for i, lesson in enumerate(lessons[:lessons_to_complete]):
                # Create lesson progress
                completed_at = enrollment.enrolled_at + timedelta(
                    days=random.randint(1, 30),
                    hours=random.randint(0, 23)
                )
                
                progress = LessonProgress(
                    user_id=user.id,
                    lesson_id=lesson.id,
                    status=ProgressStatus.COMPLETED,
                    time_spent_seconds=random.randint(
                        int(lesson.estimated_minutes * 0.8 * 60),
                        int(lesson.estimated_minutes * 1.5 * 60)
                    ),
                    completed_at=completed_at
                )
                db.add(progress)
                progress_count += 1
    
    await db.commit()
    print(f"✅ Generated {progress_count} lesson progress records")


async def create_assessments_and_attempts(db, all_courses, users):
    """Create assessments with questions and user attempts"""
    print("📝 Creating assessments and attempts...")
    
    assessment_count = 0
    attempt_count = 0
    
    # Create diagnostic assessments (not course-specific)
    for i in range(3):
        assessment = Assessment(
            title=f"Diagnostic Assessment {i+1}",
            description="Test your current skill level",
            is_diagnostic=True,
            skills_assessed=["python", "javascript", "web-development"][:i+1],
            passing_score=60,
            time_limit_minutes=45
        )
        db.add(assessment)
        await db.flush()
        assessment_count += 1
        
        # Create 8-12 questions
        for q_idx in range(random.randint(8, 12)):
            question = AssessmentQuestion(
                assessment_id=assessment.id,
                question_text=f"Question {q_idx + 1} about {'Python' if i == 0 else 'JavaScript' if i == 1 else 'Web Development'}",
                question_type="multiple_choice",
                options=["Option A", "Option B", "Option C", "Option D"],
                correct_answer="Option A",
                points=10,
                sequence_order=q_idx + 1
            )
            db.add(question)
        
        await db.flush()
        
        # Some users attempt diagnostic assessments
        for user in users[:3]:  # First 3 users
            if random.random() < 0.7:  # 70% attempt rate
                score = random.uniform(55, 90)
                points_possible = 90
                points_earned = int((score / 100) * points_possible)
                passed = score >= 60  # Passing score is 60
                
                attempt = AssessmentAttempt(
                    assessment_id=assessment.id,
                    user_id=user.id,
                    score_percecntage=round(score, 2),
                    points_earned=points_earned,
                    points_possible=points_possible,
                    time_taken_seconds=random.randint(20, 45) * 60,  # Convert minutes to seconds
                    answers={},  # simplified - empty dict for sample data
                    attempt_number=1,  # First attempt
                    passed=passed
                )
                db.add(attempt)
                attempt_count += 1
    
    await db.commit()
    print(f"✅ Created {assessment_count} assessments with {attempt_count} user attempts")


async def create_learning_goals(db, users):
    """Create learning goals for users"""
    print("🎯 Creating learning goals...")
    
    goals_data = [
        ("Become a Full Stack Developer", "Full Stack Engineer", ["python", "fastapi", "react", "postgresql", "docker"]),
        ("Master Data Science", "Data Scientist", ["python", "machine-learning", "pandas", "data-visualization"]),
        ("Learn Cloud Engineering", "Cloud Engineer", ["aws", "docker", "kubernetes", "devops"]),
        ("Frontend Development Expert", "Frontend Developer", ["react", "javascript", "css", "web-development"]),
    ]
    
    goal_count = 0
    for user in users:
        # Each user gets 1-2 goals
        num_goals = random.randint(1, 2)
        selected_goals = random.sample(goals_data, min(num_goals, len(goals_data)))
        
        for goal_desc, role, skills in selected_goals:
            goal = LearningGoal(
                user_id=user.id,
                goal_description=goal_desc,
                target_role=role,
                target_skills=skills,
                target_completion_date=(datetime.now() + timedelta(days=random.randint(60, 180))).date()
            )
            db.add(goal)
            goal_count += 1
    
    await db.commit()
    print(f"✅ Created {goal_count} learning goals")


async def main():
    """Main data generation function"""
    print("🌱 Starting comprehensive data generation...\n")
    
    async with AsyncSessionLocal() as db:
        # Get demo user as instructor
        result = await db.execute(
            select(User).where(User.email == "demo@learningplatform.com")
        )
        instructor = result.scalar_one_or_none()
        
        if not instructor:
            print("❌ Demo user not found. Run create_test_user.py first")
            return
        
        # Create sample users
        users = await create_sample_users(db)
        
        # Get all existing courses
        result = await db.execute(select(Course))
        existing_courses = result.scalars().all()
        print(f"ℹ️  Found {len(existing_courses)} existing courses")
        
        # Create additional courses
        new_courses = await create_additional_courses(db, instructor.id)
        
        # Combine all courses
        all_courses = existing_courses + new_courses
        print(f"ℹ️  Total courses: {len(all_courses)}")
        
        # Generate user progress
        await generate_user_progress(db, users, all_courses)
        
        # Create assessments and attempts
        await create_assessments_and_attempts(db, all_courses, users)
        
        # Create learning goals
        await create_learning_goals(db, users)
        
        print("\n🎉 Data generation complete!")
        print(f"\n📊 Summary:")
        print(f"   • {len(users)} sample users")
        print(f"   • {len(all_courses)} total courses")
        print(f"   • Realistic progress & quiz data")
        print(f"   • Learning goals assigned")
        print(f"\n🔐 Login credentials (all use password: demo1234):")
        for user in users:
            print(f"   • {user.email}")


if __name__ == "__main__":
    asyncio.run(main())
