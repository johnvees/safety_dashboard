"""merge_heads

Revision ID: 50c40a3d3b3b
Revises: a1b2c3d4e5f6, c9e1f3a5b7d9
Create Date: 2026-06-17 11:07:54.520041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50c40a3d3b3b'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'c9e1f3a5b7d9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
