"""change tanggal to datetime for inspectionk3l and hse_daily

Revision ID: d4e6f8a0b2c4
Revises: c3d5e7f9a1b2
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = 'd4e6f8a0b2c4'
down_revision = 'c3d5e7f9a1b2'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'reports_inspectionk3l', 'tanggal',
        type_=sa.DateTime(),
        existing_type=sa.Date(),
        postgresql_using='tanggal::timestamp',
    )
    op.alter_column(
        'reports_hse_daily', 'tanggal',
        type_=sa.DateTime(),
        existing_type=sa.Date(),
        postgresql_using='tanggal::timestamp',
    )


def downgrade():
    op.alter_column(
        'reports_inspectionk3l', 'tanggal',
        type_=sa.Date(),
        existing_type=sa.DateTime(),
        postgresql_using='tanggal::date',
    )
    op.alter_column(
        'reports_hse_daily', 'tanggal',
        type_=sa.Date(),
        existing_type=sa.DateTime(),
        postgresql_using='tanggal::date',
    )
