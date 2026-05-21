from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    level = Column(Integer, nullable=False)
    description = Column(Text)


class BusinessUnit(Base):
    __tablename__ = "business_units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime, server_default=func.current_timestamp())


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    business_unit_id = Column(Integer, ForeignKey("business_units.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    location = Column(String(150))
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime, server_default=func.current_timestamp())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    verified = Column(Boolean)
    verification_code = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    username = Column(String(50), unique=True)
    full_name = Column(String(100))
    role_id = Column(Integer, ForeignKey("roles.id"))
    business_unit_id = Column(Integer, ForeignKey("business_units.id"))
    plant_id = Column(Integer, ForeignKey("plants.id"))
    is_active = Column(Boolean, server_default="true")
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    last_login = Column(DateTime)
    otp_expires_at = Column(DateTime)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime, server_default=func.current_timestamp())


class InspectionK3L(Base):
    __tablename__ = "reports_inspectionk3l"

    id = Column(Integer, primary_key=True, index=True)

    tanggal = Column(DateTime, nullable=False)

    # Temuan
    kategori_temuan = Column(String(100), nullable=False)
    deskripsi_temuan = Column(Text)

    # Foto (path/url)
    foto_sebelum = Column(String(500))
    foto_sesudah = Column(String(500))

    # Lokasi
    lokasi = Column(String(150))

    # Tindakan
    tindakan_perbaikan = Column(Text)
    target_selesai = Column(Date)

    # Status
    status = Column(String(50), default="Open", server_default="Open")
    aktual_close = Column(DateTime)

    # Relasi
    created_by = Column(Integer, ForeignKey("users.id"))
    business_unit_id = Column(Integer, ForeignKey("business_units.id"))
    plant_id = Column(Integer, ForeignKey("plants.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))

    # Audit trail
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("status IN ('Open', 'In Progress', 'Closed')", name="reports_inspectionk3l_status_check"),
    )


class HseDailyReport(Base):
    __tablename__ = "reports_hse_daily"

    id = Column(Integer, primary_key=True, index=True)
    tanggal = Column(DateTime, nullable=False)

    # Pekerjaan & Pekerja (JSON arrays stored as text)
    pekerjaan = Column(Text, nullable=False)
    pekerja = Column(Text, nullable=False)
    lokasi_pekerjaan = Column(String(200))

    # Permit
    status_permit = Column(Boolean, server_default="false", nullable=False)
    no_permit = Column(String(100))

    # Jenis pekerjaan
    jenis_pekerjaan = Column(String(100))
    jenis_pekerjaan_lainnya = Column(String(200))

    # Hazard analysis (JSON arrays stored as text)
    potensi_bahaya = Column(Text)
    level_risiko = Column(String(20))
    pengendalian_bahaya = Column(Text)

    # HSE officer & notes
    pengawas_hse = Column(String(100))
    saran_masukan = Column(Text)

    # Photos (JSON array of URLs)
    foto = Column(Text)

    # Relasi
    department_id = Column(Integer, ForeignKey("departments.id"))
    business_unit_id = Column(Integer, ForeignKey("business_units.id"))
    plant_id = Column(Integer, ForeignKey("plants.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("level_risiko IN ('Rendah', 'Sedang', 'Tinggi')", name="reports_hse_daily_level_risiko_check"),
    )


class Comment(Base):
    __tablename__ = "report_comments"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(20), nullable=False)  # 'inspection_k3l' or 'hse_daily'
    report_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "report_type IN ('inspection_k3l', 'hse_daily')",
            name="report_comments_report_type_check",
        ),
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False, server_default="")
    attachment_url = Column(String(500), nullable=True)
    attachment_type = Column(String(20), nullable=True)  # 'image' | 'video'
    created_at = Column(DateTime, server_default=func.current_timestamp(), index=True)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    read_at = Column(DateTime, nullable=True)


class SafetyModule(Base):
    __tablename__ = "safety_modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    video_url = Column(String(500))
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
