"""Initial schema

Revision ID: 20240313_initial
Revises: 
Create Date: 2024-03-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '20240313_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create training_sessions table
    op.create_table('training_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('phases', sa.Text(), nullable=True),
        sa.Column('equipment_needed', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('coach_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['coach_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create attendances table
    op.create_table('attendances',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('training_session_id', sa.String(), nullable=False),
        sa.Column('athlete_id', sa.String(), nullable=False),
        sa.Column('check_in_time', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['athlete_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create feedbacks table
    op.create_table('feedbacks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('training_session_id', sa.String(), nullable=False),
        sa.Column('athlete_id', sa.String(), nullable=False),
        sa.Column('training_quality', sa.Integer(), nullable=False),
        sa.Column('expectations', sa.Integer(), nullable=False),
        sa.Column('body_condition', sa.Integer(), nullable=False),
        sa.Column('intensity', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['athlete_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(), nullable=False),
        sa.Column('recipient_id', sa.String(), nullable=False),
        sa.Column('sender_id', sa.String(), nullable=True),
        sa.Column('related_id', sa.String(), nullable=True),
        sa.Column('link', sa.String(), nullable=True),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('notifications')
    op.drop_table('feedbacks')
    op.drop_table('attendances')
    op.drop_table('training_sessions')
    op.drop_table('users') 