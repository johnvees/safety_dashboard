"""rename case_incidents to report_case_incidents

Revision ID: y5n7o9p1q3r5
Revises: x4m6n8o0p2q4
Create Date: 2026-06-05

"""
from alembic import op

revision = 'y5n7o9p1q3r5'
down_revision = 'x4m6n8o0p2q4'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('case_incidents', 'report_case_incidents')


def downgrade():
    op.rename_table('report_case_incidents', 'case_incidents')
