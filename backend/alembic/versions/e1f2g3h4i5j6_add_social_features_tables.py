"""add_social_features_tables

Revision ID: e1f2g3h4i5j6
Revises: d3f5a6b8c9e1
Create Date: 2026-02-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e1f2g3h4i5j6'
down_revision = 'd3f5a6b8c9e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create discussion_category enum
    op.execute("CREATE TYPE discussion_category AS ENUM ('general', 'lesson_specific', 'technical', 'career', 'projects', 'announcements')")
    
    # Create course_reviews table
    op.create_table('course_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('review_text', sa.Text(), nullable=True),
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('not_helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_verified_purchase', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('instructor_response', sa.Text(), nullable=True),
        sa.Column('instructor_response_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range')
    )
    op.create_index('ix_course_reviews_course_id', 'course_reviews', ['course_id'])
    op.create_index('ix_course_reviews_user_id', 'course_reviews', ['user_id'])
    
    # Create certificates table
    op.create_table('certificates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('certificate_number', sa.String(length=50), nullable=False),
        sa.Column('issued_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completion_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('final_grade', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('total_hours_spent', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('skills_achieved', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('certificate_url', sa.String(length=512), nullable=True),
        sa.Column('verification_url', sa.String(length=512), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('certificate_number')
    )
    op.create_index('ix_certificates_user_id', 'certificates', ['user_id'])
    op.create_index('ix_certificates_course_id', 'certificates', ['course_id'])
    
    # Create discussions table
    op.create_table('discussions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.Enum('general', 'lesson_specific', 'technical', 'career', 'projects', 'announcements', name='discussion_category'), nullable=False, server_default='general'),
        sa.Column('is_pinned', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_resolved', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_locked', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('views_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('reply_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('upvotes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_discussions_course_id', 'discussions', ['course_id'])
    op.create_index('ix_discussions_category', 'discussions', ['category'])
    
    # Create discussion_replies table
    op.create_table('discussion_replies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('discussion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_reply_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_instructor_response', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_accepted_answer', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('upvotes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_edited', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['discussion_id'], ['discussions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_reply_id'], ['discussion_replies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_discussion_replies_discussion_id', 'discussion_replies', ['discussion_id'])


def downgrade() -> None:
    op.drop_index('ix_discussion_replies_discussion_id', table_name='discussion_replies')
    op.drop_table('discussion_replies')
    
    op.drop_index('ix_discussions_category', table_name='discussions')
    op.drop_index('ix_discussions_course_id', table_name='discussions')
    op.drop_table('discussions')
    
    op.drop_index('ix_certificates_course_id', table_name='certificates')
    op.drop_index('ix_certificates_user_id', table_name='certificates')
    op.drop_table('certificates')
    
    op.drop_index('ix_course_reviews_user_id', table_name='course_reviews')
    op.drop_index('ix_course_reviews_course_id', table_name='course_reviews')
    op.drop_table('course_reviews')
    
    op.execute('DROP TYPE discussion_category')
