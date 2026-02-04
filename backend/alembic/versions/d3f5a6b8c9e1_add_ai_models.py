"""Add AI models tables

Revision ID: add_ai_models
Revises: c2805e67387e
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_ai_models'
down_revision = 'c2805e67387e'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types (only if they don't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE snapshot_type AS ENUM ('initial', 'weekly_adjustment', 'milestone', 'manual');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE recommendation_type AS ENUM ('next_lesson', 'revision', 'practice', 'difficulty_adjustment', 'course');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE recommendation_action AS ENUM ('accepted', 'skipped', 'modified', 'ignored');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create learning_path_snapshots table
    op.create_table(
        'learning_path_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('learning_goal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('learning_goals.id', ondelete='CASCADE'), nullable=True),
        sa.Column('snapshot_type', postgresql.ENUM('initial', 'weekly_adjustment', 'milestone', 'manual', name='snapshot_type', create_type=False), nullable=False),
        sa.Column('recommended_path', postgresql.JSONB, nullable=False),
        sa.Column('estimated_total_hours', sa.Integer, nullable=True),
        sa.Column('estimated_completion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confidence_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('changes_from_previous', postgresql.JSONB, nullable=True),
        sa.Column('adjustment_reasons', postgresql.JSONB, nullable=True),
        sa.Column('active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Create indexes for learning_path_snapshots
    op.create_index('idx_path_snapshots_user_active', 'learning_path_snapshots', ['user_id', 'active'])
    op.create_index('idx_path_snapshots_user_created', 'learning_path_snapshots', ['user_id', sa.text('created_at DESC')])
    
    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('recommendation_type', postgresql.ENUM('next_lesson', 'revision', 'practice', 'difficulty_adjustment', 'course', name='recommendation_type', create_type=False), nullable=False, index=True),
        sa.Column('recommended_content_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('recommended_content_type', sa.String(50), nullable=True),
        sa.Column('reason', sa.Text, nullable=False),
        sa.Column('confidence_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('priority', sa.Integer, default=5),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('features_used', postgresql.JSONB, nullable=True),
        sa.Column('user_action', postgresql.ENUM('accepted', 'skipped', 'modified', 'ignored', name='recommendation_action', create_type=False), nullable=True),
        sa.Column('actioned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Create indexes for recommendations
    op.create_index('idx_recommendations_user_expires', 'recommendations', ['user_id', 'expires_at'])
    # Partial index for pending recommendations (no NOW() to keep it immutable)
    op.create_index('idx_recommendations_active', 'recommendations', ['user_id', 'expires_at'], 
                    postgresql_where=sa.text("user_action IS NULL"))
    
    # Create ml_model_metadata table
    op.create_table(
        'ml_model_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('model_name', sa.String(100), nullable=False, index=True),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=True),
        sa.Column('model_path', sa.String(500), nullable=True),
        sa.Column('feature_columns', postgresql.JSONB, nullable=True),
        sa.Column('performance_metrics', postgresql.JSONB, nullable=True),
        sa.Column('training_data_size', sa.Integer, nullable=True),
        sa.Column('trained_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, default=False, nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    op.create_index('idx_ml_models_active', 'ml_model_metadata', ['model_name'], 
                    postgresql_where=sa.text("is_active = true"))
    
    # Create learner_events table (non-partitioned for now - partition manually if needed)
    op.create_table(
        'learner_events',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('event_type', sa.String(100), nullable=False, index=True),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=True),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=True),
        sa.Column('session_id', sa.String(100), nullable=True, index=True),
        sa.Column('event_data', postgresql.JSONB, nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('ip_address', postgresql.INET, nullable=True)
    )
    
    # Create indexes for learner_events
    op.create_index('idx_events_user_timestamp', 'learner_events', ['user_id', sa.text('event_timestamp DESC')])
    op.create_index('idx_events_type_timestamp', 'learner_events', ['event_type', sa.text('event_timestamp DESC')])
    op.create_index('idx_events_data_gin', 'learner_events', ['event_data'], postgresql_using='gin')


def downgrade():
    # Drop tables
    op.drop_table('learner_events')
    op.drop_table('ml_model_metadata')
    op.drop_table('recommendations')
    op.drop_table('learning_path_snapshots')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS recommendation_action")
    op.execute("DROP TYPE IF EXISTS recommendation_type")
    op.execute("DROP TYPE IF EXISTS snapshot_type")
