"""add attachment columns to chat_messages

Revision ID: b9d2f4a6c8e0
Revises: a7c9e1d3f5b7
Create Date: 2026-05-21 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b9d2f4a6c8e0'
down_revision: Union[str, Sequence[str], None] = 'a7c9e1d3f5b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chat_messages', sa.Column('attachment_url', sa.String(length=500), nullable=True))
    op.add_column('chat_messages', sa.Column('attachment_type', sa.String(length=20), nullable=True))
    # Existing rows already have non-null content; relax the default for future rows
    op.alter_column('chat_messages', 'content', server_default='', existing_type=sa.Text(), existing_nullable=False)


def downgrade() -> None:
    op.drop_column('chat_messages', 'attachment_type')
    op.drop_column('chat_messages', 'attachment_url')
