"""
Check LearnerProfile model structure
"""
from app.models.learner_profile import LearnerProfile

print("LearnerProfile columns:")
for col in LearnerProfile.__table__.columns:
    print(f"  - {col.name}: {col.type}")

print("\nExpected column names:")
expected = [
    "id", "user_id", "learning_style", "preferred_pace", 
    "study_hours_per_week", "skill_levels", "knowledge_gaps",
    "avg_session_duration_mins", "preferred_study_times",
    "completion_rate_30d", "avg_quiz_score_30d", 
    "created_at", "updated_at"
]

actual = [col.name for col in LearnerProfile.__table__.columns]

print("\nMissing columns:")
for col in expected:
    if col not in actual:
        print(f"  ❌ {col}")

print("\nExtra columns:")
for col in actual:
    if col not in expected:
        print(f"  ⚠️  {col}")

if set(expected) == set(actual):
    print("\n✅ All columns match!")
else:
    print("\n❌ Column mismatch detected")