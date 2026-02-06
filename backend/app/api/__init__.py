from fastapi import APIRouter
from app.api import auth, courses, learning, profile, assessments, dashboard, ai, instructor, social, monetization

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(learning.router, prefix="/learning", tags=["Learning"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(ai.router, tags=["AI Features"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["AI Dashboard"])
api_router.include_router(instructor.router, prefix="/instructor", tags=["Instructor"])
api_router.include_router(social.router, tags=["Social Features"])
api_router.include_router(monetization.router, tags=["Monetization"])

__all__ = ["api_router"]