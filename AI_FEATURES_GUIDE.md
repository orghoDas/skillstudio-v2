# AI Features Quick Start Guide

## Overview
This guide shows how to use the AI-powered features in SkillStudio V2.

---

## 🎯 1. Diagnostic Assessment & Skill Profiling

### Flow
1. User takes diagnostic assessment
2. System analyzes answers
3. Calculates skill levels (1-10 scale)
4. Updates learner profile
5. Identifies knowledge gaps

### Code Example

```python
from app.services.skill_assessment import SkillAssessor

# In your assessment submission endpoint
assessor = SkillAssessor(db)

# Process diagnostic assessment
answers = {
    "question_uuid_1": "option_a",
    "question_uuid_2": ["option_b", "option_c"],  # Multiple choice
    "question_uuid_3": True,  # True/false
}

skill_levels, knowledge_gaps = await assessor.process_diagnostic_assessment(
    user_id=current_user.id,
    assessment_id=assessment.id,
    answers=answers
)

# Returns:
# skill_levels = {"python": 7.5, "sql": 4.0, "javascript": 6.2}
# knowledge_gaps = ["sql", "async_programming"]
```

---

## 🛤️ 2. Generate Learning Path

### Flow
1. User creates a learning goal
2. System analyzes current skills vs target skills
3. Identifies skill gaps
4. Finds courses that fill gaps
5. Orders by difficulty and prerequisites
6. Generates timeline based on study pace

### Code Example

```python
from app.services.recommendation_engine import RecommendationEngine

recommender = RecommendationEngine(db)

learning_path, metadata = await recommender.generate_learning_path(
    user_id=current_user.id,
    goal_id=goal.id
)

# Returns:
# learning_path = [
#   {
#     "type": "course",
#     "id": "uuid",
#     "title": "Python Backend Development",
#     "skills_covered": ["python", "flask"],
#     "estimated_hours": 20,
#     "reason": "Builds foundation in python, flask",
#     "sequence": 1
#   },
#   ...
# ]
# 
# metadata = {
#   "total_hours": 60,
#   "estimated_weeks": 6,
#   "skills_covered": ["python", "flask", "postgresql"]
# }
```

---

## 📚 3. Recommend Next Lesson

### Flow
1. User is enrolled in a course
2. System checks completed lessons
3. Finds next uncompleted lesson
4. Verifies prerequisites are met
5. Returns recommendation

### Code Example

```python
next_lesson = await recommender.recommend_next_lesson(
    user_id=current_user.id,
    enrollment_id=enrollment.id
)

# Returns:
# {
#   "lesson_id": "uuid",
#   "title": "Python Functions",
#   "module_title": "Module 2: Advanced Python",
#   "content_type": "video",
#   "estimated_minutes": 30,
#   "reason": "Next in sequence: Module 2",
#   "difficulty_score": 5
# }
```

---

## 🔄 4. Revision Recommendations

### Flow
1. System analyzes recent quiz performance
2. Identifies skills with <70% score
3. Finds lessons covering those skills
4. Returns revision recommendations

### Code Example

```python
revision_lessons = await recommender.recommend_revision_content(
    user_id=current_user.id,
    limit=5
)

# Returns:
# [
#   {
#     "lesson_id": "uuid",
#     "title": "Async/Await Deep Dive",
#     "content_type": "video",
#     "estimated_minutes": 25,
#     "reason": "Review async_programming - recent quiz score: 45%",
#     "skills_to_review": ["async_programming"]
#   }
# ]
```

---

## 📊 5. Performance Analytics

### Code Example

```python
from app.services.learning_analytics import LearningAnalytics

analytics = LearningAnalytics(db)

# Get comprehensive performance summary
performance = await analytics.get_learner_performance_summary(
    user_id=current_user.id,
    days=30
)

# Returns:
# {
#   "lessons_completed": 15,
#   "avg_quiz_score": 78.5,
#   "completion_rate": 0.75,
#   "active_days": 18,
#   "total_study_hours": 23.5,
#   "current_streak": 5,
#   "performance_trend": "improving"
# }

# Get engagement patterns
engagement = await analytics.get_engagement_patterns(current_user.id)

# Returns:
# {
#   "peak_hours": [20, 21, 14],
#   "peak_days": ["monday", "wednesday"],
#   "avg_session_duration": 45.2,
#   "preferred_content_type": "video"
# }

# Identify struggling topics
struggling = await analytics.identify_struggling_topics(
    user_id=current_user.id,
    threshold=60.0
)

# Returns:
# [
#   {
#     "skill": "async_programming",
#     "avg_score": 45.0,
#     "attempts": 3,
#     "difficulty": "needs_help"
#   }
# ]
```

---

## 🚨 6. Detect Struggling Learner

### Code Example

```python
is_struggling, reasons = await recommender.detect_struggling_learner(
    user_id=current_user.id,
    lesson_id=lesson.id
)

if is_struggling:
    # Trigger intervention
    print(f"Learner struggling because: {', '.join(reasons)}")
    # Send notification, create revision recommendation, etc.

# Returns:
# is_struggling = True
# reasons = [
#   "Taking 60min vs expected 30min",
#   "High pause count: 12",
#   "Low completion despite time investment"
# ]
```

---

## 🔧 7. Weekly Path Adjustment

### Code Example

```python
adjustment_report = await analytics.weekly_path_adjustment(
    user_id=current_user.id
)

# Returns:
# {
#   "adjustments_needed": True,
#   "recommendations": [
#     {
#       "type": "add_revision",
#       "reason": "Quiz scores below 60% (current: 54%)",
#       "action": "Add revision content for weak topics",
#       "priority": "high"
#     }
#   ],
#   "pace_adjustment": {
#     "current_pace": 0.8,
#     "expected_hours_per_week": 10,
#     "actual_hours_this_week": 8.0,
#     "pace_status": "behind",
#     "timeline_change": "+1 week"
#   },
#   "performance_summary": {...}
# }
```

---

## 🌐 API Endpoints

### Get AI Dashboard
```http
GET /api/v1/ai/dashboard
Authorization: Bearer <token>
```

**Response:**
```json
{
  "performance_summary": {...},
  "current_goals": [...],
  "recommended_next_lessons": [...],
  "revision_recommendations": [...],
  "struggling_topics": [...],
  "engagement_insights": {...},
  "ai_insights": {
    "learning_pace": "on_track",
    "performance_trend": "improving",
    "personalized_message": "Great 5-day streak!",
    "strengths": ["Strong quiz performance"],
    "areas_for_improvement": ["async_programming"]
  }
}
```

### Generate Learning Path
```http
POST /api/v1/ai/generate-learning-path
Authorization: Bearer <token>
Content-Type: application/json

{
  "goal_id": "uuid"
}
```

### Get Active Recommendations
```http
GET /api/v1/ai/recommendations?limit=10
Authorization: Bearer <token>
```

### Action on Recommendation
```http
POST /api/v1/ai/recommendations/{id}/action
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "accepted"  // or "skipped", "ignored"
}
```

---

## 🧪 Testing Workflow

### 1. Setup User
```python
# Register
POST /api/v1/auth/register
{
  "email": "learner@example.com",
  "password": "SecurePass123",
  "full_name": "Test Learner",
  "role": "learner"
}

# Login
POST /api/v1/auth/login
# Save access_token
```

### 2. Create Learning Goal
```python
POST /api/v1/learning/goals
{
  "goal_description": "Become a Python backend developer",
  "target_role": "Backend Developer",
  "target_skills": ["python", "flask", "postgresql", "rest_api"]
}
# Save goal_id
```

### 3. Take Diagnostic Assessment
```python
# Get diagnostic assessment
GET /api/v1/assessments?diagnostic_only=true

# Submit answers
POST /api/v1/assessments/{id}/attempt
{
  "answers": {
    "question_id_1": "option_a",
    "question_id_2": ["option_b", "option_c"]
  }
}
```

### 4. Generate Learning Path
```python
POST /api/v1/ai/generate-learning-path
{
  "goal_id": "{goal_id_from_step_2}"
}
```

### 5. View Dashboard
```python
GET /api/v1/ai/dashboard
# See AI insights, recommendations, progress
```

### 6. Enroll in Recommended Course
```python
POST /api/v1/learning/enrollments
{
  "course_id": "{course_id_from_path}",
  "learning_goal_id": "{goal_id}"
}
```

### 7. Get Next Lesson
```python
# Dashboard will show recommended_next_lessons
# Or call directly:
GET /api/v1/ai/recommendations
```

---

## 📐 Formulas & Algorithms

### Skill Level Calculation
```python
skill_level = accuracy × avg_difficulty × confidence_factor

where:
  accuracy = correct_answers / total_questions
  avg_difficulty = sum(question_difficulties) / total_questions
  confidence_factor = min(1.0, total_questions / 5)  # Full confidence at 5+ questions
  
Final: round(skill_level, 1)  # Scale: 0.0 to 10.0
```

### Knowledge Gap Detection
```python
is_knowledge_gap = (
    skill_level < 5.0 OR
    (avg_difficulty <= 3 AND accuracy < 0.6)
)
```

### Performance Trend
```python
trend = recent_avg_score - older_avg_score

if difference >= 5.0:
    return "improving"
elif difference <= -5.0:
    return "declining"
else:
    return "stable"
```

### Struggling Learner Detection
```python
is_struggling = (
    time_spent > expected_time × 2 OR
    pauses > 10 OR
    (completion < 50% AND time_spent > expected_time)
)
```

---

## 🔍 PostgreSQL JSONB Queries

### Find Courses by Skill
```sql
-- Find courses teaching "python" or "flask"
SELECT * FROM courses
WHERE skills_taught ?| ARRAY['python', 'flask']  -- JSONB overlap operator
  AND is_published = true;
```

### Find Learners with Similar Skills
```sql
-- Find learners with similar skill profiles using JSONB
WITH target AS (
    SELECT skill_levels FROM learner_profiles WHERE user_id = :user_id
)
SELECT lp.user_id,
    (SELECT SUM((target.skill_levels->>key)::float * (lp.skill_levels->>key)::float)
     FROM jsonb_each_text(target.skill_levels)
     WHERE lp.skill_levels ? key) as similarity
FROM learner_profiles lp, target
WHERE lp.user_id != :user_id
ORDER BY similarity DESC
LIMIT 10;
```

### Aggregate Event Data
```sql
-- Daily engagement summary
SELECT 
    user_id,
    DATE(event_timestamp) as activity_date,
    COUNT(*) FILTER (WHERE event_type = 'lesson_start') as lessons_started,
    COUNT(*) FILTER (WHERE event_type = 'quiz_attempt') as quizzes_attempted,
    SUM((event_data->>'duration_seconds')::int) as total_active_seconds
FROM learner_events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY user_id, DATE(event_timestamp);
```

---

## 🎯 Best Practices

1. **Always explain recommendations**
   - Every recommendation should have a clear "reason"
   - Use natural language explanations

2. **Update profiles continuously**
   - After every assessment
   - After significant progress milestones

3. **Track recommendation effectiveness**
   - Use `user_action` field in recommendations table
   - A/B test different recommendation strategies

4. **Respect user pace**
   - Use learner_profile.study_hours_per_week
   - Don't overwhelm with too many recommendations

5. **Detect struggles early**
   - Run struggle detection after each lesson
   - Intervene before users give up

---

## 🚀 Future Enhancements

### Phase 2: ML Models
- Train collaborative filtering model
- Predict dropout risk
- Cluster learners by behavior

### Phase 3: Advanced AI
- Semantic search with pgvector
- LLM-powered explanations
- Conversational AI tutor

---

**Happy coding! 🎓**
