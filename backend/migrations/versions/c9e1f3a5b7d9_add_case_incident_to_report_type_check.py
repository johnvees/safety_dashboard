"""add case_incident to report_comments report_type check

Revision ID: c9e1f3a5b7d9
Revises: z6o8p0q2r4s6
Create Date: 2026-06-17

"""
from alembic import op

revision = 'c9e1f3a5b7d9'
down_revision = 'z6o8p0q2r4s6'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('report_comments_report_type_check', 'report_comments', type_='check')
    op.create_check_constraint(
        'report_comments_report_type_check',
        'report_comments',
        "report_type IN ('inspection_k3l', 'hse_daily', 'case_incident')",
    )


def downgrade():
    op.drop_constraint('report_comments_report_type_check', 'report_comments', type_='check')
    op.create_check_constraint(
        'report_comments_report_type_check',
        'report_comments',
        "report_type IN ('inspection_k3l', 'hse_daily')",
    )
