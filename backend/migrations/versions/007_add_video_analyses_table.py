"""Add video_analyses table

Revision ID: 007_add_video_analyses_table
Revises: 006_add_export_settings_to_projects
Create Date: 2026-01-12 15:22:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '007_add_video_analyses_table'
down_revision = 'a912a64b7a86'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add video_analyses table"""
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'video_analyses' not in inspector.get_table_names():
        op.create_table('video_analyses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('file_id', sa.String(length=200), nullable=False),
        sa.Column('analysis_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_id')
        )


def downgrade() -> None:
    """Remove video_analyses table"""
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'video_analyses' in inspector.get_table_names():
        op.drop_table('video_analyses')
