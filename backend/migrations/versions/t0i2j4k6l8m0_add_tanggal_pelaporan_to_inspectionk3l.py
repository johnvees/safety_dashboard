"""add tanggal_pelaporan to inspectionk3l

Revision ID: t0i2j4k6l8m0
Revises: s9h1i3j5k7l9
Create Date: 2026-06-05

"""
from alembic import op
import sqlalchemy as sa

revision = 't0i2j4k6l8m0'
down_revision = 's9h1i3j5k7l9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('reports_inspectionk3l',
        sa.Column('tanggal_pelaporan', sa.DateTime, nullable=True)
    )


def downgrade():
    op.drop_column('reports_inspectionk3l', 'tanggal_pelaporan')
