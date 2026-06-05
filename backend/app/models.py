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
    department_id = Column(Integer, ForeignKey("departments.id"))
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
    foto_sebelum = Column(Text)
    foto_sesudah = Column(Text)

    # Lokasi
    lokasi = Column(String(150))

    # Saran Perbaikan (dari form tambah/ubah temuan)
    saran_perbaikan = Column(Text)

    # Tindak Lanjut (dari form tindak lanjut)
    tindakan_perbaikan = Column(Text)
    ditindaklanjuti_oleh = Column(String(100))
    ditindaklanjuti_department_id = Column(Integer, ForeignKey("departments.id"))
    tanggal_tindaklanjuti = Column(DateTime)

    target_selesai = Column(Date)

    # Status
    status = Column(String(50), default="Open", server_default="Open")
    aktual_close = Column(DateTime)

    # Relasi
    created_by = Column(Integer, ForeignKey("users.id"))
    business_unit_id = Column(Integer, ForeignKey("business_units.id"))
    plant_id = Column(Integer, ForeignKey("plants.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))

    # Pelapor
    pelapor_username = Column(String(100))
    pelapor_department_id = Column(Integer, ForeignKey("departments.id"))

    # Jenis Inspeksi
    jenis_inspeksi = Column(String(50))

    # Tanggal Pelaporan (auto WIB on create)
    tanggal_pelaporan = Column(DateTime)

    # Petugas Inspeksi (JSON: [{nama, departmentId}])
    petugas_inspeksi = Column(Text)

    # Validasi Safety
    divalidasi_oleh = Column(String(100))
    divalidasi_department_id = Column(Integer, ForeignKey("departments.id"))
    tanggal_validasi = Column(DateTime)
    alasan_validasi = Column(Text)
    status_validasi = Column(String(20))

    # Audit trail
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("status IN ('Open', 'In Progress', 'Closed', 'Progress Validasi')", name="reports_inspectionk3l_status_check"),
    )


class InspectionK3LTindakLanjutHistory(Base):
    __tablename__ = "inspection_k3l_tindak_lanjut_history"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("reports_inspectionk3l.id", ondelete="CASCADE"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    tindakan_perbaikan = Column(Text)
    foto_sesudah = Column(Text)
    ditindaklanjuti_oleh = Column(String(100))
    ditindaklanjuti_department_id = Column(Integer, ForeignKey("departments.id"))
    tanggal_tindaklanjuti = Column(DateTime)
    created_at = Column(DateTime, server_default=func.current_timestamp())


class InspectionK3LValidasiHistory(Base):
    __tablename__ = "inspection_k3l_validasi_history"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("reports_inspectionk3l.id", ondelete="CASCADE"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    divalidasi_oleh = Column(String(100))
    divalidasi_department_id = Column(Integer, ForeignKey("departments.id"))
    tanggal_validasi = Column(DateTime)
    alasan_validasi = Column(Text)
    status_validasi = Column(String(20))
    created_at = Column(DateTime, server_default=func.current_timestamp())


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


class CaseIncident(Base):
    __tablename__ = "report_case_incidents"

    id = Column(Integer, primary_key=True, index=True)

    # Pelapor
    nama_pelapor = Column(String(100), nullable=False)
    pelapor_dept_id = Column(Integer, ForeignKey("departments.id"))

    # Saksi
    nama_saksi = Column(String(100))
    saksi_dept_id = Column(Integer, ForeignKey("departments.id"))
    saksi_list = Column(Text)  # JSON: [{nama, departmentId}]

    # Foto Kejadian
    foto_kejadian = Column(Text)  # JSON: [url, ...]

    # Waktu
    tanggal_kejadian = Column(DateTime, nullable=False)
    tanggal_pelaporan = Column(DateTime, nullable=False)

    # Korban
    nama_korban = Column(String(100), nullable=False)
    korban_dept_id = Column(Integer, ForeignKey("departments.id"))
    status_karyawan = Column(String(50))

    # Kejadian
    jenis_kecelakaan = Column(String(100))
    lokasi_kecelakaan = Column(String(200))

    # Hasil Investigasi
    deskripsi_kecelakaan = Column(Text)
    penyebab_kecelakaan = Column(Text)

    # Tindakan Perbaikan
    perbaikan_dilakukan = Column(Text)
    target_penyelesaian = Column(Date)
    status = Column(String(50), default="Open", server_default="Open")

    # Relasi
    created_by = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("status IN ('Open', 'In Progress', 'Closed')", name="case_incidents_status_check"),
    )


class SafetyModule(Base):
    __tablename__ = "safety_modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    video_url = Column(String(500))
    media_type = Column(String(20), default="video")
    files = Column(Text)  # JSON array: [{url, mediaType, name}]
    peraturan = Column(String(100))
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text)
    link = Column(String(255))
    is_read = Column(Boolean, server_default="false")
    created_at = Column(DateTime, server_default=func.current_timestamp())


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(Text, nullable=False, unique=True)
    p256dh = Column(Text, nullable=False)
    auth = Column(Text, nullable=False)
    user_agent = Column(String(300))
    created_at = Column(DateTime, server_default=func.current_timestamp())
