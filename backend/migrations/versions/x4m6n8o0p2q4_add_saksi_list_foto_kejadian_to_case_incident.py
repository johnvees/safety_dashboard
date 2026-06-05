"""add saksi_list and foto_kejadian to case_incident

Revision ID: x4m6n8o0p2q4
Revises: w3l5m7n9o1p3
Create Date: 2026-06-05

"""
from alembic import op
import sqlalchemy as sa

revision = 'x4m6n8o0p2q4'
down_revision = 'w3l5m7n9o1p3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('case_incidents', sa.Column('saksi_list', sa.Text, nullable=True))
    op.add_column('case_incidents', sa.Column('foto_kejadian', sa.Text, nullable=True))


def downgrade():
    op.drop_column('case_incidents', 'foto_kejadian')
    op.drop_column('case_incidents', 'saksi_list')
