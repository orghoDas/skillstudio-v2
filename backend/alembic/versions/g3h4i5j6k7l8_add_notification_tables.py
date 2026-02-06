"""add_notification_tables

Revision ID: g3h4i5j6k7l8
Revises: f2g3h4i5j6k7
Create Date: 2026-02-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'g3h4i5j6k7l8'
down_revision = 'f2g3h4i5j6k7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notification_type enum
    op.execute("""
        CREATE TYPE notification_type AS ENUM (
            'course_update', 'new_enrollment', 'course_completion', 'new_review',
            'review_response', 'discussion_reply', 'payment_success', 'payout_approved',
            'payout_completed', 'new_certificate', 'subscription_expiring',
            'subscription_renewed', 'achievement_unlocked', 'system_announcement'
        )
    """)
    
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum(
            'course_update', 'new_enrollment', 'course_completion', 'new_review',
            'review_response', 'discussion_reply', 'payment_success', 'payout_approved',
            'payout_completed', 'new_certificate', 'subscription_expiring',
            'subscription_renewed', 'achievement_unlocked', 'system_announcement',
            name='notification_type'
        ), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('enrollment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('discussion_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('action_url', sa.String(length=512), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])
    
    # Create notification_preferences table
    op.create_table('notification_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email_course_updates', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_new_enrollments', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_course_completions', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_new_reviews', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_discussion_replies', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_payment_updates', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_payout_updates', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_marketing', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('inapp_course_updates', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('inapp_new_enrollments', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('inapp_course_completions', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('inapp_new_reviews', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('inapp_discussion_replies', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('inapp_payment_updates', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('inapp_payout_updates', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_notification_preferences_user_id', 'notification_preferences', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_notification_preferences_user_id', table_name='notification_preferences')
    op.drop_table('notification_preferences')
    
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
    
    op.execute('DROP TYPE notification_type')
