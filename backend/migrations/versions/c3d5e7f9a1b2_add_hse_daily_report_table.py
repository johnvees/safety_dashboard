"""add_hse_daily_report_table

Revision ID: c3d5e7f9a1b2
Revises: a3f8c1d9e2b7
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d5e7f9a1b2'
down_revision: Union[str, Sequence[str], None] = 'a3f8c1d9e2b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reports_hse_daily',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tanggal', sa.Date(), nullable=False),
        sa.Column('pekerjaan', sa.Text(), nullable=False),
        sa.Column('pekerja', sa.Text(), nullable=False),
        sa.Column('lokasi_pekerjaan', sa.String(200), nullable=True),
        sa.Column('status_permit', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('no_permit', sa.String(100), nullable=True),
        sa.Column('jenis_pekerjaan', sa.String(100), nullable=True),
        sa.Column('jenis_pekerjaan_lainnya', sa.String(200), nullable=True),
        sa.Column('potensi_bahaya', sa.Text(), nullable=True),
        sa.Column('level_risiko', sa.String(20), nullable=True),
        sa.Column('pengendalian_bahaya', sa.Text(), nullable=True),
        sa.Column('pengawas_hse', sa.String(100), nullable=True),
        sa.Column('saran_masukan', sa.Text(), nullable=True),
        sa.Column('foto', sa.Text(), nullable=True),
        sa.Column('department_id', sa.Integer(), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('business_unit_id', sa.Integer(), sa.ForeignKey('business_units.id'), nullable=True),
        sa.Column('plant_id', sa.Integer(), sa.ForeignKey('plants.id'), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.current_timestamp()),
        sa.CheckConstraint(
            "level_risiko IN ('Rendah', 'Sedang', 'Tinggi')",
            name='reports_hse_daily_level_risiko_check',
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_reports_hse_daily_id', 'reports_hse_daily', ['id'])


def downgrade() -> None:
    op.drop_index('ix_reports_hse_daily_id', table_name='reports_hse_daily')
    op.drop_table('reports_hse_daily')
