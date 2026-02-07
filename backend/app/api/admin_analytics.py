"""
Admin Analytics API Routes
Platform-wide analytics and reporting for administrators
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from datetime import date

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.admin_analytics import AdminAnalyticsService


router = APIRouter(prefix="/api/admin/analytics", tags=["Admin Analytics"])


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/overview")
async def get_platform_overview(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get high-level platform statistics
    """
    analytics_service = AdminAnalyticsService()
    overview = await analytics_service.get_platform_overview(db)
    
    return overview


@router.get("/user-growth")
async def get_user_growth(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user growth metrics
    """
    analytics_service = AdminAnalyticsService()
    growth = await analytics_service.get_user_growth(db, days)
    
    return growth


@router.get("/engagement")
async def get_engagement_metrics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get platform engagement metrics (DAU, MAU, WAU, etc.)
    """
    analytics_service = AdminAnalyticsService()
    engagement = await analytics_service.get_engagement_metrics(db, days)
    
    return engagement


@router.get("/revenue")
async def get_revenue_metrics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get revenue metrics and trends
    """
    analytics_service = AdminAnalyticsService()
    revenue = await analytics_service.get_revenue_metrics(db, days)
    
    return revenue


@router.get("/top-courses")
async def get_top_courses(
    metric: str = Query("enrollments", regex="^(enrollments|revenue|rating)$"),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get top performing courses
    """
    analytics_service = AdminAnalyticsService()
    top_courses = await analytics_service.get_top_courses(db, limit, metric)
    
    return top_courses


@router.get("/top-instructors")
async def get_top_instructors(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get top performing instructors
    """
    analytics_service = AdminAnalyticsService()
    top_instructors = await analytics_service.get_top_instructors(db, limit)
    
    return top_instructors


@router.get("/system-health")
async def get_system_health(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get system health metrics
    """
    analytics_service = AdminAnalyticsService()
    health = await analytics_service.get_system_health(db)
    
    return health


@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive admin dashboard data (all metrics in one call)
    """
    analytics_service = AdminAnalyticsService()
    
    # Fetch all metrics in parallel
    overview = await analytics_service.get_platform_overview(db)
    growth = await analytics_service.get_user_growth(db, 30)
    engagement = await analytics_service.get_engagement_metrics(db, 30)
    revenue = await analytics_service.get_revenue_metrics(db, 30)
    top_courses = await analytics_service.get_top_courses(db, 5, "enrollments")
    top_instructors = await analytics_service.get_top_instructors(db, 5)
    health = await analytics_service.get_system_health(db)
    
    return {
        "overview": overview,
        "user_growth": growth,
        "engagement": engagement,
        "revenue": revenue,
        "top_courses": top_courses,
        "top_instructors": top_instructors,
        "system_health": health
    }


@router.post("/aggregate/{target_date}")
async def aggregate_daily_metrics(
    target_date: date,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Manually trigger daily metrics aggregation for a specific date
    (Normally run as cron job)
    """
    analytics_service = AdminAnalyticsService()
    await analytics_service.aggregate_daily_metrics(db, target_date)
    
    return {
        "message": f"Metrics aggregated for {target_date}"
    }
