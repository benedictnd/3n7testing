"""add_training_logs_index

Revision ID: ba3f1e926b04
Revises: 20240313_initial_schema
Create Date: 2024-05-15 10:15:32.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ba3f1e926b04'
down_revision = '20240313_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add composite index to training_logs table to optimize query performance.
    This index specifically targets the common query pattern in the /training/logs endpoint
    which filters by user_id, session_id and sorts by created_at.
    
    Using PostgreSQL-specific optimizations:
    - btree for the composite index (efficient for equality and range operations)
    - brin for the date index (efficient for time-series data with natural ordering)
    - concurrent creation to avoid locking tables in production
    """
    # Use raw SQL for concurrent index creation to avoid table locks
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS training_logs_user_session_idx "
        "ON training_logs (user_id, session_id, created_at DESC) "
        "USING btree"
    )
    
    # Add BRIN index for date range queries (more efficient for time-series data)
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS training_logs_created_at_idx "
        "ON training_logs (created_at) "
        "USING brin"
    )


def downgrade():
    """Remove the indexes if needed to rollback"""
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS training_logs_user_session_idx")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS training_logs_created_at_idx") 