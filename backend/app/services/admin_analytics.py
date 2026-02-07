"""
Admin Analytics Service
Provides platform-wide analytics and metrics for admin dashboard
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, distinct
from decimal import Decimal

from app.models.user import User, UserRole
from app.models.course import Course
from app.models.learning import Enrollment
from app.models.assessment import AssessmentAttempt
from app.models.monetization import Payment, UserSubscription, InstructorEarnings
from app.models.gamification import UserStats
from app.models.video_and_analytics import (
    PlatformAnalytics,
    CourseAnalytics,
    InstructorAnalytics
)


class AdminAnalyticsService:
    """Service for admin analytics and reporting"""
    
    async def get_platform_overview(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get high-level platform statistics"""
        
        # Total users by role
        total_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        total_users = total_users_result.scalar()
        
        learners_result = await db.execute(
            select(func.count(User.id)).where(
                and_(User.role == UserRole.LEARNER, User.is_active == True)
            )
        )
        total_learners = learners_result.scalar()
        
        instructors_result = await db.execute(
            select(func.count(User.id)).where(
                and_(User.role == UserRole.INSTRUCTOR, User.is_active == True)
            )
        )
        total_instructors = instructors_result.scalar()
        
        # Total courses
        courses_result = await db.execute(
            select(func.count(Course.id)).where(Course.is_published == True)
        )
        total_courses = courses_result.scalar()
        
        # Total enrollments
        enrollments_result = await db.execute(
            select(func.count(Enrollment.id))
        )
        total_enrollments = enrollments_result.scalar()
        
        # Total revenue
        revenue_result = await db.execute(
            select(func.sum(Payment.amount)).where(Payment.status == 'completed')
        )
        total_revenue = float(revenue_result.scalar() or 0)
        
        # Active subscriptions
        active_subs_result = await db.execute(
            select(func.count(UserSubscription.id)).where(
                UserSubscription.status == 'active'
            )
        )
        active_subscriptions = active_subs_result.scalar()
        
        return {
            "total_users": total_users,
            "total_learners": total_learners,
            "total_instructors": total_instructors,
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "total_revenue": total_revenue,
            "active_subscriptions": active_subscriptions,
            "avg_courses_per_instructor": round(total_courses / total_instructors, 2) if total_instructors > 0 else 0
        }
    
    async def get_user_growth(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get user growth metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # New users in period
        new_users_result = await db.execute(
            select(func.count(User.id)).where(
                User.created_at >= start_date
            )
        )
        new_users = new_users_result.scalar()
        
        # Users by day
        daily_users_result = await db.execute(
            select(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            )
            .where(User.created_at >= start_date)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
        )
        
        daily_signups = [
            {"date": str(row.date), "count": row.count}
            for row in daily_users_result.fetchall()
        ]
        
        # Calculate growth rate
        previous_period_result = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.created_at >= start_date - timedelta(days=days),
                    User.created_at < start_date
                )
            )
        )
        previous_period_users = previous_period_result.scalar()
        
        growth_rate = 0
        if previous_period_users > 0:
            growth_rate = ((new_users - previous_period_users) / previous_period_users) * 100
        
        return {
            "new_users": new_users,
            "growth_rate_percentage": round(growth_rate, 2),
            "daily_signups": daily_signups
        }
    
    async def get_engagement_metrics(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get platform engagement metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # DAU (Daily Active Users) - users who logged in today
        today = date.today()
        dau_result = await db.execute(
            select(func.count(distinct(User.id))).where(
                func.date(User.last_login) == today
            )
        )
        dau = dau_result.scalar() or 0
        
        # MAU (Monthly Active Users) - users active in last 30 days
        thirty_days_ago = today - timedelta(days=30)
        mau_result = await db.execute(
            select(func.count(distinct(User.id))).where(
                func.date(User.last_login) >= thirty_days_ago
            )
        )
        mau = mau_result.scalar() or 0
        
        # WAU (Weekly Active Users)
        seven_days_ago = today - timedelta(days=7)
        wau_result = await db.execute(
            select(func.count(distinct(User.id))).where(
                func.date(User.last_login) >= seven_days_ago
            )
        )
        wau = wau_result.scalar() or 0
        
        # Average session duration (from user stats)
        avg_study_time_result = await db.execute(
            select(func.avg(UserStats.total_study_time_minutes))
        )
        avg_study_time = float(avg_study_time_result.scalar() or 0)
        
        # Completion rate
        total_enrollments_result = await db.execute(
            select(func.count(Enrollment.id))
        )
        total_enrollments_count = total_enrollments_result.scalar() or 1
        
        completed_enrollments_result = await db.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.status == 'completed'
            )
        )
        completed_enrollments = completed_enrollments_result.scalar() or 0
        
        completion_rate = (completed_enrollments / total_enrollments_count) * 100
        
        return {
            "dau": dau,
            "wau": wau,
            "mau": mau,
            "dau_mau_ratio": round((dau / mau * 100), 2) if mau > 0 else 0,
            "avg_study_time_minutes": round(avg_study_time, 2),
            "course_completion_rate": round(completion_rate, 2)
        }
    
    async def get_revenue_metrics(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get revenue metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total revenue in period
        period_revenue_result = await db.execute(
            select(func.sum(Payment.amount)).where(
                and_(
                    Payment.status == 'completed',
                    Payment.created_at >= start_date
                )
            )
        )
        period_revenue = float(period_revenue_result.scalar() or 0)
        
        # Revenue by day
        daily_revenue_result = await db.execute(
            select(
                func.date(Payment.created_at).label('date'),
                func.sum(Payment.amount).label('revenue'),
                func.count(Payment.id).label('transactions')
            )
            .where(
                and_(
                    Payment.status == 'completed',
                    Payment.created_at >= start_date
                )
            )
            .group_by(func.date(Payment.created_at))
            .order_by(func.date(Payment.created_at))
        )
        
        daily_revenue = [
            {
                "date": str(row.date),
                "revenue": float(row.revenue),
                "transactions": row.transactions
            }
            for row in daily_revenue_result.fetchall()
        ]
        
        # MRR (Monthly Recurring Revenue) from active subscriptions
        mrr_result = await db.execute(
            select(
                func.sum(Payment.amount)
            )
            .join(UserSubscription, Payment.subscription_id == UserSubscription.id)
            .where(
                and_(
                    UserSubscription.status == 'active',
                    Payment.created_at >= start_date
                )
            )
        )
        mrr = float(mrr_result.scalar() or 0)
        
        # Average transaction value
        avg_transaction_result = await db.execute(
            select(func.avg(Payment.amount)).where(
                and_(
                    Payment.status == 'completed',
                    Payment.created_at >= start_date
                )
            )
        )
        avg_transaction = float(avg_transaction_result.scalar() or 0)
        
        return {
            "period_revenue": round(period_revenue, 2),
            "mrr": round(mrr, 2),
            "avg_transaction_value": round(avg_transaction, 2),
            "daily_revenue": daily_revenue
        }
    
    async def get_top_courses(
        self,
        db: AsyncSession,
        limit: int = 10,
        metric: str = "enrollments"  # enrollments, revenue, rating
    ) -> List[Dict[str, Any]]:
        """Get top performing courses"""
        
        if metric == "enrollments":
            result = await db.execute(
                select(
                    Course.id,
                    Course.title,
                    Course.total_enrollments,
                    Course.average_rating
                )
                .where(Course.is_published == True)
                .order_by(desc(Course.total_enrollments))
                .limit(limit)
            )
            
            return [
                {
                    "course_id": str(row.id),
                    "title": row.title,
                    "enrollments": row.total_enrollments,
                    "rating": float(row.average_rating) if row.average_rating else 0
                }
                for row in result.fetchall()
            ]
        
        elif metric == "revenue":
            result = await db.execute(
                select(
                    Course.id,
                    Course.title,
                    func.sum(Payment.amount).label('revenue')
                )
                .join(Payment, Payment.course_id == Course.id)
                .where(
                    and_(
                        Course.is_published == True,
                        Payment.status == 'completed'
                    )
                )
                .group_by(Course.id, Course.title)
                .order_by(desc('revenue'))
                .limit(limit)
            )
            
            return [
                {
                    "course_id": str(row.id),
                    "title": row.title,
                    "revenue": float(row.revenue)
                }
                for row in result.fetchall()
            ]
        
        elif metric == "rating":
            result = await db.execute(
                select(
                    Course.id,
                    Course.title,
                    Course.average_rating,
                    Course.total_enrollments
                )
                .where(
                    and_(
                        Course.is_published == True,
                        Course.average_rating.isnot(None)
                    )
                )
                .order_by(desc(Course.average_rating))
                .limit(limit)
            )
            
            return [
                {
                    "course_id": str(row.id),
                    "title": row.title,
                    "rating": float(row.average_rating),
                    "enrollments": row.total_enrollments
                }
                for row in result.fetchall()
            ]
        
        return []
    
    async def get_top_instructors(
        self,
        db: AsyncSession,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top performing instructors"""
        result = await db.execute(
            select(
                User.id,
                User.full_name,
                func.count(distinct(Course.id)).label('course_count'),
                func.sum(Course.total_enrollments).label('total_enrollments'),
                func.sum(InstructorEarnings.amount).label('total_earnings')
            )
            .join(Course, Course.created_by == User.id)
            .outerjoin(InstructorEarnings, InstructorEarnings.instructor_id == User.id)
            .where(
                and_(
                    User.role == UserRole.INSTRUCTOR,
                    Course.is_published == True
                )
            )
            .group_by(User.id, User.full_name)
            .order_by(desc('total_enrollments'))
            .limit(limit)
        )
        
        return [
            {
                "instructor_id": str(row.id),
                "name": row.full_name,
                "course_count": row.course_count,
                "total_enrollments": row.total_enrollments or 0,
                "total_earnings": float(row.total_earnings or 0)
            }
            for row in result.fetchall()
        ]
    
    async def get_system_health(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get system health metrics"""
        
        # Recent error rate (would need error logging table)
        # For now, return mock data
        
        # Active sessions (would need session tracking)
        # For now, calculate from recent logins
        recent_logins_result = await db.execute(
            select(func.count(User.id)).where(
                User.last_login >= datetime.utcnow() - timedelta(hours=1)
            )
        )
        active_sessions = recent_logins_result.scalar()
        
        # Database size (PostgreSQL specific)
        # This would require raw SQL and proper permissions
        
        return {
            "active_sessions": active_sessions,
            "status": "healthy",
            "uptime_percentage": 99.9  # Mock data
        }
    
    async def aggregate_daily_metrics(
        self,
        db: AsyncSession,
        target_date: date
    ):
        """Aggregate metrics for a specific day (run as cron job)"""
        
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # User metrics
        new_users_result = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.created_at >= start_datetime,
                    User.created_at <= end_datetime
                )
            )
        )
        new_users = new_users_result.scalar()
        
        dau_result = await db.execute(
            select(func.count(distinct(User.id))).where(
                func.date(User.last_login) == target_date
            )
        )
        dau = dau_result.scalar()
        
        # Revenue metrics
        revenue_result = await db.execute(
            select(
                func.sum(Payment.amount),
                func.count(Payment.id)
            ).where(
                and_(
                    Payment.status == 'completed',
                    Payment.created_at >= start_datetime,
                    Payment.created_at <= end_datetime
                )
            )
        )
        revenue_row = revenue_result.first()
        daily_revenue = float(revenue_row[0] or 0)
        daily_transactions = revenue_row[1] or 0
        
        # Engagement metrics
        enrollments_result = await db.execute(
            select(func.count(Enrollment.id)).where(
                and_(
                    Enrollment.enrolled_at >= start_datetime,
                    Enrollment.enrolled_at <= end_datetime
                )
            )
        )
        daily_enrollments = enrollments_result.scalar()
        
        completions_result = await db.execute(
            select(func.count(Enrollment.id)).where(
                and_(
                    Enrollment.status == 'completed',
                    Enrollment.completed_at >= start_datetime,
                    Enrollment.completed_at <= end_datetime
                )
            )
        )
        daily_completions = completions_result.scalar()
        
        # Store aggregated data
        analytics = PlatformAnalytics(
            date=target_date,
            timeframe='daily',
            metric_type='users',
            metric_data={
                "new_users": new_users,
                "dau": dau,
                "daily_enrollments": daily_enrollments,
                "daily_completions": daily_completions,
                "daily_revenue": daily_revenue,
                "daily_transactions": daily_transactions
            }
        )
        
        db.add(analytics)
        await db.commit()
        
        return analytics
