from fastapi import APIRouter
from app.api import auth

api_router = APIRouter()

# include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

__all__ = ["api_router"]