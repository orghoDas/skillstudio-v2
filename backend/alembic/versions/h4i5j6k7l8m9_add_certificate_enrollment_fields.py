"""Add certificate_url and status to enrollments

Revision ID: j6k7l8m9n0o1
Revises: h4i5j6k7l8m9
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'j6k7l8m9n0o1'
down_revision = 'h4i5j6k7l8m9'
branch_labels = None
depends_on = None


def upgrade():
    # Add status column to enrollments
    op.add_column('enrollments', sa.Column('status', sa.String(50), nullable=False, server_default='active'))
    
    # Add certificate_url column to enrollments
    op.add_column('enrollments', sa.Column('certificate_url', sa.String(512), nullable=True))
    
    # Update existing enrollments: set status to 'completed' where completed_at is not null
    op.execute("""
        UPDATE enrollments 
        SET status = 'completed' 
        WHERE completed_at IS NOT NULL
    """)


def downgrade():
    op.drop_column('enrollments', 'certificate_url')
    op.drop_column('enrollments', 'status')
