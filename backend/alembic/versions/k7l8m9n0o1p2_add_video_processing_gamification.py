"""add_video_processing_gamification

Revision ID: k7l8m9n0o1p2
Revises: c4b9a5e3cc72
Create Date: 2026-02-07 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


# revision identifiers, used by Alembic.
revision = 'k7l8m9n0o1p2'
down_revision = 'c4b9a5e3cc72'
branch_labels = None
depends_on = None


def upgrade():
    # ==========================================
    # 1. VIDEO PROCESSING ENHANCEMENTS
    # ==========================================
    
    # Add video processing fields to lessons table
    op.add_column('lessons', sa.Column('video_status', sa.String(50), nullable=True))
    op.add_column('lessons', sa.Column('video_original_url', sa.String(512), nullable=True))
    op.add_column('lessons', sa.Column('video_hls_url', sa.String(512), nullable=True))
    op.add_column('lessons', sa.Column('video_thumbnail_url', sa.String(512), nullable=True))
    op.add_column('lessons', sa.Column('video_duration_seconds', sa.Integer(), nullable=True))
    op.add_column('lessons', sa.Column('video_quality_variants', JSONB, nullable=True))
    op.add_column('lessons', sa.Column('transcoding_job_id', sa.String(255), nullable=True))
    op.add_column('lessons', sa.Column('transcoding_progress', sa.Integer(), nullable=True))
    
    # Add video analytics table
    op.create_table(
        'video_analytics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('lesson_id', UUID(as_uuid=True), sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('watch_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('completion_percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('playback_speed', sa.Numeric(3, 2), nullable=True),
        sa.Column('quality_selected', sa.String(50), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('watched_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # ==========================================
    # 2. GAMIFICATION SYSTEM
    # ==========================================
    
    # Achievements table
    op.create_table(
        'achievements',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),  # learning, social, completion, streak
        sa.Column('icon_url', sa.String(512), nullable=True),
        sa.Column('badge_color', sa.String(50), nullable=True),
        sa.Column('points', sa.Integer(), default=0),
        sa.Column('requirement_type', sa.String(100), nullable=False),  # courses_completed, streak_days, etc.
        sa.Column('requirement_value', sa.Integer(), nullable=False),
        sa.Column('requirement_data', JSONB, nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('rarity', sa.String(50), nullable=True),  # common, rare, epic, legendary
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # User achievements (many-to-many)
    op.create_table(
        'user_achievements',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('achievement_id', UUID(as_uuid=True), sa.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('progress', sa.Integer(), default=0),
        sa.Column('is_displayed', sa.Boolean(), default=True),
        sa.UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )
    
    # User stats for gamification
    op.create_table(
        'user_stats',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        sa.Column('total_xp', sa.Integer(), default=0),
        sa.Column('level', sa.Integer(), default=1),
        sa.Column('courses_completed', sa.Integer(), default=0),
        sa.Column('lessons_completed', sa.Integer(), default=0),
        sa.Column('quizzes_completed', sa.Integer(), default=0),
        sa.Column('current_streak_days', sa.Integer(), default=0),
        sa.Column('longest_streak_days', sa.Integer(), default=0),
        sa.Column('last_activity_date', sa.Date(), nullable=True),
        sa.Column('total_study_time_minutes', sa.Integer(), default=0),
        sa.Column('achievements_unlocked', sa.Integer(), default=0),
        sa.Column('rank_position', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # XP transaction log
    op.create_table(
        'xp_transactions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('reference_type', sa.String(100), nullable=True),  # lesson, quiz, achievement
        sa.Column('reference_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Leaderboard (materialized view alternative - actual table for performance)
    op.create_table(
        'leaderboard_cache',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('total_xp', sa.Integer(), default=0),
        sa.Column('level', sa.Integer(), default=1),
        sa.Column('courses_completed', sa.Integer(), default=0),
        sa.Column('current_streak', sa.Integer(), default=0),
        sa.Column('timeframe', sa.String(50), default='all_time'),  # all_time, monthly, weekly
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # ==========================================
    # 3. ADMIN ANALYTICS AGGREGATIONS
    # ==========================================
    
    # Daily/Weekly/Monthly platform statistics
    op.create_table(
        'platform_analytics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('timeframe', sa.String(50), nullable=False),  # daily, weekly, monthly
        sa.Column('metric_type', sa.String(100), nullable=False),  # users, revenue, engagement
        sa.Column('metric_data', JSONB, nullable=False),
        # Example metric_data structure:
        # {
        #   "dau": 1234,
        #   "mau": 5678,
        #   "new_users": 45,
        #   "revenue": 12345.67,
        #   "courses_completed": 89,
        #   "avg_engagement_minutes": 45.6
        # }
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('date', 'timeframe', 'metric_type', name='uq_platform_analytics'),
    )
    
    # Course performance analytics
    op.create_table(
        'course_analytics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('enrollments_count', sa.Integer(), default=0),
        sa.Column('completions_count', sa.Integer(), default=0),
        sa.Column('avg_completion_time_hours', sa.Numeric(10, 2), nullable=True),
        sa.Column('avg_rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('total_revenue', sa.Numeric(12, 2), default=0),
        sa.Column('active_learners', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('course_id', 'date', name='uq_course_analytics_date'),
    )
    
    # Instructor performance analytics
    op.create_table(
        'instructor_analytics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('instructor_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('total_students', sa.Integer(), default=0),
        sa.Column('total_courses', sa.Integer(), default=0),
        sa.Column('total_revenue', sa.Numeric(12, 2), default=0),
        sa.Column('avg_course_rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('total_enrollments', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('instructor_id', 'date', name='uq_instructor_analytics_date'),
    )


def downgrade():
    # Drop analytics tables
    op.drop_table('instructor_analytics')
    op.drop_table('course_analytics')
    op.drop_table('platform_analytics')
    
    # Drop gamification tables
    op.drop_table('leaderboard_cache')
    op.drop_table('xp_transactions')
    op.drop_table('user_stats')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    
    # Drop video analytics
    op.drop_table('video_analytics')
    
    # Remove video processing columns from lessons
    op.drop_column('lessons', 'transcoding_progress')
    op.drop_column('lessons', 'transcoding_job_id')
    op.drop_column('lessons', 'video_quality_variants')
    op.drop_column('lessons', 'video_duration_seconds')
    op.drop_column('lessons', 'video_thumbnail_url')
    op.drop_column('lessons', 'video_hls_url')
    op.drop_column('lessons', 'video_original_url')
    op.drop_column('lessons', 'video_status')
