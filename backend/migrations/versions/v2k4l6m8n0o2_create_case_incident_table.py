"""create case_incident table

Revision ID: v2k4l6m8n0o2
Revises: u1j3k5l7m9n1
Create Date: 2026-06-05

"""
from alembic import op
import sqlalchemy as sa

revision = 'v2k4l6m8n0o2'
down_revision = 'u1j3k5l7m9n1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'case_incidents',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('nama_pelapor', sa.String(100), nullable=False),
        sa.Column('pelapor_dept_id', sa.Integer, sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('nama_saksi', sa.String(100), nullable=True),
        sa.Column('saksi_dept_id', sa.Integer, sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('tanggal_kejadian', sa.DateTime, nullable=False),
        sa.Column('tanggal_pelaporan', sa.DateTime, nullable=False),
        sa.Column('nama_korban', sa.String(100), nullable=False),
        sa.Column('korban_dept_id', sa.Integer, sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('status_karyawan', sa.String(50), nullable=True),
        sa.Column('jenis_kecelakaan', sa.String(100), nullable=True),
        sa.Column('lokasi_kecelakaan', sa.String(200), nullable=True),
        sa.Column('deskripsi_kecelakaan', sa.Text, nullable=True),
        sa.Column('penyebab_kecelakaan', sa.Text, nullable=True),
        sa.Column('target_penyelesaian', sa.Date, nullable=True),
        sa.Column('status', sa.String(50), server_default='Open', nullable=True),
        sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("status IN ('Open', 'In Progress', 'Closed')", name='case_incidents_status_check'),
    )


def downgrade():
    op.drop_table('case_incidents')
