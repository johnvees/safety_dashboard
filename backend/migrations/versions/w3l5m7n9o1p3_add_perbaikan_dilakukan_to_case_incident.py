"""add perbaikan_dilakukan to case_incident

Revision ID: w3l5m7n9o1p3
Revises: v2k4l6m8n0o2
Create Date: 2026-06-05

"""
from alembic import op
import sqlalchemy as sa

revision = 'w3l5m7n9o1p3'
down_revision = 'v2k4l6m8n0o2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('case_incidents',
        sa.Column('perbaikan_dilakukan', sa.Text, nullable=True)
    )


def downgrade():
    op.drop_column('case_incidents', 'perbaikan_dilakukan')
