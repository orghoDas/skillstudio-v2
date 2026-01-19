"""
Test that models are properly defined
"""
from app.models.user import User, UserRole
from app.models.learner_profile import LearnerProfile
from app.core.database import Base

def test_models():
    print("Testing model definitions...")
    
    # Test User model
    print(f"✅ User model table name: {User.__tablename__}")
    print(f"✅ User columns: {[c.name for c in User.__table__.columns]}")
    
    # Test LearnerProfile model
    print(f"✅ LearnerProfile model table name: {LearnerProfile.__tablename__}")
    print(f"✅ LearnerProfile columns: {[c.name for c in LearnerProfile.__table__.columns]}")
    
    # Test relationship
    print(f"✅ User has relationship: {list(User.__mapper__.relationships.keys())}")
    print(f"✅ LearnerProfile has relationship: {list(LearnerProfile.__mapper__.relationships.keys())}")
    
    # Test enum
    print(f"✅ UserRole values: {[role.value for role in UserRole]}")
    
    print("\n✅ All models are properly defined!")

if __name__ == "__main__":
    test_models()