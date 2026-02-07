"""Rename metadata to room_metadata in realtime tables

Revision ID: l8m9n0o1p2q3
Revises: k7l8m9n0o1p2
Create Date: 2026-02-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'l8m9n0o1p2q3'
down_revision = 'k7l8m9n0o1p2'
branch_labels = None
depends_on = None


def upgrade():
    """
    Rename metadata column to room_metadata in realtime tables to avoid SQLAlchemy reserved keyword conflict.
    This aligns the database schema with the model definitions.
    """
    # Rename metadata to room_metadata in chat_rooms table
    op.alter_column('chat_rooms', 'metadata', new_column_name='room_metadata')
    
    # Rename metadata to room_metadata in chat_messages table
    op.alter_column('chat_messages', 'metadata', new_column_name='room_metadata')
    
    # Rename metadata to room_metadata in live_class_sessions table
    op.alter_column('live_class_sessions', 'metadata', new_column_name='room_metadata')


def downgrade():
    """
    Rename back to metadata for rollback.
    """
    # Rename room_metadata back to metadata in chat_rooms table
    op.alter_column('chat_rooms', 'room_metadata', new_column_name='metadata')
    
    # Rename room_metadata back to metadata in chat_messages table
    op.alter_column('chat_messages', 'room_metadata', new_column_name='metadata')
    
    # Rename room_metadata back to metadata in live_class_sessions table
    op.alter_column('live_class_sessions', 'room_metadata', new_column_name='metadata')
