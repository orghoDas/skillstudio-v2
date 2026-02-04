from fastapi import APIRouter
from app.api import auth, courses, learning, profile, assessments, dashboard

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(learning.router, prefix="/learning", tags=["Learning"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(dashboard.router, prefix="/ai", tags=["AI Dashboard"])

__all__ = ["api_router"]