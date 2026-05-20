"""change aktual_close to datetime for inspectionk3l

Revision ID: e5f7a9b1c3d5
Revises: d4e6f8a0b2c4
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = 'e5f7a9b1c3d5'
down_revision = 'd4e6f8a0b2c4'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'reports_inspectionk3l', 'aktual_close',
        type_=sa.DateTime(),
        existing_type=sa.Date(),
        existing_nullable=True,
        postgresql_using='aktual_close::timestamp',
    )


def downgrade():
    op.alter_column(
        'reports_inspectionk3l', 'aktual_close',
        type_=sa.Date(),
        existing_type=sa.DateTime(),
        existing_nullable=True,
        postgresql_using='aktual_close::date',
    )
