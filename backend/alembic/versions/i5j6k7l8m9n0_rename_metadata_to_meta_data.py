"""Rename metadata to meta_data in notifications table

Revision ID: i5j6k7l8m9n0
Revises: j6k7l8m9n0o1
Create Date: 2026-02-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'i5j6k7l8m9n0'
down_revision = 'j6k7l8m9n0o1'
branch_labels = None
depends_on = None


def upgrade():
    # Rename metadata column to meta_data to avoid SQLAlchemy reserved keyword conflict
    op.alter_column('notifications', 'metadata', new_column_name='meta_data')


def downgrade():
    # Rename back to metadata
    op.alter_column('notifications', 'meta_data', new_column_name='metadata')
