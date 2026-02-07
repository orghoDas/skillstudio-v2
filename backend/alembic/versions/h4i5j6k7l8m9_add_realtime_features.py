"""Add real-time features tables

Revision ID: h4i5j6k7l8m9
Revises: g3h4i5j6k7l8
Create Date: 2026-02-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h4i5j6k7l8m9'
down_revision = 'g3h4i5j6k7l8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Chat Rooms
    op.create_table(
        'chat_rooms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('room_type', sa.Enum('DIRECT', 'COURSE', 'LIVE_CLASS', 'GROUP', name='chatroomtype'), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('courses.id', ondelete='CASCADE'), nullable=True),
        sa.Column('live_class_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), default=dict, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_chat_room_course', 'chat_rooms', ['course_id'])
    op.create_index('idx_chat_room_type', 'chat_rooms', ['room_type'])

    # Chat Participants
    op.create_table(
        'chat_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('room_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_rooms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_online', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_muted', sa.Boolean(), default=False, nullable=False),
    )
    op.create_index('idx_chat_participant_room', 'chat_participants', ['room_id'])
    op.create_index('idx_chat_participant_user', 'chat_participants', ['user_id'])

    # Chat Messages
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('room_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_rooms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message_type', sa.Enum('TEXT', 'IMAGE', 'FILE', 'CODE', 'SYSTEM', name='messagetype'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), default=dict, nullable=False),
        sa.Column('is_edited', sa.Boolean(), default=False, nullable=False),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reply_to_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_messages.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_chat_message_room_created', 'chat_messages', ['room_id', 'created_at'])
    op.create_index('idx_chat_message_sender', 'chat_messages', ['sender_id'])
    op.create_index('idx_chat_message_created', 'chat_messages', ['created_at'])

    # Live Class Sessions
    op.create_table(
        'live_class_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('instructor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scheduled_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('meeting_url', sa.String(512), nullable=True),
        sa.Column('meeting_id', sa.String(255), nullable=True),
        sa.Column('meeting_password', sa.String(255), nullable=True),
        sa.Column('recording_url', sa.String(512), nullable=True),
        sa.Column('is_recorded', sa.Boolean(), default=False, nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('current_participants', sa.Integer(), default=0, nullable=False),
        sa.Column('chat_room_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_rooms.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(50), default='scheduled', nullable=False),
        sa.Column('metadata', postgresql.JSONB(), default=dict, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_live_class_course', 'live_class_sessions', ['course_id'])
    op.create_index('idx_live_class_instructor', 'live_class_sessions', ['instructor_id'])
    op.create_index('idx_live_class_scheduled', 'live_class_sessions', ['scheduled_start'])

    # Live Class Attendees
    op.create_table(
        'live_class_attendees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('live_class_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), default=0, nullable=False),
        sa.Column('questions_asked', sa.Integer(), default=0, nullable=False),
        sa.Column('is_hand_raised', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_muted', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_live_class_attendee_session', 'live_class_attendees', ['session_id'])
    op.create_index('idx_live_class_attendee_user', 'live_class_attendees', ['user_id'])

    # Collaborative Sessions
    op.create_table(
        'collaborative_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('language', sa.String(50), default='python', nullable=False),
        sa.Column('code_content', sa.Text(), default='', nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('max_collaborators', sa.Integer(), default=10, nullable=False),
        sa.Column('is_public', sa.Boolean(), default=False, nullable=False),
        sa.Column('access_code', sa.String(50), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), default=dict, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_collab_session_owner', 'collaborative_sessions', ['owner_id'])
    op.create_index('idx_collab_session_active', 'collaborative_sessions', ['is_active'])

    # Collaborative Participants
    op.create_table(
        'collaborative_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('collaborative_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cursor_position', postgresql.JSONB(), default=dict, nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_active_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_collab_participant_session', 'collaborative_participants', ['session_id'])
    op.create_index('idx_collab_participant_user', 'collaborative_participants', ['user_id'])


def downgrade() -> None:
    op.drop_table('collaborative_participants')
    op.drop_table('collaborative_sessions')
    op.drop_table('live_class_attendees')
    op.drop_table('live_class_sessions')
    op.drop_table('chat_messages')
    op.drop_table('chat_participants')
    op.drop_table('chat_rooms')
    
    op.execute('DROP TYPE IF EXISTS chatroomtype')
    op.execute('DROP TYPE IF EXISTS messagetype')
