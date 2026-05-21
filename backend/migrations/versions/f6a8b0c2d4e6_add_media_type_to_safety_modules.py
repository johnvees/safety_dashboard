"""add media_type to safety_modules

Revision ID: f6a8b0c2d4e6
Revises: b9d2f4a6c8e0
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = 'f6a8b0c2d4e6'
down_revision = 'b9d2f4a6c8e0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('safety_modules', sa.Column('media_type', sa.String(20), nullable=True, server_default='video'))


def downgrade():
    op.drop_column('safety_modules', 'media_type')
