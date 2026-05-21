"""add report_comments table

Revision ID: f6a8b2c4d6e8
Revises: e5f7a9b1c3d5
Create Date: 2026-05-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6a8b2c4d6e8'
down_revision: Union[str, Sequence[str], None] = 'e5f7a9b1c3d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'report_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=20), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "report_type IN ('inspection_k3l', 'hse_daily')",
            name='report_comments_report_type_check',
        ),
    )
    op.create_index(op.f('ix_report_comments_id'), 'report_comments', ['id'], unique=False)
    op.create_index(
        'ix_report_comments_target',
        'report_comments',
        ['report_type', 'report_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_report_comments_target', table_name='report_comments')
    op.drop_index(op.f('ix_report_comments_id'), table_name='report_comments')
    op.drop_table('report_comments')
