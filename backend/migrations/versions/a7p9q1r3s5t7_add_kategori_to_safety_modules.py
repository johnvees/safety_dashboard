"""add kategori to safety_modules

Revision ID: a7p9q1r3s5t7
Revises: z6o8p0q2r4s6
Create Date: 2026-06-08

"""
from alembic import op
import sqlalchemy as sa

revision = 'a7p9q1r3s5t7'
down_revision = 'z6o8p0q2r4s6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('safety_modules', sa.Column('kategori', sa.String(length=50), nullable=True))


def downgrade():
    op.drop_column('safety_modules', 'kategori')
