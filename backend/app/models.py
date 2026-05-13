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
    role = Column(String, nullable=False, default="user", server_default="user")
    business_unit = Column(String, nullable=False, default="", server_default="")


class InspectionK3L(Base):
    __tablename__ = "reports_inspectionk3l"

    id = Column(Integer, primary_key=True, index=True)

    tanggal = Column(Date, nullable=False)

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
    aktual_close = Column(Date)

    # Relasi
    created_by = Column(Integer, ForeignKey("users.id"))
    business_unit_id = Column(Integer, ForeignKey("business_units.id"))
    plant_id = Column(Integer, ForeignKey("plants.id"))

    # Audit trail
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("status IN ('Open', 'In Progress', 'Closed')", name="reports_inspectionk3l_status_check"),
    )


class SafetyModule(Base):
    __tablename__ = "safety_modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    video_url = Column(String(500))
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
