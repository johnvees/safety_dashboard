import strawberry
import json
import asyncio
from strawberry.fastapi import GraphQLRouter
from typing import Optional, List, AsyncIterator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func as sa_func
from datetime import date, datetime

from app import models, auth
from app.database import get_db
from app.cloudinary_utils import delete_image, delete_video, delete_document
from app.chat_broker import broker as chat_broker
from app.notification_broker import broker as notif_broker
from app import web_push


def _get_db() -> Session:
    return next(get_db())


def _get_current_user(info: strawberry.types.Info) -> Optional[models.User]:
    """Extract current user from request Authorization header."""
    request = info.context["request"]
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        return None
    email = auth.decode_token(token)
    if not email:
        return None
    db = _get_db()
    user = db.query(models.User).filter(models.User.email == email).first()
    db.close()
    return user


def _get_role_level(user: models.User) -> int:
    """Return the role level for a user. Higher level = more restricted."""
    if not user.role_id:
        return 999
    db = _get_db()
    role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
    db.close()
    return role.level if role else 999


def _is_staff(user: models.User) -> bool:
    """Staff (level 6) can only see their own business unit and plant."""
    return _get_role_level(user) >= 6


def _is_privileged(user: models.User) -> bool:
    """Level 0-3 bypasses department restrictions."""
    return _get_role_level(user) <= 3


def _is_safety_department(db, user: models.User) -> bool:
    """True if user belongs to the 'Safety' department."""
    if not user.department_id:
        return False
    dept = db.query(models.Department).filter(models.Department.id == user.department_id).first()
    return bool(dept and dept.name == "Safety")


@strawberry.type
class UserType:
    id: int
    email: str
    role: str
    business_unit: str
    plant: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    role_id: Optional[int] = None
    role_level: Optional[int] = None
    business_unit_id: Optional[int] = None
    plant_id: Optional[int] = None
    department_id: Optional[int] = None
    department: Optional[str] = None


@strawberry.type
class RoleType:
    id: int
    name: str
    level: int
    description: Optional[str] = None


@strawberry.type
class RolePayload:
    success: bool
    message: str
    role: Optional["RoleType"] = None


@strawberry.type
class FullUserType:
    id: int
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    business_unit_id: Optional[int] = None
    plant_id: Optional[int] = None
    department_id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@strawberry.type
class UserPayload:
    success: bool
    message: str
    user: Optional["FullUserType"] = None


@strawberry.type
class AuthPayload:
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[UserType] = None


@strawberry.type
class GenericPayload:
    success: bool
    message: str


@strawberry.type
class BusinessUnitType:
    id: int
    name: str
    code: str = ""
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


@strawberry.type
class BusinessUnitPayload:
    success: bool
    message: str
    business_unit: Optional["BusinessUnitType"] = None


@strawberry.type
class PlantType:
    id: int
    name: str
    code: str = ""
    business_unit_id: Optional[int] = None
    location: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


@strawberry.type
class PlantPayload:
    success: bool
    message: str
    plant: Optional["PlantType"] = None


@strawberry.type
class DepartmentType:
    id: int
    name: str
    code: str = ""
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


@strawberry.type
class DepartmentPayload:
    success: bool
    message: str
    department: Optional["DepartmentType"] = None


@strawberry.type
class InspectionK3LTindakLanjutHistoryType:
    id: int
    inspection_id: int
    round_number: int
    tindakan_perbaikan: Optional[str] = None
    foto_sesudah: Optional[str] = None
    ditindaklanjuti_oleh: Optional[str] = None
    ditindaklanjuti_department_id: Optional[int] = None
    tanggal_tindaklanjuti: Optional[str] = None
    created_at: Optional[str] = None


@strawberry.type
class InspectionK3LValidasiHistoryType:
    id: int
    inspection_id: int
    round_number: int
    divalidasi_oleh: Optional[str] = None
    divalidasi_department_id: Optional[int] = None
    tanggal_validasi: Optional[str] = None
    alasan_validasi: Optional[str] = None
    status_validasi: Optional[str] = None
    created_at: Optional[str] = None


@strawberry.type
class InspectionK3LType:
    id: int
    tanggal: str
    kategori_temuan: str
    deskripsi_temuan: Optional[str] = None
    foto_sebelum: Optional[str] = None
    foto_sesudah: Optional[str] = None
    lokasi: Optional[str] = None
    saran_perbaikan: Optional[str] = None
    tindakan_perbaikan: Optional[str] = None
    ditindaklanjuti_oleh: Optional[str] = None
    ditindaklanjuti_department_id: Optional[int] = None
    tanggal_tindaklanjuti: Optional[str] = None
    target_selesai: Optional[str] = None
    status: str
    aktual_close: Optional[str] = None
    created_by: Optional[int] = None
    business_unit_id: Optional[int] = None
    plant_id: Optional[int] = None
    department_id: Optional[int] = None
    pelapor_username: Optional[str] = None
    pelapor_department_id: Optional[int] = None
    jenis_inspeksi: Optional[str] = None
    tanggal_pelaporan: Optional[str] = None
    petugas_inspeksi: Optional[str] = None
    divalidasi_oleh: Optional[str] = None
    divalidasi_department_id: Optional[int] = None
    tanggal_validasi: Optional[str] = None
    alasan_validasi: Optional[str] = None
    status_validasi: Optional[str] = None
    tindak_lanjut_count: int = 0
    tindak_lanjut_list: Optional[List[InspectionK3LTindakLanjutHistoryType]] = None
    validasi_count: int = 0
    validasi_list: Optional[List[InspectionK3LValidasiHistoryType]] = None
    updated_by_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    comment_count: int = 0


@strawberry.type
class InspectionK3LPayload:
    success: bool
    message: str
    inspection: Optional[InspectionK3LType] = None


@strawberry.type
class CaseIncidentType:
    id: int
    nama_pelapor: str
    pelapor_dept_id: Optional[int] = None
    nama_saksi: Optional[str] = None
    saksi_dept_id: Optional[int] = None
    saksi_list: Optional[str] = None
    foto_kejadian: Optional[str] = None
    tanggal_kejadian: str
    tanggal_pelaporan: str
    nama_korban: str
    korban_dept_id: Optional[int] = None
    status_karyawan: Optional[str] = None
    jenis_kecelakaan: Optional[str] = None
    lokasi_kecelakaan: Optional[str] = None
    deskripsi_kecelakaan: Optional[str] = None
    penyebab_kecelakaan: Optional[str] = None
    perbaikan_dilakukan: Optional[str] = None
    target_penyelesaian: Optional[str] = None
    status: str
    created_by: Optional[int] = None
    business_unit_id: Optional[int] = None
    business_unit_name: Optional[str] = None
    plant_id: Optional[int] = None
    plant_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    comment_count: int = 0


@strawberry.type
class CaseIncidentPayload:
    success: bool
    message: str
    incident: Optional[CaseIncidentType] = None


def _ci_to_type(r: models.CaseIncident, db=None) -> CaseIncidentType:
    close_db = False
    if db is None:
        db = _get_db()
        close_db = True
    try:
        bu = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == r.business_unit_id).first() if r.business_unit_id else None
        plant = db.query(models.Plant).filter(models.Plant.id == r.plant_id).first() if r.plant_id else None
        return CaseIncidentType(
            id=r.id,
            nama_pelapor=r.nama_pelapor,
            pelapor_dept_id=r.pelapor_dept_id,
            nama_saksi=r.nama_saksi,
            saksi_dept_id=r.saksi_dept_id,
            saksi_list=r.saksi_list,
            foto_kejadian=r.foto_kejadian,
            tanggal_kejadian=str(r.tanggal_kejadian) if r.tanggal_kejadian else "",
            tanggal_pelaporan=str(r.tanggal_pelaporan) if r.tanggal_pelaporan else "",
            nama_korban=r.nama_korban,
            korban_dept_id=r.korban_dept_id,
            status_karyawan=r.status_karyawan,
            jenis_kecelakaan=r.jenis_kecelakaan,
            lokasi_kecelakaan=r.lokasi_kecelakaan,
            deskripsi_kecelakaan=r.deskripsi_kecelakaan,
            penyebab_kecelakaan=r.penyebab_kecelakaan,
            perbaikan_dilakukan=r.perbaikan_dilakukan,
            target_penyelesaian=str(r.target_penyelesaian) if r.target_penyelesaian else None,
            status=r.status or "Open",
            created_by=r.created_by,
            business_unit_id=r.business_unit_id,
            business_unit_name=bu.name if bu else None,
            plant_id=r.plant_id,
            plant_name=plant.name if plant else None,
            updated_by_name=r.updated_by_name,
            created_at=str(r.created_at) if r.created_at else None,
            updated_at=str(r.updated_at) if r.updated_at else None,
            comment_count=_comment_count(db, "case_incident", r.id),
        )
    finally:
        if close_db:
            db.close()


@strawberry.type
class HseDailyType:
    id: int
    tanggal: str
    pekerjaan: str
    pekerja: str
    lokasi_pekerjaan: Optional[str] = None
    status_permit: bool = False
    no_permit: Optional[str] = None
    jenis_pekerjaan: Optional[str] = None
    jenis_pekerjaan_lainnya: Optional[str] = None
    potensi_bahaya: Optional[str] = None
    level_risiko: Optional[str] = None
    pengendalian_bahaya: Optional[str] = None
    pengawas_hse: Optional[str] = None
    saran_masukan: Optional[str] = None
    foto: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    business_unit_id: Optional[int] = None
    business_unit_name: Optional[str] = None
    plant_id: Optional[int] = None
    plant_name: Optional[str] = None
    created_by: Optional[int] = None
    updated_by_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    comment_count: int = 0


@strawberry.type
class HseDailyPayload:
    success: bool
    message: str
    report: Optional[HseDailyType] = None


def _dept_to_type(r: models.Department) -> DepartmentType:
    return DepartmentType(
        id=r.id,
        name=r.name,
        code=r.code or "",
        description=r.description,
        is_active=r.is_active if r.is_active is not None else True,
        created_at=str(r.created_at) if r.created_at else None,
    )


@strawberry.type
class SafetyModuleType:
    id: int
    title: str
    video_url: Optional[str] = None
    media_type: Optional[str] = None
    files: Optional[str] = None  # JSON string
    kategori: Optional[str] = None
    peraturan: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@strawberry.type
class SafetyModulePayload:
    success: bool
    message: str
    module: Optional[SafetyModuleType] = None


def _module_to_type(r: models.SafetyModule) -> SafetyModuleType:
    return SafetyModuleType(
        id=r.id,
        title=r.title,
        video_url=r.video_url,
        media_type=r.media_type or "video",
        files=r.files,
        kategori=r.kategori,
        peraturan=r.peraturan,
        description=r.description,
        created_by=r.created_by,
        created_at=str(r.created_at) if r.created_at else None,
        updated_at=str(r.updated_at) if r.updated_at else None,
    )


def _bu_to_type(r: models.BusinessUnit) -> BusinessUnitType:
    return BusinessUnitType(
        id=r.id,
        name=r.name,
        code=r.code or "",
        description=r.description,
        is_active=r.is_active if r.is_active is not None else True,
        created_at=str(r.created_at) if r.created_at else None,
    )


def _plant_to_type(r: models.Plant) -> PlantType:
    return PlantType(
        id=r.id,
        name=r.name,
        code=r.code or "",
        business_unit_id=r.business_unit_id,
        location=r.location,
        is_active=r.is_active if r.is_active is not None else True,
        created_at=str(r.created_at) if r.created_at else None,
    )


def _user_to_full_type(u: models.User) -> FullUserType:
    return FullUserType(
        id=u.id,
        email=u.email,
        username=u.username,
        full_name=u.full_name,
        role_id=u.role_id,
        business_unit_id=u.business_unit_id,
        plant_id=u.plant_id,
        department_id=u.department_id,
        is_active=u.is_active if u.is_active is not None else True,
        created_at=str(u.created_at) if u.created_at else None,
        updated_at=str(u.updated_at) if u.updated_at else None,
    )


def _comment_count(db: Session, report_type: str, report_id: int) -> int:
    return (
        db.query(models.Comment)
        .filter(models.Comment.report_type == report_type, models.Comment.report_id == report_id)
        .count()
    )


def _tl_count(db: Session, inspection_id: int) -> int:
    return (
        db.query(models.InspectionK3LTindakLanjutHistory)
        .filter(models.InspectionK3LTindakLanjutHistory.inspection_id == inspection_id)
        .count()
    )


def _tl_list(db: Session, inspection_id: int) -> List[InspectionK3LTindakLanjutHistoryType]:
    rows = (
        db.query(models.InspectionK3LTindakLanjutHistory)
        .filter(models.InspectionK3LTindakLanjutHistory.inspection_id == inspection_id)
        .order_by(models.InspectionK3LTindakLanjutHistory.round_number.asc())
        .all()
    )
    return [
        InspectionK3LTindakLanjutHistoryType(
            id=r.id,
            inspection_id=r.inspection_id,
            round_number=r.round_number,
            tindakan_perbaikan=r.tindakan_perbaikan,
            foto_sesudah=r.foto_sesudah,
            ditindaklanjuti_oleh=r.ditindaklanjuti_oleh,
            ditindaklanjuti_department_id=r.ditindaklanjuti_department_id,
            tanggal_tindaklanjuti=str(r.tanggal_tindaklanjuti) if r.tanggal_tindaklanjuti else None,
            created_at=str(r.created_at) if r.created_at else None,
        )
        for r in rows
    ]


def _val_count(db: Session, inspection_id: int) -> int:
    return (
        db.query(models.InspectionK3LValidasiHistory)
        .filter(models.InspectionK3LValidasiHistory.inspection_id == inspection_id)
        .count()
    )


def _val_list(db: Session, inspection_id: int) -> List[InspectionK3LValidasiHistoryType]:
    rows = (
        db.query(models.InspectionK3LValidasiHistory)
        .filter(models.InspectionK3LValidasiHistory.inspection_id == inspection_id)
        .order_by(models.InspectionK3LValidasiHistory.round_number.asc())
        .all()
    )
    return [
        InspectionK3LValidasiHistoryType(
            id=r.id,
            inspection_id=r.inspection_id,
            round_number=r.round_number,
            divalidasi_oleh=r.divalidasi_oleh,
            divalidasi_department_id=r.divalidasi_department_id,
            tanggal_validasi=str(r.tanggal_validasi) if r.tanggal_validasi else None,
            alasan_validasi=r.alasan_validasi,
            status_validasi=r.status_validasi,
            created_at=str(r.created_at) if r.created_at else None,
        )
        for r in rows
    ]


def _model_to_type(record: models.InspectionK3L, db: Optional[Session] = None) -> InspectionK3LType:
    close_db = False
    if db is None:
        db = _get_db()
        close_db = True
    try:
        return InspectionK3LType(
            id=record.id,
            tanggal=str(record.tanggal) if record.tanggal else "",
            kategori_temuan=record.kategori_temuan,
            deskripsi_temuan=record.deskripsi_temuan,
            foto_sebelum=record.foto_sebelum,
            foto_sesudah=record.foto_sesudah,
            lokasi=record.lokasi,
            saran_perbaikan=record.saran_perbaikan,
            tindakan_perbaikan=record.tindakan_perbaikan,
            ditindaklanjuti_oleh=record.ditindaklanjuti_oleh,
            ditindaklanjuti_department_id=record.ditindaklanjuti_department_id,
            tanggal_tindaklanjuti=str(record.tanggal_tindaklanjuti) if record.tanggal_tindaklanjuti else None,
            target_selesai=str(record.target_selesai) if record.target_selesai else None,
            status=record.status or "Open",
            aktual_close=str(record.aktual_close) if record.aktual_close else None,
            created_by=record.created_by,
            business_unit_id=record.business_unit_id,
            plant_id=record.plant_id,
            department_id=record.department_id,
            pelapor_username=record.pelapor_username,
            pelapor_department_id=record.pelapor_department_id,
            jenis_inspeksi=record.jenis_inspeksi,
            tanggal_pelaporan=str(record.tanggal_pelaporan) if record.tanggal_pelaporan else None,
            petugas_inspeksi=record.petugas_inspeksi,
            divalidasi_oleh=record.divalidasi_oleh,
            divalidasi_department_id=record.divalidasi_department_id,
            tanggal_validasi=str(record.tanggal_validasi) if record.tanggal_validasi else None,
            alasan_validasi=record.alasan_validasi,
            status_validasi=record.status_validasi,
            tindak_lanjut_count=_tl_count(db, record.id),
            tindak_lanjut_list=_tl_list(db, record.id),
            validasi_count=_val_count(db, record.id),
            validasi_list=_val_list(db, record.id),
            updated_by_name=record.updated_by_name,
            created_at=str(record.created_at) if record.created_at else None,
            updated_at=str(record.updated_at) if record.updated_at else None,
            comment_count=_comment_count(db, "inspection_k3l", record.id),
        )
    finally:
        if close_db:
            db.close()


def _hse_daily_to_type(r: models.HseDailyReport, db=None) -> HseDailyType:
    close_db = False
    if db is None:
        db = _get_db()
        close_db = True
    try:
        dept = db.query(models.Department).filter(models.Department.id == r.department_id).first() if r.department_id else None
        bu = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == r.business_unit_id).first() if r.business_unit_id else None
        plant = db.query(models.Plant).filter(models.Plant.id == r.plant_id).first() if r.plant_id else None
        return HseDailyType(
            id=r.id,
            tanggal=str(r.tanggal) if r.tanggal else "",
            pekerjaan=r.pekerjaan,
            pekerja=r.pekerja,
            lokasi_pekerjaan=r.lokasi_pekerjaan,
            status_permit=r.status_permit or False,
            no_permit=r.no_permit,
            jenis_pekerjaan=r.jenis_pekerjaan,
            jenis_pekerjaan_lainnya=r.jenis_pekerjaan_lainnya,
            potensi_bahaya=r.potensi_bahaya,
            level_risiko=r.level_risiko,
            pengendalian_bahaya=r.pengendalian_bahaya,
            pengawas_hse=r.pengawas_hse,
            saran_masukan=r.saran_masukan,
            foto=r.foto,
            department_id=r.department_id,
            department_name=dept.name if dept else None,
            business_unit_id=r.business_unit_id,
            business_unit_name=bu.name if bu else None,
            plant_id=r.plant_id,
            plant_name=plant.name if plant else None,
            created_by=r.created_by,
            updated_by_name=r.updated_by_name,
            created_at=str(r.created_at) if r.created_at else None,
            updated_at=str(r.updated_at) if r.updated_at else None,
            comment_count=_comment_count(db, "hse_daily", r.id),
        )
    finally:
        if close_db:
            db.close()


@strawberry.type
class CommentType:
    id: int
    report_type: str
    report_id: int
    user_id: int
    user_email: Optional[str] = None
    user_full_name: Optional[str] = None
    user_username: Optional[str] = None
    content: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    can_edit: bool = False
    can_delete: bool = False


@strawberry.type
class CommentPayload:
    success: bool
    message: str
    comment: Optional[CommentType] = None


_VALID_REPORT_TYPES = ("inspection_k3l", "hse_daily", "case_incident")


def _comment_to_type(c: models.Comment, db: Session, current_user: models.User) -> CommentType:
    author = db.query(models.User).filter(models.User.id == c.user_id).first()
    is_admin = current_user.role_id == 1
    is_author = current_user.id == c.user_id
    return CommentType(
        id=c.id,
        report_type=c.report_type,
        report_id=c.report_id,
        user_id=c.user_id,
        user_email=author.email if author else None,
        user_full_name=author.full_name if author else None,
        user_username=author.username if author else None,
        content=c.content,
        created_at=str(c.created_at) if c.created_at else None,
        updated_at=str(c.updated_at) if c.updated_at else None,
        can_edit=is_author,
        can_delete=is_author or is_admin,
    )


def _can_access_report(db: Session, user: models.User, report_type: str, report_id: int) -> bool:
    """Check whether the user can view the target report (mirrors list visibility rules)."""
    if report_type == "inspection_k3l":
        record = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == report_id).first()
    elif report_type == "hse_daily":
        record = db.query(models.HseDailyReport).filter(models.HseDailyReport.id == report_id).first()
    elif report_type == "case_incident":
        record = db.query(models.CaseIncident).filter(models.CaseIncident.id == report_id).first()
    else:
        return False
    if not record:
        return False
    if _is_staff(user):
        if record.business_unit_id != user.business_unit_id or record.plant_id != user.plant_id:
            return False
    return True


# ── Chat types & helpers ─────────────────────────────────────────────────

@strawberry.type
class ChatMessageType:
    id: int
    sender_id: int
    recipient_id: int
    content: str
    attachment_url: Optional[str] = None
    attachment_type: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    read_at: Optional[str] = None
    sender_full_name: Optional[str] = None
    sender_email: Optional[str] = None
    sender_username: Optional[str] = None


@strawberry.type
class ChatMessagePayload:
    success: bool
    message: str
    chat_message: Optional[ChatMessageType] = None


@strawberry.type
class ChatUserSummaryType:
    id: int
    email: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    role_level: Optional[int] = None
    business_unit_id: Optional[int] = None
    business_unit_name: Optional[str] = None
    plant_id: Optional[int] = None
    plant_name: Optional[str] = None
    is_active: bool = True
    last_message_content: Optional[str] = None
    last_message_at: Optional[str] = None
    last_message_from_me: bool = False
    unread_count: int = 0


def _chat_msg_to_type(m: models.ChatMessage, sender: Optional[models.User] = None) -> ChatMessageType:
    return ChatMessageType(
        id=m.id,
        sender_id=m.sender_id,
        recipient_id=m.recipient_id,
        content=m.content or "",
        attachment_url=m.attachment_url,
        attachment_type=m.attachment_type,
        created_at=str(m.created_at) if m.created_at else None,
        updated_at=str(m.updated_at) if m.updated_at else None,
        read_at=str(m.read_at) if m.read_at else None,
        sender_full_name=sender.full_name if sender else None,
        sender_email=sender.email if sender else None,
        sender_username=sender.username if sender else None,
    )


def _can_chat_pair(db: Session, a: models.User, b: models.User) -> bool:
    """Allow chat if at least one side has admin-tier reach, otherwise require same BU+plant."""
    if a.id == b.id:
        return False
    if not _is_staff(a) or not _is_staff(b):
        return True
    return (
        a.business_unit_id == b.business_unit_id
        and a.plant_id == b.plant_id
        and a.business_unit_id is not None
        and a.plant_id is not None
    )


def _contactable_users_query(db: Session, user: models.User):
    """Query users that `user` is permitted to chat with."""
    q = db.query(models.User).filter(
        models.User.id != user.id,
        models.User.is_active == True,  # noqa: E712
    )
    if _is_staff(user):
        # staff can see: same BU+plant peers, plus any admin-tier user (role.level < 6)
        admin_role_ids = db.query(models.Role.id).filter(models.Role.level < 6).subquery()
        q = q.filter(
            or_(
                and_(
                    models.User.business_unit_id == user.business_unit_id,
                    models.User.plant_id == user.plant_id,
                ),
                models.User.role_id.in_(admin_role_ids),
            )
        )
    return q


@strawberry.type
class NotificationType:
    id: int
    type: str
    title: str
    message: Optional[str] = None
    link: Optional[str] = None
    is_read: bool = False
    created_at: Optional[str] = None


@strawberry.type
class NotificationPayload:
    success: bool
    message: str


def _notify_users(db, user_ids: list[int], notif_type: str, title: str, message: str, link: str, exclude_id: int = 0) -> None:
    from datetime import datetime as _dt
    now = _dt.utcnow()
    for uid in user_ids:
        if uid == exclude_id:
            continue
        record = models.Notification(
            user_id=uid,
            type=notif_type,
            title=title,
            message=message,
            link=link,
            created_at=now,
        )
        db.add(record)
        db.flush()  # Assigns real DB id within the transaction
        payload = NotificationType(
            id=record.id,
            type=notif_type,
            title=title,
            message=message,
            link=link,
            is_read=False,
            created_at=str(now),
        )
        notif_broker.publish(uid, payload)
        # Also deliver a native browser/OS push (works when the app is closed).
        web_push.push_to_user(uid, title=title, body=message, url=link or "/", tag=notif_type)


@strawberry.type
class Query:
    @strawberry.field
    def me(self, info: strawberry.types.Info) -> Optional[UserType]:
        user = _get_current_user(info)
        if not user:
            return None
        return UserType(id=user.id, email=user.email, role=user.role, business_unit=user.business_unit)

    @strawberry.field
    def inspection_k3l_list(self, info: strawberry.types.Info) -> List[InspectionK3LType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            query = db.query(models.InspectionK3L)
            if _is_staff(user):
                query = query.filter(
                    models.InspectionK3L.business_unit_id == user.business_unit_id,
                    models.InspectionK3L.plant_id == user.plant_id,
                )
            records = query.order_by(models.InspectionK3L.created_at.desc()).all()
            return [_model_to_type(r) for r in records]
        finally:
            db.close()

    @strawberry.field
    def inspection_k3l_by_id(self, info: strawberry.types.Info, id: int) -> Optional[InspectionK3LType]:
        user = _get_current_user(info)
        if not user:
            return None
        db = _get_db()
        try:
            record = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == id).first()
            if not record:
                return None
            if _is_staff(user) and (
                record.business_unit_id != user.business_unit_id
                or record.plant_id != user.plant_id
            ):
                return None
            return _model_to_type(record)
        finally:
            db.close()

    @strawberry.field
    def business_units(self, info: strawberry.types.Info) -> List[BusinessUnitType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            records = db.query(models.BusinessUnit).order_by(models.BusinessUnit.name.asc()).all()
            return [_bu_to_type(r) for r in records]
        finally:
            db.close()

    @strawberry.field
    def roles(self, info: strawberry.types.Info) -> List[RoleType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            records = db.query(models.Role).order_by(models.Role.level.asc()).all()
            return [RoleType(id=r.id, name=r.name, level=r.level, description=r.description) for r in records]
        finally:
            db.close()

    @strawberry.field
    def users(self, info: strawberry.types.Info) -> List[FullUserType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            records = db.query(models.User).order_by(models.User.created_at.desc()).all()
            return [_user_to_full_type(r) for r in records]
        finally:
            db.close()

    @strawberry.field
    def departments(self, info: strawberry.types.Info) -> List[DepartmentType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            records = db.query(models.Department).order_by(models.Department.name.asc()).all()
            return [_dept_to_type(r) for r in records]
        finally:
            db.close()

    @strawberry.field
    def plants(self, info: strawberry.types.Info, business_unit_id: Optional[int] = None) -> List[PlantType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            query = db.query(models.Plant)
            if business_unit_id is not None:
                query = query.filter(models.Plant.business_unit_id == business_unit_id)
            records = query.order_by(models.Plant.name.asc()).all()
            return [_plant_to_type(r) for r in records]
        finally:
            db.close()

    @strawberry.field
    def safety_modules(self, info: strawberry.types.Info) -> List[SafetyModuleType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            records = db.query(models.SafetyModule).order_by(models.SafetyModule.created_at.desc()).all()
            return [_module_to_type(r) for r in records]
        finally:
            db.close()

    @strawberry.field
    def safety_module_by_id(self, info: strawberry.types.Info, id: int) -> Optional[SafetyModuleType]:
        user = _get_current_user(info)
        if not user:
            return None
        db = _get_db()
        try:
            record = db.query(models.SafetyModule).filter(models.SafetyModule.id == id).first()
            return _module_to_type(record) if record else None
        finally:
            db.close()

    @strawberry.field
    def hse_daily_list(self, info: strawberry.types.Info) -> List[HseDailyType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            records = db.query(models.HseDailyReport).order_by(models.HseDailyReport.created_at.desc()).all()
            return [_hse_daily_to_type(r, db) for r in records]
        finally:
            db.close()

    @strawberry.field
    def hse_daily_by_id(self, info: strawberry.types.Info, id: int) -> Optional[HseDailyType]:
        user = _get_current_user(info)
        if not user:
            return None
        db = _get_db()
        try:
            record = db.query(models.HseDailyReport).filter(models.HseDailyReport.id == id).first()
            return _hse_daily_to_type(record, db) if record else None
        finally:
            db.close()

    @strawberry.field
    def comments(self, info: strawberry.types.Info, report_type: str, report_id: int) -> List[CommentType]:
        user = _get_current_user(info)
        if not user:
            return []
        if report_type not in _VALID_REPORT_TYPES:
            return []
        db = _get_db()
        try:
            if not _can_access_report(db, user, report_type, report_id):
                return []
            records = (
                db.query(models.Comment)
                .filter(
                    models.Comment.report_type == report_type,
                    models.Comment.report_id == report_id,
                )
                .order_by(models.Comment.created_at.asc())
                .all()
            )
            return [_comment_to_type(c, db, user) for c in records]
        finally:
            db.close()

    @strawberry.field
    def chat_users(self, info: strawberry.types.Info) -> List[ChatUserSummaryType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            users = _contactable_users_query(db, user).all()
            # Bulk-fetch related lookups
            role_map = {r.id: r for r in db.query(models.Role).all()}
            bu_map = {b.id: b for b in db.query(models.BusinessUnit).all()}
            plant_map = {p.id: p for p in db.query(models.Plant).all()}

            other_ids = [u.id for u in users]
            if not other_ids:
                return []

            # Last message per peer (within this user's conversations)
            last_msgs: dict[int, models.ChatMessage] = {}
            msgs = (
                db.query(models.ChatMessage)
                .filter(
                    or_(
                        and_(models.ChatMessage.sender_id == user.id, models.ChatMessage.recipient_id.in_(other_ids)),
                        and_(models.ChatMessage.recipient_id == user.id, models.ChatMessage.sender_id.in_(other_ids)),
                    )
                )
                .order_by(models.ChatMessage.created_at.desc())
                .all()
            )
            for m in msgs:
                peer = m.recipient_id if m.sender_id == user.id else m.sender_id
                if peer not in last_msgs:
                    last_msgs[peer] = m

            # Unread counts (messages sent to me, not yet read)
            unread_rows = (
                db.query(
                    models.ChatMessage.sender_id,
                    sa_func.count(models.ChatMessage.id),
                )
                .filter(
                    models.ChatMessage.recipient_id == user.id,
                    models.ChatMessage.read_at.is_(None),
                    models.ChatMessage.sender_id.in_(other_ids),
                )
                .group_by(models.ChatMessage.sender_id)
                .all()
            )
            unread_map = {sid: cnt for sid, cnt in unread_rows}

            summaries: list[ChatUserSummaryType] = []
            for u in users:
                role = role_map.get(u.role_id) if u.role_id else None
                bu = bu_map.get(u.business_unit_id) if u.business_unit_id else None
                pl = plant_map.get(u.plant_id) if u.plant_id else None
                last = last_msgs.get(u.id)
                summaries.append(
                    ChatUserSummaryType(
                        id=u.id,
                        email=u.email,
                        full_name=u.full_name,
                        username=u.username,
                        role_id=u.role_id,
                        role_name=role.name if role else None,
                        role_level=role.level if role else None,
                        business_unit_id=u.business_unit_id,
                        business_unit_name=bu.name if bu else None,
                        plant_id=u.plant_id,
                        plant_name=pl.name if pl else None,
                        is_active=u.is_active if u.is_active is not None else True,
                        last_message_content=last.content if last else None,
                        last_message_at=str(last.created_at) if last and last.created_at else None,
                        last_message_from_me=bool(last and last.sender_id == user.id),
                        unread_count=int(unread_map.get(u.id, 0)),
                    )
                )

            # Sort: unread first, then most recent message, then name
            summaries.sort(key=lambda s: (-s.unread_count, -_safe_ts(s.last_message_at), (s.full_name or s.email or "").lower()))
            return summaries
        finally:
            db.close()

    @strawberry.field
    def chat_messages(
        self,
        info: strawberry.types.Info,
        other_user_id: int,
        limit: Optional[int] = 100,
        before_id: Optional[int] = None,
    ) -> List[ChatMessageType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            other = db.query(models.User).filter(models.User.id == other_user_id).first()
            if not other or not _can_chat_pair(db, user, other):
                return []
            q = db.query(models.ChatMessage).filter(
                or_(
                    and_(models.ChatMessage.sender_id == user.id, models.ChatMessage.recipient_id == other_user_id),
                    and_(models.ChatMessage.sender_id == other_user_id, models.ChatMessage.recipient_id == user.id),
                )
            )
            if before_id is not None:
                q = q.filter(models.ChatMessage.id < before_id)
            rows = q.order_by(models.ChatMessage.id.desc()).limit(min(max(limit or 100, 1), 500)).all()
            rows.reverse()  # oldest first for the UI
            sender_ids = {r.sender_id for r in rows}
            sender_map = {u.id: u for u in db.query(models.User).filter(models.User.id.in_(sender_ids)).all()} if sender_ids else {}
            return [_chat_msg_to_type(m, sender_map.get(m.sender_id)) for m in rows]
        finally:
            db.close()

    @strawberry.field
    def my_notifications(self, info: strawberry.types.Info) -> List[NotificationType]:
        user = _get_current_user(info)
        if not user:
            return []
        db = _get_db()
        try:
            rows = (
                db.query(models.Notification)
                .filter(models.Notification.user_id == user.id)
                .order_by(models.Notification.created_at.desc())
                .limit(50)
                .all()
            )
            return [
                NotificationType(
                    id=r.id,
                    type=r.type,
                    title=r.title,
                    message=r.message,
                    link=r.link,
                    is_read=bool(r.is_read),
                    created_at=str(r.created_at) if r.created_at else None,
                )
                for r in rows
            ]
        finally:
            db.close()

    @strawberry.field
    def push_public_key(self, info: strawberry.types.Info) -> str:
        """VAPID public (application server) key for the browser to subscribe with."""
        return web_push.PUBLIC_KEY

    @strawberry.field
    def case_incident_list(self, info: strawberry.types.Info) -> List[CaseIncidentType]:
        user = _get_current_user(info)
        if not user:
            raise Exception("Authentication required")
        db = _get_db()
        try:
            records = db.query(models.CaseIncident).order_by(models.CaseIncident.tanggal_kejadian.desc()).all()
            return [_ci_to_type(r, db) for r in records]
        finally:
            db.close()

    @strawberry.field
    def case_incident_by_id(self, info: strawberry.types.Info, id: int) -> Optional[CaseIncidentType]:
        user = _get_current_user(info)
        if not user:
            raise Exception("Authentication required")
        db = _get_db()
        try:
            r = db.query(models.CaseIncident).filter(models.CaseIncident.id == id).first()
            return _ci_to_type(r) if r else None
        finally:
            db.close()


def _safe_ts(s: Optional[str]) -> float:
    if not s:
        return 0.0
    try:
        return datetime.fromisoformat(s.replace(" ", "T")).timestamp()
    except Exception:
        return 0.0


def _delete_module_files(files_json: str | None) -> None:
    """Delete all Cloudinary assets for a safety module."""
    import json
    if not files_json:
        return
    try:
        files = json.loads(files_json)
    except Exception:
        return
    for f in files:
        url = f.get("url") if isinstance(f, dict) else None
        if not url:
            continue
        media_type = (f.get("mediaType") or "").lower() if isinstance(f, dict) else ""
        try:
            if media_type == "video":
                delete_video(url)
            elif media_type == "image":
                delete_image(url)
            else:
                delete_document(url)
        except Exception:
            pass


@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, email: str, password: str) -> AuthPayload:
        if not email.endswith("@cp.co.id"):
            return AuthPayload(success=False, message="Email must be a @cp.co.id address")
        if len(password) < 6:
            return AuthPayload(success=False, message="Password must be at least 6 characters")

        db = _get_db()
        try:
            if db.query(models.User).filter(models.User.email == email).first():
                return AuthPayload(success=False, message="Email already registered")

            user = models.User(
                email=email,
                hashed_password=auth.hash_password(password),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            token = auth.create_token(email)
            role_name = db.query(models.Role).filter(models.Role.id == user.role_id).first()
            bu_name = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == user.business_unit_id).first()
            plant_rec = db.query(models.Plant).filter(models.Plant.id == user.plant_id).first()
            dept_rec = db.query(models.Department).filter(models.Department.id == user.department_id).first()
            return AuthPayload(
                success=True,
                message="Registration successful",
                token=token,
                user=UserType(
                    id=user.id, email=user.email,
                    role=role_name.name if role_name else "",
                    business_unit=bu_name.name if bu_name else "",
                    plant=plant_rec.name if plant_rec else None,
                    full_name=user.full_name,
                    username=user.username,
                    role_id=user.role_id,
                    role_level=role_name.level if role_name else None,
                    business_unit_id=user.business_unit_id,
                    plant_id=user.plant_id,
                    department_id=user.department_id,
                    department=dept_rec.name if dept_rec else None,
                ),
            )
        except Exception as e:
            db.rollback()
            return AuthPayload(success=False, message=f"Registration failed: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def login(self, identifier: str, password: str) -> AuthPayload:
        db = _get_db()
        try:
            if "@" in identifier:
                user = db.query(models.User).filter(models.User.email == identifier).first()
            else:
                user = db.query(models.User).filter(models.User.username == identifier).first()
            if not user:
                return AuthPayload(success=False, message="User not found. Please register first")
            if not auth.verify_password(password, user.hashed_password):
                return AuthPayload(success=False, message="Invalid password")

            token = auth.create_token(user.email)
            role_name = db.query(models.Role).filter(models.Role.id == user.role_id).first()
            bu_name = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == user.business_unit_id).first()
            plant_rec = db.query(models.Plant).filter(models.Plant.id == user.plant_id).first()
            dept_rec = db.query(models.Department).filter(models.Department.id == user.department_id).first()
            return AuthPayload(
                success=True,
                message="Login successful",
                token=token,
                user=UserType(
                    id=user.id, email=user.email,
                    role=role_name.name if role_name else "",
                    business_unit=bu_name.name if bu_name else "",
                    plant=plant_rec.name if plant_rec else None,
                    full_name=user.full_name,
                    username=user.username,
                    role_id=user.role_id,
                    role_level=role_name.level if role_name else None,
                    business_unit_id=user.business_unit_id,
                    plant_id=user.plant_id,
                    department_id=user.department_id,
                    department=dept_rec.name if dept_rec else None,
                ),
            )
        finally:
            db.close()

    @strawberry.mutation
    def change_password(self, info: strawberry.types.Info, current_password: str, new_password: str) -> GenericPayload:
        user = _get_current_user(info)
        if not user:
            return GenericPayload(success=False, message="Authentication required")

        if len(new_password) < 6:
            return GenericPayload(success=False, message="Password must be at least 6 characters")

        if not auth.verify_password(current_password, user.hashed_password):
            return GenericPayload(success=False, message="Current password is incorrect")

        db = _get_db()
        try:
            record = db.query(models.User).filter(models.User.id == user.id).first()
            if not record:
                return GenericPayload(success=False, message="User not found")

            record.hashed_password = auth.hash_password(new_password)
            db.commit()
            return GenericPayload(success=True, message="Password berhasil diubah")
        except Exception as e:
            db.rollback()
            return GenericPayload(success=False, message=f"Failed to update password: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def create_inspection_k3l(
        self,
        info: strawberry.types.Info,
        tanggal: str,
        kategori_temuan: str,
        deskripsi_temuan: Optional[str] = None,
        foto_sebelum: Optional[str] = None,
        foto_sesudah: Optional[str] = None,
        lokasi: Optional[str] = None,
        tindakan_perbaikan: Optional[str] = None,
        target_selesai: Optional[str] = None,
        status: Optional[str] = "Open",
        aktual_close: Optional[str] = None,
        business_unit_id: Optional[int] = None,
        plant_id: Optional[int] = None,
        department_id: Optional[int] = None,
        jenis_inspeksi: Optional[str] = None,
        petugas_inspeksi: Optional[str] = None,
    ) -> InspectionK3LPayload:
        user = _get_current_user(info)
        if not user:
            return InspectionK3LPayload(success=False, message="Authentication required")

        if status and status not in ("Open", "Closed", "Progress Validasi"):
            return InspectionK3LPayload(success=False, message="Status tidak valid")

        db = _get_db()
        try:
            if not _is_privileged(user) and not _is_safety_department(db, user):
                return InspectionK3LPayload(success=False, message="Hanya departemen Safety yang dapat menambahkan temuan")
            if business_unit_id is not None:
                business_unit = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == business_unit_id).first()
                if not business_unit:
                    return InspectionK3LPayload(success=False, message="Business unit not found")
            if plant_id is not None:
                plant = db.query(models.Plant).filter(models.Plant.id == plant_id).first()
                if not plant:
                    return InspectionK3LPayload(success=False, message="Plant not found")
                if business_unit_id is not None and plant.business_unit_id != business_unit_id:
                    return InspectionK3LPayload(success=False, message="Plant does not belong to selected business unit")

            from datetime import timezone, timedelta
            wib_now = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
            record = models.InspectionK3L(
                tanggal=datetime.fromisoformat(tanggal),
                kategori_temuan=kategori_temuan,
                deskripsi_temuan=deskripsi_temuan,
                foto_sebelum=foto_sebelum,
                foto_sesudah=foto_sesudah,
                lokasi=lokasi,
                saran_perbaikan=tindakan_perbaikan,
                target_selesai=date.fromisoformat(target_selesai) if target_selesai else None,
                status=status or "Open",
                aktual_close=datetime.fromisoformat(aktual_close) if aktual_close else None,
                created_by=user.id,
                updated_by_name=user.full_name or user.username or user.email,
                pelapor_username=user.full_name or user.username or user.email,
                pelapor_department_id=user.department_id,
                business_unit_id=business_unit_id,
                plant_id=plant_id,
                department_id=department_id,
                jenis_inspeksi=jenis_inspeksi,
                tanggal_pelaporan=wib_now,
                petugas_inspeksi=petugas_inspeksi,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            try:
                all_user_ids = [u.id for u in db.query(models.User.id).filter(models.User.is_active == True).all()]
                submitter = user.full_name or user.username or user.email
                _notify_users(db, all_user_ids, "new_report", "Laporan K3L Baru", f"Laporan Inspeksi K3L baru telah dibuat oleh {submitter}.", "/dashboard/reports/inspection-k3l", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return InspectionK3LPayload(
                success=True,
                message="Inspection K3L created successfully",
                inspection=_model_to_type(record),
            )
        except Exception as e:
            db.rollback()
            return InspectionK3LPayload(success=False, message=f"Failed to create: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_inspection_k3l(
        self,
        info: strawberry.types.Info,
        id: int,
        tanggal: Optional[str] = None,
        kategori_temuan: Optional[str] = None,
        deskripsi_temuan: Optional[str] = None,
        foto_sebelum: Optional[str] = None,
        foto_sesudah: Optional[str] = None,
        lokasi: Optional[str] = None,
        tindakan_perbaikan: Optional[str] = None,
        target_selesai: Optional[str] = None,
        status: Optional[str] = None,
        aktual_close: Optional[str] = None,
        business_unit_id: Optional[int] = None,
        plant_id: Optional[int] = None,
        department_id: Optional[int] = None,
        jenis_inspeksi: Optional[str] = None,
        petugas_inspeksi: Optional[str] = None,
    ) -> InspectionK3LPayload:
        user = _get_current_user(info)
        if not user:
            return InspectionK3LPayload(success=False, message="Authentication required")

        db = _get_db()
        try:
            record = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == id).first()
            if not record:
                return InspectionK3LPayload(success=False, message="Record not found")

            if not _is_privileged(user) and not _is_safety_department(db, user):
                return InspectionK3LPayload(success=False, message="Hanya departemen Safety yang dapat mengubah temuan")

            if _is_staff(user) and (
                record.business_unit_id != user.business_unit_id
                or record.plant_id != user.plant_id
            ):
                return InspectionK3LPayload(success=False, message="Access denied")

            next_business_unit_id = business_unit_id if business_unit_id is not None else record.business_unit_id
            next_plant_id = plant_id if plant_id is not None else record.plant_id
            if next_business_unit_id is not None:
                business_unit = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == next_business_unit_id).first()
                if not business_unit:
                    return InspectionK3LPayload(success=False, message="Business unit not found")
            if next_plant_id is not None:
                plant = db.query(models.Plant).filter(models.Plant.id == next_plant_id).first()
                if not plant:
                    return InspectionK3LPayload(success=False, message="Plant not found")
                if next_business_unit_id is not None and plant.business_unit_id != next_business_unit_id:
                    return InspectionK3LPayload(success=False, message="Plant does not belong to selected business unit")

            if tanggal is not None:
                record.tanggal = datetime.fromisoformat(tanggal)
            if kategori_temuan is not None:
                record.kategori_temuan = kategori_temuan
            if deskripsi_temuan is not None:
                record.deskripsi_temuan = deskripsi_temuan
            if foto_sebelum is not None:
                record.foto_sebelum = foto_sebelum
            if foto_sesudah is not None:
                record.foto_sesudah = foto_sesudah
            if lokasi is not None:
                record.lokasi = lokasi
            if tindakan_perbaikan is not None:
                record.saran_perbaikan = tindakan_perbaikan
            if target_selesai is not None:
                record.target_selesai = date.fromisoformat(target_selesai)
            reopened = False
            if status is not None:
                if status not in ("Open", "Closed", "Progress Validasi"):
                    return InspectionK3LPayload(success=False, message="Status must be Open, Progress Validasi, or Closed")
                reopened = record.status in ("Closed", "Progress Validasi") and status == "Open"
                record.status = status
            if aktual_close is not None:
                record.aktual_close = datetime.fromisoformat(aktual_close)
            if business_unit_id is not None:
                record.business_unit_id = business_unit_id
            if plant_id is not None:
                record.plant_id = plant_id
            if department_id is not None:
                record.department_id = department_id
            if jenis_inspeksi is not None:
                record.jenis_inspeksi = jenis_inspeksi
            if petugas_inspeksi is not None:
                record.petugas_inspeksi = petugas_inspeksi

            # Record whoever last edited the data
            record.updated_by_name = user.full_name or user.username or user.email

            db.commit()
            db.refresh(record)
            try:
                actor = user.full_name or user.username or user.email
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                if reopened:
                    _notify_users(db, level3_ids, "reopen_report", "Temuan K3L Dibuka Kembali", f"Temuan Inspeksi K3L telah dibuka kembali (status Open) oleh {actor}.", "/dashboard/reports/inspection-k3l", exclude_id=user.id)
                else:
                    _notify_users(db, level3_ids, "update_report", "Laporan K3L Diperbarui", f"Laporan Inspeksi K3L telah diperbarui oleh {actor}.", "/dashboard/reports/inspection-k3l", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return InspectionK3LPayload(
                success=True,
                message="Inspection K3L updated successfully",
                inspection=_model_to_type(record),
            )
        except Exception as e:
            db.rollback()
            return InspectionK3LPayload(success=False, message=f"Failed to update: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def tindak_lanjut_inspection_k3l(
        self,
        info: strawberry.types.Info,
        id: int,
        tindakan_perbaikan: Optional[str] = None,
        foto_sesudah: Optional[str] = None,
        ditindaklanjuti_department_id: Optional[int] = None,
    ) -> InspectionK3LPayload:
        user = _get_current_user(info)
        if not user:
            return InspectionK3LPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == id).first()
            if not record:
                return InspectionK3LPayload(success=False, message="Record not found")
            if not _is_privileged(user) and (not record.department_id or user.department_id != record.department_id):
                return InspectionK3LPayload(success=False, message="Hanya departemen yang dipilih pada temuan ini yang dapat melakukan tindak lanjut")
            existing_count = _tl_count(db, id)
            if existing_count >= 4:
                return InspectionK3LPayload(success=False, message="Maksimal 4 kali tindak lanjut")
            from datetime import timezone, timedelta
            wib = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
            actor = user.full_name or user.username or user.email
            dept_id = ditindaklanjuti_department_id or user.department_id
            history = models.InspectionK3LTindakLanjutHistory(
                inspection_id=id,
                round_number=existing_count + 1,
                tindakan_perbaikan=tindakan_perbaikan,
                foto_sesudah=foto_sesudah,
                ditindaklanjuti_oleh=actor,
                ditindaklanjuti_department_id=dept_id,
                tanggal_tindaklanjuti=wib,
            )
            db.add(history)
            # mirror onto main record; accumulate all foto_sesudah across rounds
            record.tindakan_perbaikan = tindakan_perbaikan
            if foto_sesudah is not None:
                try:
                    existing = json.loads(record.foto_sesudah or '[]')
                    if not isinstance(existing, list):
                        existing = [record.foto_sesudah] if record.foto_sesudah else []
                except Exception:
                    existing = [record.foto_sesudah] if record.foto_sesudah else []
                try:
                    new_photos = json.loads(foto_sesudah)
                    if not isinstance(new_photos, list):
                        new_photos = [foto_sesudah]
                except Exception:
                    new_photos = [foto_sesudah]
                seen = set(existing)
                combined = existing + [u for u in new_photos if u not in seen]
                record.foto_sesudah = json.dumps(combined)
            record.ditindaklanjuti_oleh = actor
            record.ditindaklanjuti_department_id = dept_id
            record.tanggal_tindaklanjuti = wib
            record.status = "Progress Validasi"
            db.commit()
            db.refresh(record)
            return InspectionK3LPayload(success=True, message="Tindak lanjut berhasil disimpan", inspection=_model_to_type(record, db))
        except Exception as e:
            db.rollback()
            return InspectionK3LPayload(success=False, message=f"Failed: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def validasi_inspection_k3l(
        self,
        info: strawberry.types.Info,
        id: int,
        alasan_validasi: Optional[str] = None,
        status_validasi: Optional[str] = None,
        divalidasi_department_id: Optional[int] = None,
        aktual_close: Optional[str] = None,
    ) -> InspectionK3LPayload:
        user = _get_current_user(info)
        if not user:
            return InspectionK3LPayload(success=False, message="Authentication required")
        if status_validasi not in ("Closed", "Open"):
            return InspectionK3LPayload(success=False, message="Status validasi harus Closed atau Open")
        db = _get_db()
        try:
            record = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == id).first()
            if not record:
                return InspectionK3LPayload(success=False, message="Record not found")
            if not _is_privileged(user) and not _is_safety_department(db, user):
                return InspectionK3LPayload(success=False, message="Hanya departemen Safety yang dapat melakukan validasi")
            existing_count = _val_count(db, id)
            if existing_count >= 4:
                return InspectionK3LPayload(success=False, message="Maksimal 4 ronde validasi")
            if alasan_validasi is not None:
                record.alasan_validasi = alasan_validasi
            record.status_validasi = status_validasi
            record.divalidasi_oleh = user.full_name or user.username or user.email
            record.divalidasi_department_id = divalidasi_department_id or user.department_id
            from datetime import timezone, timedelta
            wib = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
            record.tanggal_validasi = wib
            record.status = "Closed" if status_validasi == "Closed" else "Open"
            if status_validasi == "Closed":
                record.aktual_close = datetime.fromisoformat(aktual_close) if aktual_close else wib
            history = models.InspectionK3LValidasiHistory(
                inspection_id=id,
                round_number=existing_count + 1,
                divalidasi_oleh=record.divalidasi_oleh,
                divalidasi_department_id=record.divalidasi_department_id,
                tanggal_validasi=wib,
                alasan_validasi=record.alasan_validasi,
                status_validasi=status_validasi,
            )
            db.add(history)
            db.commit()
            db.refresh(record)
            return InspectionK3LPayload(success=True, message="Validasi berhasil disimpan", inspection=_model_to_type(record))
        except Exception as e:
            db.rollback()
            return InspectionK3LPayload(success=False, message=f"Failed: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_inspection_k3l(self, info: strawberry.types.Info, id: int) -> InspectionK3LPayload:
        user = _get_current_user(info)
        if not user:
            return InspectionK3LPayload(success=False, message="Authentication required")

        db = _get_db()
        try:
            record = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == id).first()
            if not record:
                return InspectionK3LPayload(success=False, message="Record not found")

            if not _is_privileged(user) and not _is_safety_department(db, user):
                return InspectionK3LPayload(success=False, message="Hanya departemen Safety yang dapat menghapus temuan")

            if _is_staff(user) and (
                record.business_unit_id != user.business_unit_id
                or record.plant_id != user.plant_id
            ):
                return InspectionK3LPayload(success=False, message="Access denied")

            # Collect all Cloudinary URLs before deleting the DB record
            photo_urls = []
            for field in (record.foto_sebelum, record.foto_sesudah):
                if field:
                    try:
                        parsed = json.loads(field)
                        if isinstance(parsed, list):
                            photo_urls.extend(parsed)
                        else:
                            photo_urls.append(field)
                    except (json.JSONDecodeError, TypeError):
                        photo_urls.append(field)

            label = record.deskripsi_temuan or record.kategori_temuan
            db.delete(record)
            db.commit()

            # Delete from Cloudinary after successful DB delete (best-effort)
            for url in photo_urls:
                try:
                    delete_image(url)
                except Exception:
                    pass

            try:
                actor = user.full_name or user.username or user.email
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                _notify_users(db, level3_ids, "delete_report", "Laporan K3L Dihapus", f"Laporan Inspeksi K3L telah dihapus oleh {actor}.", "/dashboard/reports/inspection-k3l", exclude_id=user.id)
                db.commit()
            except Exception:
                pass

            return InspectionK3LPayload(success=True, message="Inspection K3L deleted successfully")
        except Exception as e:
            db.rollback()
            return InspectionK3LPayload(success=False, message=f"Failed to delete: {str(e)}")
        finally:
            db.close()


    # ── Business Unit mutations ──────────────────────────────────────────

    @strawberry.mutation
    def create_business_unit(
        self,
        info: strawberry.types.Info,
        name: str,
        code: str,
        description: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> BusinessUnitPayload:
        user = _get_current_user(info)
        if not user:
            return BusinessUnitPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            if db.query(models.BusinessUnit).filter(models.BusinessUnit.name == name).first():
                return BusinessUnitPayload(success=False, message="Business unit name already exists")
            if db.query(models.BusinessUnit).filter(models.BusinessUnit.code == code).first():
                return BusinessUnitPayload(success=False, message="Business unit code already exists")
            record = models.BusinessUnit(
                name=name, code=code, description=description,
                is_active=is_active if is_active is not None else True,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return BusinessUnitPayload(success=True, message="Business unit created", business_unit=_bu_to_type(record))
        except Exception as e:
            db.rollback()
            return BusinessUnitPayload(success=False, message=f"Failed to create: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_business_unit(
        self,
        info: strawberry.types.Info,
        id: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> BusinessUnitPayload:
        user = _get_current_user(info)
        if not user:
            return BusinessUnitPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == id).first()
            if not record:
                return BusinessUnitPayload(success=False, message="Business unit not found")
            if name is not None:
                dup = db.query(models.BusinessUnit).filter(models.BusinessUnit.name == name, models.BusinessUnit.id != id).first()
                if dup:
                    return BusinessUnitPayload(success=False, message="Business unit name already exists")
                record.name = name
            if code is not None:
                dup = db.query(models.BusinessUnit).filter(models.BusinessUnit.code == code, models.BusinessUnit.id != id).first()
                if dup:
                    return BusinessUnitPayload(success=False, message="Business unit code already exists")
                record.code = code
            if description is not None:
                record.description = description
            if is_active is not None:
                record.is_active = is_active
            db.commit()
            db.refresh(record)
            return BusinessUnitPayload(success=True, message="Business unit updated", business_unit=_bu_to_type(record))
        except Exception as e:
            db.rollback()
            return BusinessUnitPayload(success=False, message=f"Failed to update: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_business_unit(self, info: strawberry.types.Info, id: int) -> BusinessUnitPayload:
        user = _get_current_user(info)
        if not user:
            return BusinessUnitPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == id).first()
            if not record:
                return BusinessUnitPayload(success=False, message="Business unit not found")
            db.delete(record)
            db.commit()
            return BusinessUnitPayload(success=True, message="Business unit deleted")
        except IntegrityError:
            db.rollback()
            return BusinessUnitPayload(
                success=False,
                message="Business Unit tidak dapat dihapus karena masih memiliki Plant yang terkait. Hapus semua Plant di Business Unit ini terlebih dahulu.",
            )
        except Exception as e:
            db.rollback()
            return BusinessUnitPayload(success=False, message=f"Failed to delete: {str(e)}")
        finally:
            db.close()

    # ── Department mutations ─────────────────────────────────────────────

    @strawberry.mutation
    def create_department(
        self,
        info: strawberry.types.Info,
        name: str,
        code: str,
        description: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> DepartmentPayload:
        user = _get_current_user(info)
        if not user:
            return DepartmentPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            if db.query(models.Department).filter(models.Department.name == name).first():
                return DepartmentPayload(success=False, message="Department name already exists")
            if db.query(models.Department).filter(models.Department.code == code).first():
                return DepartmentPayload(success=False, message="Department code already exists")
            record = models.Department(
                name=name, code=code, description=description,
                is_active=is_active if is_active is not None else True,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return DepartmentPayload(success=True, message="Department created", department=_dept_to_type(record))
        except Exception as e:
            db.rollback()
            return DepartmentPayload(success=False, message=f"Failed to create: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_department(
        self,
        info: strawberry.types.Info,
        id: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> DepartmentPayload:
        user = _get_current_user(info)
        if not user:
            return DepartmentPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.Department).filter(models.Department.id == id).first()
            if not record:
                return DepartmentPayload(success=False, message="Department not found")
            if name is not None:
                dup = db.query(models.Department).filter(models.Department.name == name, models.Department.id != id).first()
                if dup:
                    return DepartmentPayload(success=False, message="Department name already exists")
                record.name = name
            if code is not None:
                dup = db.query(models.Department).filter(models.Department.code == code, models.Department.id != id).first()
                if dup:
                    return DepartmentPayload(success=False, message="Department code already exists")
                record.code = code
            if description is not None:
                record.description = description
            if is_active is not None:
                record.is_active = is_active
            db.commit()
            db.refresh(record)
            return DepartmentPayload(success=True, message="Department updated", department=_dept_to_type(record))
        except Exception as e:
            db.rollback()
            return DepartmentPayload(success=False, message=f"Failed to update: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_department(self, info: strawberry.types.Info, id: int) -> DepartmentPayload:
        user = _get_current_user(info)
        if not user:
            return DepartmentPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.Department).filter(models.Department.id == id).first()
            if not record:
                return DepartmentPayload(success=False, message="Department not found")
            db.delete(record)
            db.commit()
            return DepartmentPayload(success=True, message="Department deleted")
        except IntegrityError:
            db.rollback()
            return DepartmentPayload(
                success=False,
                message="Department tidak dapat dihapus karena masih digunakan oleh data lain.",
            )
        except Exception as e:
            db.rollback()
            return DepartmentPayload(success=False, message=f"Failed to delete: {str(e)}")
        finally:
            db.close()

    # ── Plant mutations ──────────────────────────────────────────────────

    @strawberry.mutation
    def create_plant(
        self,
        info: strawberry.types.Info,
        name: str,
        code: str,
        business_unit_id: int,
        location: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> PlantPayload:
        user = _get_current_user(info)
        if not user:
            return PlantPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            bu = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == business_unit_id).first()
            if not bu:
                return PlantPayload(success=False, message="Business unit not found")
            if db.query(models.Plant).filter(models.Plant.code == code).first():
                return PlantPayload(success=False, message="Plant code already exists")
            record = models.Plant(
                name=name, code=code, business_unit_id=business_unit_id,
                location=location, is_active=is_active if is_active is not None else True,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return PlantPayload(success=True, message="Plant created", plant=_plant_to_type(record))
        except Exception as e:
            db.rollback()
            return PlantPayload(success=False, message=f"Failed to create: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_plant(
        self,
        info: strawberry.types.Info,
        id: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
        business_unit_id: Optional[int] = None,
        location: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PlantPayload:
        user = _get_current_user(info)
        if not user:
            return PlantPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.Plant).filter(models.Plant.id == id).first()
            if not record:
                return PlantPayload(success=False, message="Plant not found")
            if business_unit_id is not None:
                bu = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == business_unit_id).first()
                if not bu:
                    return PlantPayload(success=False, message="Business unit not found")
                record.business_unit_id = business_unit_id
            if name is not None:
                record.name = name
            if code is not None:
                dup = db.query(models.Plant).filter(models.Plant.code == code, models.Plant.id != id).first()
                if dup:
                    return PlantPayload(success=False, message="Plant code already exists")
                record.code = code
            if location is not None:
                record.location = location
            if is_active is not None:
                record.is_active = is_active
            db.commit()
            db.refresh(record)
            return PlantPayload(success=True, message="Plant updated", plant=_plant_to_type(record))
        except Exception as e:
            db.rollback()
            return PlantPayload(success=False, message=f"Failed to update: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_plant(self, info: strawberry.types.Info, id: int) -> PlantPayload:
        user = _get_current_user(info)
        if not user:
            return PlantPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.Plant).filter(models.Plant.id == id).first()
            if not record:
                return PlantPayload(success=False, message="Plant not found")
            db.delete(record)
            db.commit()
            return PlantPayload(success=True, message="Plant deleted")
        except IntegrityError:
            db.rollback()
            return PlantPayload(
                success=False,
                message="Plant tidak dapat dihapus karena masih memiliki data Inspeksi K3L yang terkait. Hapus semua data Inspeksi K3L di Plant ini terlebih dahulu.",
            )
        except Exception as e:
            db.rollback()
            return PlantPayload(success=False, message=f"Failed to delete: {str(e)}")
        finally:
            db.close()


    # ── Role mutations ───────────────────────────────────────────────────

    @strawberry.mutation
    def create_role(
        self,
        info: strawberry.types.Info,
        name: str,
        level: int,
        description: Optional[str] = None,
    ) -> RolePayload:
        current_user = _get_current_user(info)
        if not current_user:
            return RolePayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            if db.query(models.Role).filter(models.Role.name == name).first():
                return RolePayload(success=False, message="Nama role sudah digunakan")
            if db.query(models.Role).filter(models.Role.level == level).first():
                return RolePayload(success=False, message="Level role sudah digunakan oleh role lain")
            record = models.Role(name=name, level=level, description=description)
            db.add(record)
            db.commit()
            db.refresh(record)
            return RolePayload(success=True, message="Role berhasil dibuat",
                               role=RoleType(id=record.id, name=record.name, level=record.level, description=record.description))
        except Exception as e:
            db.rollback()
            return RolePayload(success=False, message=f"Failed to create: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_role(
        self,
        info: strawberry.types.Info,
        id: int,
        name: Optional[str] = None,
        level: Optional[int] = None,
        description: Optional[str] = None,
    ) -> RolePayload:
        current_user = _get_current_user(info)
        if not current_user:
            return RolePayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.Role).filter(models.Role.id == id).first()
            if not record:
                return RolePayload(success=False, message="Role tidak ditemukan")
            if name is not None:
                dup = db.query(models.Role).filter(models.Role.name == name, models.Role.id != id).first()
                if dup:
                    return RolePayload(success=False, message="Nama role sudah digunakan")
                record.name = name
            if level is not None:
                dup = db.query(models.Role).filter(models.Role.level == level, models.Role.id != id).first()
                if dup:
                    return RolePayload(success=False, message="Level role sudah digunakan oleh role lain")
                record.level = level
            if description is not None:
                record.description = description or None
            db.commit()
            db.refresh(record)
            return RolePayload(success=True, message="Role berhasil diperbarui",
                               role=RoleType(id=record.id, name=record.name, level=record.level, description=record.description))
        except Exception as e:
            db.rollback()
            return RolePayload(success=False, message=f"Failed to update: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_role(self, info: strawberry.types.Info, id: int) -> RolePayload:
        current_user = _get_current_user(info)
        if not current_user:
            return RolePayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.Role).filter(models.Role.id == id).first()
            if not record:
                return RolePayload(success=False, message="Role tidak ditemukan")
            db.delete(record)
            db.commit()
            return RolePayload(success=True, message="Role berhasil dihapus")
        except IntegrityError:
            db.rollback()
            return RolePayload(
                success=False,
                message="Role tidak dapat dihapus karena masih digunakan oleh User. Ubah role User tersebut terlebih dahulu.",
            )
        except Exception as e:
            db.rollback()
            return RolePayload(success=False, message=f"Failed to delete: {str(e)}")
        finally:
            db.close()

    # ── User mutations ───────────────────────────────────────────────────

    @strawberry.mutation
    def create_user(
        self,
        info: strawberry.types.Info,
        email: str,
        password: str,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        role_id: Optional[int] = None,
        business_unit_id: Optional[int] = None,
        plant_id: Optional[int] = None,
        department_id: Optional[int] = None,
        is_active: Optional[bool] = True,
    ) -> UserPayload:
        current_user = _get_current_user(info)
        if not current_user:
            return UserPayload(success=False, message="Authentication required")
        if not email.endswith("@cp.co.id"):
            return UserPayload(success=False, message="Email harus menggunakan domain @cp.co.id")
        if len(password) < 6:
            return UserPayload(success=False, message="Password minimal 6 karakter")
        db = _get_db()
        try:
            if db.query(models.User).filter(models.User.email == email).first():
                return UserPayload(success=False, message="Email sudah terdaftar")
            if username and db.query(models.User).filter(models.User.username == username).first():
                return UserPayload(success=False, message="Username sudah digunakan")
            record = models.User(
                email=email,
                hashed_password=auth.hash_password(password),
                username=username or None,
                full_name=full_name or None,
                role_id=role_id,
                business_unit_id=business_unit_id,
                plant_id=plant_id,
                department_id=department_id,
                is_active=is_active if is_active is not None else True,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return UserPayload(success=True, message="User berhasil dibuat", user=_user_to_full_type(record))
        except Exception as e:
            db.rollback()
            return UserPayload(success=False, message=f"Failed to create: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_user(
        self,
        info: strawberry.types.Info,
        id: int,
        email: Optional[str] = None,
        password: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        role_id: Optional[int] = None,
        business_unit_id: Optional[int] = None,
        plant_id: Optional[int] = None,
        department_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> UserPayload:
        current_user = _get_current_user(info)
        if not current_user:
            return UserPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.User).filter(models.User.id == id).first()
            if not record:
                return UserPayload(success=False, message="User tidak ditemukan")
            if email is not None:
                if not email.endswith("@cp.co.id"):
                    return UserPayload(success=False, message="Email harus menggunakan domain @cp.co.id")
                dup = db.query(models.User).filter(models.User.email == email, models.User.id != id).first()
                if dup:
                    return UserPayload(success=False, message="Email sudah terdaftar")
                record.email = email
            if password is not None and password.strip():
                if len(password) < 6:
                    return UserPayload(success=False, message="Password minimal 6 karakter")
                record.hashed_password = auth.hash_password(password)
            if username is not None:
                dup = db.query(models.User).filter(models.User.username == username, models.User.id != id).first()
                if dup:
                    return UserPayload(success=False, message="Username sudah digunakan")
                record.username = username or None
            if full_name is not None:
                record.full_name = full_name or None
            if role_id is not None:
                record.role_id = role_id
            if business_unit_id is not None:
                record.business_unit_id = business_unit_id
            if plant_id is not None:
                record.plant_id = plant_id
            if department_id is not None:
                record.department_id = department_id
            if is_active is not None:
                record.is_active = is_active
            db.commit()
            db.refresh(record)
            return UserPayload(success=True, message="User berhasil diperbarui", user=_user_to_full_type(record))
        except Exception as e:
            db.rollback()
            return UserPayload(success=False, message=f"Failed to update: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_user(self, info: strawberry.types.Info, id: int) -> UserPayload:
        current_user = _get_current_user(info)
        if not current_user:
            return UserPayload(success=False, message="Authentication required")
        if current_user.id == id:
            return UserPayload(success=False, message="Anda tidak dapat menghapus akun Anda sendiri")
        db = _get_db()
        try:
            record = db.query(models.User).filter(models.User.id == id).first()
            if not record:
                return UserPayload(success=False, message="User tidak ditemukan")
            db.delete(record)
            db.commit()
            return UserPayload(success=True, message="User berhasil dihapus")
        except IntegrityError:
            db.rollback()
            return UserPayload(
                success=False,
                message="User tidak dapat dihapus karena masih memiliki data yang terkait.",
            )
        except Exception as e:
            db.rollback()
            return UserPayload(success=False, message=f"Failed to delete: {str(e)}")
        finally:
            db.close()


    # ── Safety Module mutations ──────────────────────────────────────────

    @strawberry.mutation
    def create_safety_module(
        self,
        info: strawberry.types.Info,
        title: str,
        video_url: Optional[str] = None,
        media_type: Optional[str] = "video",
        files: Optional[str] = None,
        kategori: Optional[str] = None,
        peraturan: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SafetyModulePayload:
        user = _get_current_user(info)
        if not user:
            return SafetyModulePayload(success=False, message="Authentication required")
        if user.role_id != 1:
            return SafetyModulePayload(success=False, message="Admin access required")
        db = _get_db()
        try:
            record = models.SafetyModule(
                title=title,
                video_url=video_url,
                media_type=media_type or "video",
                files=files,
                kategori=kategori,
                peraturan=peraturan,
                description=description,
                created_by=user.id,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            try:
                all_user_ids = [u.id for u in db.query(models.User.id).filter(models.User.is_active == True).all()]
                _notify_users(db, all_user_ids, "new_safety_module", f"Modul Baru: {title}", description or "", "/dashboard/modules", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return SafetyModulePayload(success=True, message="Module created", module=_module_to_type(record))
        except Exception as e:
            db.rollback()
            return SafetyModulePayload(success=False, message=f"Failed to create: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_safety_module(
        self,
        info: strawberry.types.Info,
        id: int,
        title: Optional[str] = None,
        video_url: Optional[str] = None,
        media_type: Optional[str] = None,
        files: Optional[str] = None,
        kategori: Optional[str] = None,
        peraturan: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SafetyModulePayload:
        user = _get_current_user(info)
        if not user:
            return SafetyModulePayload(success=False, message="Authentication required")
        if user.role_id != 1:
            return SafetyModulePayload(success=False, message="Admin access required")
        db = _get_db()
        try:
            record = db.query(models.SafetyModule).filter(models.SafetyModule.id == id).first()
            if not record:
                return SafetyModulePayload(success=False, message="Module not found")
            if title is not None:
                record.title = title
            if video_url is not None:
                record.video_url = video_url
            if media_type is not None:
                record.media_type = media_type
            if files is not None:
                record.files = files
            if kategori is not None:
                record.kategori = kategori if kategori != "" else None
            if peraturan is not None:
                record.peraturan = peraturan if peraturan != "" else None
            if description is not None:
                record.description = description if description != "" else None
            db.commit()
            db.refresh(record)
            try:
                actor = user.full_name or user.username or user.email
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                _notify_users(db, level3_ids, "update_safety_module", f"Modul Diperbarui: {record.title}", f"Diperbarui oleh {actor}", "/dashboard/modules", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return SafetyModulePayload(success=True, message="Module updated", module=_module_to_type(record))
        except Exception as e:
            db.rollback()
            return SafetyModulePayload(success=False, message=f"Failed to update: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_safety_module(self, info: strawberry.types.Info, id: int) -> SafetyModulePayload:
        user = _get_current_user(info)
        if not user:
            return SafetyModulePayload(success=False, message="Authentication required")
        if user.role_id != 1:
            return SafetyModulePayload(success=False, message="Admin access required")
        db = _get_db()
        try:
            record = db.query(models.SafetyModule).filter(models.SafetyModule.id == id).first()
            if not record:
                return SafetyModulePayload(success=False, message="Module not found")
            module_title = record.title
            files_json = record.files
            db.delete(record)
            db.commit()
            _delete_module_files(files_json)
            try:
                actor = user.full_name or user.username or user.email
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                _notify_users(db, level3_ids, "delete_safety_module", f"Modul Dihapus: {module_title}", f"Dihapus oleh {actor}", "/dashboard/modules", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return SafetyModulePayload(success=True, message="Module deleted")
        except Exception as e:
            db.rollback()
            return SafetyModulePayload(success=False, message=f"Failed to delete: {str(e)}")
        finally:
            db.close()


    # ── HSE Daily Report mutations ───────────────────────────────────────

    @strawberry.mutation
    def create_hse_daily(
        self,
        info: strawberry.types.Info,
        tanggal: str,
        pekerjaan: str,
        pekerja: str,
        lokasi_pekerjaan: Optional[str] = None,
        status_permit: Optional[bool] = False,
        no_permit: Optional[str] = None,
        jenis_pekerjaan: Optional[str] = None,
        jenis_pekerjaan_lainnya: Optional[str] = None,
        potensi_bahaya: Optional[str] = None,
        level_risiko: Optional[str] = None,
        pengendalian_bahaya: Optional[str] = None,
        pengawas_hse: Optional[str] = None,
        saran_masukan: Optional[str] = None,
        foto: Optional[str] = None,
        department_id: Optional[int] = None,
        business_unit_id: Optional[int] = None,
        plant_id: Optional[int] = None,
    ) -> HseDailyPayload:
        user = _get_current_user(info)
        if not user:
            return HseDailyPayload(success=False, message="Authentication required")
        if level_risiko and level_risiko not in ("Minor", "Major", "Critical"):
            return HseDailyPayload(success=False, message="Level risiko must be Minor, Major, or Critical")
        db = _get_db()
        try:
            record = models.HseDailyReport(
                tanggal=datetime.fromisoformat(tanggal),
                pekerjaan=pekerjaan,
                pekerja=pekerja,
                lokasi_pekerjaan=lokasi_pekerjaan,
                status_permit=status_permit or False,
                no_permit=no_permit,
                jenis_pekerjaan=jenis_pekerjaan,
                jenis_pekerjaan_lainnya=jenis_pekerjaan_lainnya,
                potensi_bahaya=potensi_bahaya,
                level_risiko=level_risiko,
                pengendalian_bahaya=pengendalian_bahaya,
                pengawas_hse=pengawas_hse,
                saran_masukan=saran_masukan,
                foto=foto,
                department_id=department_id,
                business_unit_id=business_unit_id,
                plant_id=plant_id,
                created_by=user.id,
                updated_by_name=user.full_name or user.username or user.email,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            try:
                all_user_ids = [u.id for u in db.query(models.User.id).filter(models.User.is_active == True).all()]
                submitter = user.full_name or user.username or user.email
                risiko_txt = f" (Risiko {level_risiko})" if level_risiko else ""
                _notify_users(db, all_user_ids, "new_report", "Permit Kerja HSE Baru", f"Permit Kerja HSE baru telah dibuat oleh {submitter}{risiko_txt}.", "/dashboard/reports/hse-daily", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return HseDailyPayload(success=True, message="HSE Daily Report created", report=_hse_daily_to_type(record, db))
        except Exception as e:
            db.rollback()
            return HseDailyPayload(success=False, message=f"Failed to create: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_hse_daily(
        self,
        info: strawberry.types.Info,
        id: int,
        tanggal: Optional[str] = None,
        pekerjaan: Optional[str] = None,
        pekerja: Optional[str] = None,
        lokasi_pekerjaan: Optional[str] = None,
        status_permit: Optional[bool] = None,
        no_permit: Optional[str] = None,
        jenis_pekerjaan: Optional[str] = None,
        jenis_pekerjaan_lainnya: Optional[str] = None,
        potensi_bahaya: Optional[str] = None,
        level_risiko: Optional[str] = None,
        pengendalian_bahaya: Optional[str] = None,
        pengawas_hse: Optional[str] = None,
        saran_masukan: Optional[str] = None,
        foto: Optional[str] = None,
        department_id: Optional[int] = None,
        business_unit_id: Optional[int] = None,
        plant_id: Optional[int] = None,
    ) -> HseDailyPayload:
        user = _get_current_user(info)
        if not user:
            return HseDailyPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.HseDailyReport).filter(models.HseDailyReport.id == id).first()
            if not record:
                return HseDailyPayload(success=False, message="Record not found")
            if level_risiko and level_risiko not in ("Minor", "Major", "Critical"):
                return HseDailyPayload(success=False, message="Level risiko must be Minor, Major, or Critical")
            if tanggal is not None:
                record.tanggal = datetime.fromisoformat(tanggal)
            if pekerjaan is not None:
                record.pekerjaan = pekerjaan
            if pekerja is not None:
                record.pekerja = pekerja
            if lokasi_pekerjaan is not None:
                record.lokasi_pekerjaan = lokasi_pekerjaan
            if status_permit is not None:
                record.status_permit = status_permit
            if no_permit is not None:
                record.no_permit = no_permit
            if jenis_pekerjaan is not None:
                record.jenis_pekerjaan = jenis_pekerjaan
            if jenis_pekerjaan_lainnya is not None:
                record.jenis_pekerjaan_lainnya = jenis_pekerjaan_lainnya
            if potensi_bahaya is not None:
                record.potensi_bahaya = potensi_bahaya
            if level_risiko is not None:
                record.level_risiko = level_risiko
            if pengendalian_bahaya is not None:
                record.pengendalian_bahaya = pengendalian_bahaya
            if pengawas_hse is not None:
                record.pengawas_hse = pengawas_hse
            if saran_masukan is not None:
                record.saran_masukan = saran_masukan
            if foto is not None:
                record.foto = foto
            if department_id is not None:
                record.department_id = department_id
            if business_unit_id is not None:
                record.business_unit_id = business_unit_id
            if plant_id is not None:
                record.plant_id = plant_id
            # Record whoever last edited the data
            record.updated_by_name = user.full_name or user.username or user.email
            db.commit()
            db.refresh(record)
            try:
                actor = user.full_name or user.username or user.email
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                risiko_txt = f" (Risiko {record.level_risiko})" if record.level_risiko else ""
                _notify_users(db, level3_ids, "update_report", "Permit Kerja HSE Diperbarui", f"Permit Kerja HSE telah diperbarui oleh {actor}{risiko_txt}.", "/dashboard/reports/hse-daily", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return HseDailyPayload(success=True, message="HSE Daily Report updated", report=_hse_daily_to_type(record, db))
        except Exception as e:
            db.rollback()
            return HseDailyPayload(success=False, message=f"Failed to update: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_hse_daily(self, info: strawberry.types.Info, id: int) -> HseDailyPayload:
        user = _get_current_user(info)
        if not user:
            return HseDailyPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.HseDailyReport).filter(models.HseDailyReport.id == id).first()
            if not record:
                return HseDailyPayload(success=False, message="Record not found")
            # Delete photos from Cloudinary
            if record.foto:
                try:
                    urls = json.loads(record.foto)
                    for url in (urls if isinstance(urls, list) else [urls]):
                        try:
                            delete_image(url)
                        except Exception:
                            pass
                except (json.JSONDecodeError, TypeError):
                    pass
            db.delete(record)
            db.commit()
            try:
                actor = user.full_name or user.username or user.email
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                _notify_users(db, level3_ids, "delete_report", "Permit Kerja HSE Dihapus", f"Permit Kerja HSE telah dihapus oleh {actor}.", "/dashboard/reports/hse-daily", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return HseDailyPayload(success=True, message="HSE Daily Report deleted")
        except Exception as e:
            db.rollback()
            return HseDailyPayload(success=False, message=f"Failed to delete: {str(e)}")
        finally:
            db.close()


    # ── Comment mutations ────────────────────────────────────────────────

    @strawberry.mutation
    def create_comment(
        self,
        info: strawberry.types.Info,
        report_type: str,
        report_id: int,
        content: str,
    ) -> CommentPayload:
        user = _get_current_user(info)
        if not user:
            return CommentPayload(success=False, message="Authentication required")
        if report_type not in _VALID_REPORT_TYPES:
            return CommentPayload(success=False, message="Invalid report type")
        content = (content or "").strip()
        if not content:
            return CommentPayload(success=False, message="Comment cannot be empty")
        if len(content) > 2000:
            return CommentPayload(success=False, message="Comment too long (max 2000 characters)")
        db = _get_db()
        try:
            if not _can_access_report(db, user, report_type, report_id):
                return CommentPayload(success=False, message="Report not found or access denied")
            record = models.Comment(
                report_type=report_type,
                report_id=report_id,
                user_id=user.id,
                content=content,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            try:
                if report_type == "inspection_k3l":
                    rep = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == report_id).first()
                    link = "/dashboard/reports/inspection-k3l"
                    label = "Inspeksi K3L"
                else:
                    rep = db.query(models.HseDailyReport).filter(models.HseDailyReport.id == report_id).first()
                    link = "/dashboard/reports/hse-daily"
                    label = "HSE Daily"
                if rep:
                    commenter = user.full_name or user.username or user.email
                    all_user_ids = [u.id for u in db.query(models.User.id).filter(models.User.is_active == True).all()]
                    _notify_users(db, all_user_ids, "new_comment", f"Komentar Baru pada {label}", f"{commenter}: {content[:80]}", link, exclude_id=user.id)
                    db.commit()
            except Exception:
                pass
            return CommentPayload(success=True, message="Comment posted", comment=_comment_to_type(record, db, user))
        except Exception as e:
            db.rollback()
            return CommentPayload(success=False, message=f"Failed to create comment: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_comment(self, info: strawberry.types.Info, id: int, content: str) -> CommentPayload:
        user = _get_current_user(info)
        if not user:
            return CommentPayload(success=False, message="Authentication required")
        content = (content or "").strip()
        if not content:
            return CommentPayload(success=False, message="Comment cannot be empty")
        if len(content) > 2000:
            return CommentPayload(success=False, message="Comment too long (max 2000 characters)")
        db = _get_db()
        try:
            record = db.query(models.Comment).filter(models.Comment.id == id).first()
            if not record:
                return CommentPayload(success=False, message="Comment not found")
            if record.user_id != user.id:
                return CommentPayload(success=False, message="You can only edit your own comments")
            report_type = record.report_type
            record.content = content
            db.commit()
            db.refresh(record)
            try:
                actor = user.full_name or user.username or user.email
                link = "/dashboard/reports/inspection-k3l" if report_type == "inspection_k3l" else "/dashboard/reports/hse-daily"
                label = "Inspeksi K3L" if report_type == "inspection_k3l" else "HSE Daily"
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                _notify_users(db, level3_ids, "update_comment", f"Komentar Diperbarui pada {label}", f"{actor}: {content[:80]}", link, exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return CommentPayload(success=True, message="Comment updated", comment=_comment_to_type(record, db, user))
        except Exception as e:
            db.rollback()
            return CommentPayload(success=False, message=f"Failed to update comment: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_comment(self, info: strawberry.types.Info, id: int) -> CommentPayload:
        user = _get_current_user(info)
        if not user:
            return CommentPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.Comment).filter(models.Comment.id == id).first()
            if not record:
                return CommentPayload(success=False, message="Comment not found")
            is_admin = user.role_id == 1
            if record.user_id != user.id and not is_admin:
                return CommentPayload(success=False, message="You can only delete your own comments")
            report_type = record.report_type
            snippet = record.content[:80]
            db.delete(record)
            db.commit()
            try:
                actor = user.full_name or user.username or user.email
                link = "/dashboard/reports/inspection-k3l" if report_type == "inspection_k3l" else "/dashboard/reports/hse-daily"
                label = "Inspeksi K3L" if report_type == "inspection_k3l" else "HSE Daily"
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                _notify_users(db, level3_ids, "delete_comment", f"Komentar Dihapus pada {label}", f"{actor}: {snippet}", link, exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return CommentPayload(success=True, message="Comment deleted")
        except Exception as e:
            db.rollback()
            return CommentPayload(success=False, message=f"Failed to delete comment: {str(e)}")
        finally:
            db.close()


    # ── Chat mutations ───────────────────────────────────────────────────

    @strawberry.mutation
    def send_chat_message(
        self,
        info: strawberry.types.Info,
        recipient_id: int,
        content: Optional[str] = None,
        attachment_url: Optional[str] = None,
        attachment_type: Optional[str] = None,
    ) -> ChatMessagePayload:
        user = _get_current_user(info)
        if not user:
            return ChatMessagePayload(success=False, message="Authentication required")
        content = (content or "").strip()
        if len(content) > 4000:
            return ChatMessagePayload(success=False, message="Pesan terlalu panjang (maks 4000 karakter)")
        if attachment_url and attachment_type not in ("image", "video"):
            return ChatMessagePayload(success=False, message="Jenis lampiran tidak valid")
        if not content and not attachment_url:
            return ChatMessagePayload(success=False, message="Pesan atau lampiran wajib diisi")
        db = _get_db()
        try:
            recipient = db.query(models.User).filter(models.User.id == recipient_id).first()
            if not recipient or not recipient.is_active:
                return ChatMessagePayload(success=False, message="Penerima tidak ditemukan")
            if not _can_chat_pair(db, user, recipient):
                return ChatMessagePayload(success=False, message="Anda tidak diizinkan mengirim pesan ke user ini")
            record = models.ChatMessage(
                sender_id=user.id,
                recipient_id=recipient_id,
                content=content,
                attachment_url=attachment_url or None,
                attachment_type=attachment_type or None,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            payload = _chat_msg_to_type(record, user)
            # Push to live subscribers — both sender (other tabs) and recipient
            chat_broker.publish(recipient_id, payload)
            chat_broker.publish(user.id, payload)
            try:
                sender_name = user.full_name or user.username or user.email
                msg_preview = content[:60] if content else "📎 Lampiran"
                _notify_users(db, [recipient_id], "new_chat", f"Pesan dari {sender_name}", msg_preview, "/dashboard/chat")
                db.commit()
            except Exception:
                pass
            return ChatMessagePayload(success=True, message="Pesan terkirim", chat_message=payload)
        except Exception as e:
            db.rollback()
            return ChatMessagePayload(success=False, message=f"Gagal mengirim pesan: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def update_chat_message(self, info: strawberry.types.Info, id: int, content: str) -> ChatMessagePayload:
        user = _get_current_user(info)
        if not user:
            return ChatMessagePayload(success=False, message="Authentication required")
        content = (content or "").strip()
        if len(content) > 4000:
            return ChatMessagePayload(success=False, message="Pesan terlalu panjang (maks 4000 karakter)")
        db = _get_db()
        try:
            record = db.query(models.ChatMessage).filter(models.ChatMessage.id == id).first()
            if not record:
                return ChatMessagePayload(success=False, message="Pesan tidak ditemukan")
            if record.sender_id != user.id:
                return ChatMessagePayload(success=False, message="Anda hanya dapat mengedit pesan Anda sendiri")
            if not content and not record.attachment_url:
                return ChatMessagePayload(success=False, message="Pesan tidak boleh kosong")
            recipient_id = record.recipient_id
            record.content = content
            db.commit()
            db.refresh(record)
            payload = _chat_msg_to_type(record, user)
            chat_broker.publish(record.recipient_id, payload)
            chat_broker.publish(record.sender_id, payload)
            try:
                sender_name = user.full_name or user.username or user.email
                _notify_users(db, [recipient_id], "new_chat", f"Pesan Diperbarui dari {sender_name}", content[:60], "/dashboard/chat")
                db.commit()
            except Exception:
                pass
            return ChatMessagePayload(success=True, message="Pesan diperbarui", chat_message=payload)
        except Exception as e:
            db.rollback()
            return ChatMessagePayload(success=False, message=f"Gagal memperbarui pesan: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_chat_message(self, info: strawberry.types.Info, id: int) -> ChatMessagePayload:
        user = _get_current_user(info)
        if not user:
            return ChatMessagePayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.ChatMessage).filter(models.ChatMessage.id == id).first()
            if not record:
                return ChatMessagePayload(success=False, message="Pesan tidak ditemukan")
            if record.sender_id != user.id and user.role_id != 1:
                return ChatMessagePayload(success=False, message="Anda hanya dapat menghapus pesan Anda sendiri")
            recipient_id = record.recipient_id
            sender_id = record.sender_id
            msg_id = record.id
            att_url = record.attachment_url
            att_type = record.attachment_type
            db.delete(record)
            db.commit()
            # Best-effort cleanup of the cloud asset
            if att_url:
                try:
                    if att_type == "video":
                        delete_video(att_url)
                    else:
                        delete_image(att_url)
                except Exception:
                    pass
            # Notify both sides with a tombstone payload (id only, content cleared)
            tombstone = ChatMessageType(
                id=msg_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                content="__deleted__",
                created_at=None,
                updated_at=None,
                read_at=None,
            )
            chat_broker.publish(recipient_id, tombstone)
            chat_broker.publish(sender_id, tombstone)
            try:
                actor_name = user.full_name or user.username or user.email
                notify_id = recipient_id if user.id == sender_id else sender_id
                _notify_users(db, [notify_id], "new_chat", f"Pesan Dihapus oleh {actor_name}", "Pesan telah dihapus", "/dashboard/chat")
                db.commit()
            except Exception:
                pass
            return ChatMessagePayload(success=True, message="Pesan dihapus")
        except Exception as e:
            db.rollback()
            return ChatMessagePayload(success=False, message=f"Gagal menghapus pesan: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def mark_chat_read(self, info: strawberry.types.Info, other_user_id: int) -> GenericPayload:
        user = _get_current_user(info)
        if not user:
            return GenericPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            now = datetime.utcnow()
            updated = (
                db.query(models.ChatMessage)
                .filter(
                    models.ChatMessage.sender_id == other_user_id,
                    models.ChatMessage.recipient_id == user.id,
                    models.ChatMessage.read_at.is_(None),
                )
                .update({models.ChatMessage.read_at: now}, synchronize_session=False)
            )
            db.commit()
            return GenericPayload(success=True, message=f"Marked {updated} messages as read")
        except Exception as e:
            db.rollback()
            return GenericPayload(success=False, message=f"Failed to mark read: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def mark_notification_read(self, info: strawberry.types.Info, id: int) -> NotificationPayload:
        user = _get_current_user(info)
        if not user:
            return NotificationPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            row = db.query(models.Notification).filter(
                models.Notification.id == id,
                models.Notification.user_id == user.id,
            ).first()
            if row:
                row.is_read = True
                db.commit()
            return NotificationPayload(success=True, message="Marked as read")
        except Exception as e:
            db.rollback()
            return NotificationPayload(success=False, message=str(e))
        finally:
            db.close()

    @strawberry.mutation
    def delete_notification(self, info: strawberry.types.Info, id: int) -> NotificationPayload:
        user = _get_current_user(info)
        if not user:
            return NotificationPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            db.query(models.Notification).filter(
                models.Notification.id == id,
                models.Notification.user_id == user.id,
            ).delete()
            db.commit()
            return NotificationPayload(success=True, message="Notification deleted")
        except Exception as e:
            db.rollback()
            return NotificationPayload(success=False, message=str(e))
        finally:
            db.close()

    @strawberry.mutation
    def mark_all_notifications_read(self, info: strawberry.types.Info) -> NotificationPayload:
        user = _get_current_user(info)
        if not user:
            return NotificationPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            db.query(models.Notification).filter(
                models.Notification.user_id == user.id,
            ).delete()
            db.commit()
            return NotificationPayload(success=True, message="All notifications cleared")
        except Exception as e:
            db.rollback()
            return NotificationPayload(success=False, message=str(e))
        finally:
            db.close()

    @strawberry.mutation
    def save_push_subscription(
        self,
        info: strawberry.types.Info,
        endpoint: str,
        p256dh: str,
        auth: str,
        user_agent: Optional[str] = None,
    ) -> NotificationPayload:
        """Register (or refresh) a browser Web Push subscription for this user."""
        user = _get_current_user(info)
        if not user:
            return NotificationPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            existing = (
                db.query(models.PushSubscription)
                .filter(models.PushSubscription.endpoint == endpoint)
                .first()
            )
            if existing:
                existing.user_id = user.id
                existing.p256dh = p256dh
                existing.auth = auth
                existing.user_agent = (user_agent or "")[:300]
            else:
                db.add(models.PushSubscription(
                    user_id=user.id,
                    endpoint=endpoint,
                    p256dh=p256dh,
                    auth=auth,
                    user_agent=(user_agent or "")[:300],
                ))
            db.commit()
            return NotificationPayload(success=True, message="Push subscription saved")
        except Exception as e:
            db.rollback()
            return NotificationPayload(success=False, message=str(e))
        finally:
            db.close()

    @strawberry.mutation
    def delete_push_subscription(self, info: strawberry.types.Info, endpoint: str) -> NotificationPayload:
        """Remove a browser Web Push subscription (e.g. on logout / unsubscribe)."""
        user = _get_current_user(info)
        if not user:
            return NotificationPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            db.query(models.PushSubscription).filter(
                models.PushSubscription.endpoint == endpoint,
                models.PushSubscription.user_id == user.id,
            ).delete()
            db.commit()
            return NotificationPayload(success=True, message="Push subscription removed")
        except Exception as e:
            db.rollback()
            return NotificationPayload(success=False, message=str(e))
        finally:
            db.close()


    @strawberry.mutation
    def create_case_incident(
        self,
        info: strawberry.types.Info,
        nama_pelapor: str,
        tanggal_kejadian: str,
        tanggal_pelaporan: str,
        nama_korban: str,
        pelapor_dept_id: Optional[int] = None,
        nama_saksi: Optional[str] = None,
        saksi_dept_id: Optional[int] = None,
        saksi_list: Optional[str] = None,
        korban_dept_id: Optional[int] = None,
        status_karyawan: Optional[str] = None,
        jenis_kecelakaan: Optional[str] = None,
        lokasi_kecelakaan: Optional[str] = None,
        deskripsi_kecelakaan: Optional[str] = None,
        penyebab_kecelakaan: Optional[str] = None,
        perbaikan_dilakukan: Optional[str] = None,
        foto_kejadian: Optional[str] = None,
        target_penyelesaian: Optional[str] = None,
        status: Optional[str] = None,
        business_unit_id: Optional[int] = None,
        plant_id: Optional[int] = None,
    ) -> CaseIncidentPayload:
        user = _get_current_user(info)
        if not user:
            return CaseIncidentPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = models.CaseIncident(
                nama_pelapor=nama_pelapor,
                pelapor_dept_id=pelapor_dept_id,
                nama_saksi=nama_saksi,
                saksi_dept_id=saksi_dept_id,
                saksi_list=saksi_list,
                tanggal_kejadian=datetime.fromisoformat(tanggal_kejadian.replace("T", " ")),
                tanggal_pelaporan=datetime.fromisoformat(tanggal_pelaporan.replace("T", " ")),
                nama_korban=nama_korban,
                korban_dept_id=korban_dept_id,
                status_karyawan=status_karyawan,
                jenis_kecelakaan=jenis_kecelakaan,
                lokasi_kecelakaan=lokasi_kecelakaan,
                deskripsi_kecelakaan=deskripsi_kecelakaan,
                penyebab_kecelakaan=penyebab_kecelakaan,
                perbaikan_dilakukan=perbaikan_dilakukan,
                foto_kejadian=foto_kejadian,
                target_penyelesaian=date.fromisoformat(target_penyelesaian) if target_penyelesaian else None,
                status=status or "Open",
                created_by=user.id,
                updated_by_name=user.full_name or user.username or user.email,
                business_unit_id=business_unit_id if business_unit_id is not None else user.business_unit_id,
                plant_id=plant_id if plant_id is not None else user.plant_id,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            try:
                all_user_ids = [u.id for u in db.query(models.User.id).filter(models.User.is_active == True).all()]
                submitter = user.full_name or user.username or user.email
                _notify_users(db, all_user_ids, "new_report", "Laporan Insiden Baru", f"Laporan Insiden & Kecelakaan Kerja baru telah dibuat oleh {submitter}.", "/dashboard/reports/case-incident", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return CaseIncidentPayload(success=True, message="Laporan berhasil disimpan", incident=_ci_to_type(record))
        except Exception as e:
            db.rollback()
            return CaseIncidentPayload(success=False, message=str(e))
        finally:
            db.close()

    @strawberry.mutation
    def update_case_incident(
        self,
        info: strawberry.types.Info,
        id: int,
        nama_pelapor: Optional[str] = None,
        pelapor_dept_id: Optional[int] = None,
        nama_saksi: Optional[str] = None,
        saksi_dept_id: Optional[int] = None,
        tanggal_kejadian: Optional[str] = None,
        tanggal_pelaporan: Optional[str] = None,
        nama_korban: Optional[str] = None,
        korban_dept_id: Optional[int] = None,
        status_karyawan: Optional[str] = None,
        jenis_kecelakaan: Optional[str] = None,
        lokasi_kecelakaan: Optional[str] = None,
        deskripsi_kecelakaan: Optional[str] = None,
        penyebab_kecelakaan: Optional[str] = None,
        perbaikan_dilakukan: Optional[str] = None,
        saksi_list: Optional[str] = None,
        foto_kejadian: Optional[str] = None,
        target_penyelesaian: Optional[str] = None,
        status: Optional[str] = None,
        business_unit_id: Optional[int] = None,
        plant_id: Optional[int] = None,
    ) -> CaseIncidentPayload:
        user = _get_current_user(info)
        if not user:
            return CaseIncidentPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.CaseIncident).filter(models.CaseIncident.id == id).first()
            if not record:
                return CaseIncidentPayload(success=False, message="Laporan tidak ditemukan")
            if nama_pelapor is not None: record.nama_pelapor = nama_pelapor
            if pelapor_dept_id is not None: record.pelapor_dept_id = pelapor_dept_id
            if nama_saksi is not None: record.nama_saksi = nama_saksi
            if saksi_dept_id is not None: record.saksi_dept_id = saksi_dept_id
            if tanggal_kejadian is not None: record.tanggal_kejadian = datetime.fromisoformat(tanggal_kejadian.replace("T", " "))
            if tanggal_pelaporan is not None: record.tanggal_pelaporan = datetime.fromisoformat(tanggal_pelaporan.replace("T", " "))
            if nama_korban is not None: record.nama_korban = nama_korban
            if korban_dept_id is not None: record.korban_dept_id = korban_dept_id
            if status_karyawan is not None: record.status_karyawan = status_karyawan
            if jenis_kecelakaan is not None: record.jenis_kecelakaan = jenis_kecelakaan
            if lokasi_kecelakaan is not None: record.lokasi_kecelakaan = lokasi_kecelakaan
            if deskripsi_kecelakaan is not None: record.deskripsi_kecelakaan = deskripsi_kecelakaan
            if penyebab_kecelakaan is not None: record.penyebab_kecelakaan = penyebab_kecelakaan
            if perbaikan_dilakukan is not None: record.perbaikan_dilakukan = perbaikan_dilakukan
            if saksi_list is not None: record.saksi_list = saksi_list
            if foto_kejadian is not None: record.foto_kejadian = foto_kejadian
            if target_penyelesaian is not None: record.target_penyelesaian = date.fromisoformat(target_penyelesaian) if target_penyelesaian else None
            reopened = False
            if status is not None:
                reopened = record.status == "Closed" and status == "Open"
                record.status = status
            if business_unit_id is not None: record.business_unit_id = business_unit_id
            if plant_id is not None: record.plant_id = plant_id
            # Record whoever last edited the data
            record.updated_by_name = user.full_name or user.username or user.email
            db.commit()
            db.refresh(record)
            try:
                actor = user.full_name or user.username or user.email
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                if reopened:
                    _notify_users(db, level3_ids, "reopen_report", "Laporan Insiden Dibuka Kembali", f"Laporan Insiden & Kecelakaan Kerja telah dibuka kembali (status Open) oleh {actor}.", "/dashboard/reports/case-incident", exclude_id=user.id)
                else:
                    _notify_users(db, level3_ids, "update_report", "Laporan Insiden Diperbarui", f"Laporan Insiden & Kecelakaan Kerja telah diperbarui oleh {actor}.", "/dashboard/reports/case-incident", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return CaseIncidentPayload(success=True, message="Laporan berhasil diperbarui", incident=_ci_to_type(record))
        except Exception as e:
            db.rollback()
            return CaseIncidentPayload(success=False, message=str(e))
        finally:
            db.close()

    @strawberry.mutation
    def delete_case_incident(self, info: strawberry.types.Info, id: int) -> CaseIncidentPayload:
        user = _get_current_user(info)
        if not user:
            return CaseIncidentPayload(success=False, message="Authentication required")
        db = _get_db()
        try:
            record = db.query(models.CaseIncident).filter(models.CaseIncident.id == id).first()
            if not record:
                return CaseIncidentPayload(success=False, message="Laporan tidak ditemukan")
            db.delete(record)
            db.commit()
            try:
                actor = user.full_name or user.username or user.email
                level3_ids = [u.id for u in db.query(models.User.id).join(models.Role, models.User.role_id == models.Role.id).filter(models.User.is_active == True, models.Role.level == 0).all()]
                _notify_users(db, level3_ids, "delete_report", "Laporan Insiden Dihapus", f"Laporan Insiden & Kecelakaan Kerja telah dihapus oleh {actor}.", "/dashboard/reports/case-incident", exclude_id=user.id)
                db.commit()
            except Exception:
                pass
            return CaseIncidentPayload(success=True, message="Laporan berhasil dihapus")
        except Exception as e:
            db.rollback()
            return CaseIncidentPayload(success=False, message=str(e))
        finally:
            db.close()


def _user_from_connection(info: strawberry.types.Info) -> Optional[models.User]:
    """Resolve auth from a WebSocket connection_init payload (subscriptions)."""
    ctx = info.context
    params = None
    if isinstance(ctx, dict):
        params = ctx.get("connection_params")
    else:
        params = getattr(ctx, "connection_params", None)
    if not params:
        return None
    token = params.get("authorization") or params.get("Authorization") or ""
    if isinstance(token, str):
        token = token.removeprefix("Bearer ").strip()
    if not token:
        return None
    email = auth.decode_token(token)
    if not email:
        return None
    db = _get_db()
    try:
        return db.query(models.User).filter(models.User.email == email).first()
    finally:
        db.close()


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def chat_message_stream(self, info: strawberry.types.Info) -> AsyncIterator[ChatMessageType]:
        user = _user_from_connection(info)
        if not user:
            return
        q = chat_broker.subscribe(user.id)
        try:
            while True:
                payload = await q.get()
                yield payload
        except asyncio.CancelledError:
            raise
        finally:
            chat_broker.unsubscribe(user.id, q)

    @strawberry.subscription
    async def notification_stream(self, info: strawberry.types.Info) -> AsyncIterator[NotificationType]:
        user = _user_from_connection(info)
        if not user:
            return
        q = notif_broker.subscribe(user.id)
        try:
            while True:
                payload = await q.get()
                yield payload
        except asyncio.CancelledError:
            raise
        finally:
            notif_broker.unsubscribe(user.id, q)


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
graphql_router = GraphQLRouter(
    schema,
    subscription_protocols=["graphql-transport-ws", "graphql-ws"],
)
