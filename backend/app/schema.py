import strawberry
import json
from strawberry.fastapi import GraphQLRouter
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime

from app import models, auth
from app.database import get_db
from app.cloudinary_utils import delete_image, delete_video


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
    business_unit_id: Optional[int] = None
    plant_id: Optional[int] = None


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
class InspectionK3LType:
    id: int
    tanggal: str
    kategori_temuan: str
    deskripsi_temuan: Optional[str] = None
    foto_sebelum: Optional[str] = None
    foto_sesudah: Optional[str] = None
    lokasi: Optional[str] = None
    tindakan_perbaikan: Optional[str] = None
    target_selesai: Optional[str] = None
    status: str
    aktual_close: Optional[str] = None
    created_by: Optional[int] = None
    business_unit_id: Optional[int] = None
    plant_id: Optional[int] = None
    department_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@strawberry.type
class InspectionK3LPayload:
    success: bool
    message: str
    inspection: Optional[InspectionK3LType] = None


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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


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
        is_active=u.is_active if u.is_active is not None else True,
        created_at=str(u.created_at) if u.created_at else None,
        updated_at=str(u.updated_at) if u.updated_at else None,
    )


def _model_to_type(record: models.InspectionK3L) -> InspectionK3LType:
    return InspectionK3LType(
        id=record.id,
        tanggal=str(record.tanggal) if record.tanggal else "",
        kategori_temuan=record.kategori_temuan,
        deskripsi_temuan=record.deskripsi_temuan,
        foto_sebelum=record.foto_sebelum,
        foto_sesudah=record.foto_sesudah,
        lokasi=record.lokasi,
        tindakan_perbaikan=record.tindakan_perbaikan,
        target_selesai=str(record.target_selesai) if record.target_selesai else None,
        status=record.status or "Open",
        aktual_close=str(record.aktual_close) if record.aktual_close else None,
        created_by=record.created_by,
        business_unit_id=record.business_unit_id,
        plant_id=record.plant_id,
        department_id=record.department_id,
        created_at=str(record.created_at) if record.created_at else None,
        updated_at=str(record.updated_at) if record.updated_at else None,
    )


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
            created_at=str(r.created_at) if r.created_at else None,
            updated_at=str(r.updated_at) if r.updated_at else None,
        )
    finally:
        if close_db:
            db.close()


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
                    business_unit_id=user.business_unit_id,
                    plant_id=user.plant_id,
                ),
            )
        except Exception as e:
            db.rollback()
            return AuthPayload(success=False, message=f"Registration failed: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def login(self, email: str, password: str) -> AuthPayload:
        if not email.endswith("@cp.co.id"):
            return AuthPayload(success=False, message="Invalid email format")

        db = _get_db()
        try:
            user = db.query(models.User).filter(models.User.email == email).first()
            if not user:
                return AuthPayload(success=False, message="User not found. Please register first")
            if not auth.verify_password(password, user.hashed_password):
                return AuthPayload(success=False, message="Invalid password")

            token = auth.create_token(email)
            role_name = db.query(models.Role).filter(models.Role.id == user.role_id).first()
            bu_name = db.query(models.BusinessUnit).filter(models.BusinessUnit.id == user.business_unit_id).first()
            plant_rec = db.query(models.Plant).filter(models.Plant.id == user.plant_id).first()
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
                    business_unit_id=user.business_unit_id,
                    plant_id=user.plant_id,
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
    ) -> InspectionK3LPayload:
        user = _get_current_user(info)
        if not user:
            return InspectionK3LPayload(success=False, message="Authentication required")

        if status and status not in ("Open", "In Progress", "Closed"):
            return InspectionK3LPayload(success=False, message="Status must be Open, In Progress, or Closed")

        db = _get_db()
        try:
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

            record = models.InspectionK3L(
                tanggal=datetime.fromisoformat(tanggal),
                kategori_temuan=kategori_temuan,
                deskripsi_temuan=deskripsi_temuan,
                foto_sebelum=foto_sebelum,
                foto_sesudah=foto_sesudah,
                lokasi=lokasi,
                tindakan_perbaikan=tindakan_perbaikan,
                target_selesai=date.fromisoformat(target_selesai) if target_selesai else None,
                status=status or "Open",
                aktual_close=datetime.fromisoformat(aktual_close) if aktual_close else None,
                created_by=user.id,
                business_unit_id=business_unit_id,
                plant_id=plant_id,
                department_id=department_id,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
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
    ) -> InspectionK3LPayload:
        user = _get_current_user(info)
        if not user:
            return InspectionK3LPayload(success=False, message="Authentication required")

        db = _get_db()
        try:
            record = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == id).first()
            if not record:
                return InspectionK3LPayload(success=False, message="Record not found")

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
                record.tindakan_perbaikan = tindakan_perbaikan
            if target_selesai is not None:
                record.target_selesai = date.fromisoformat(target_selesai)
            if status is not None:
                if status not in ("Open", "In Progress", "Closed"):
                    return InspectionK3LPayload(success=False, message="Status must be Open, In Progress, or Closed")
                record.status = status
            if aktual_close is not None:
                record.aktual_close = datetime.fromisoformat(aktual_close)
            if business_unit_id is not None:
                record.business_unit_id = business_unit_id
            if plant_id is not None:
                record.plant_id = plant_id
            if department_id is not None:
                record.department_id = department_id

            db.commit()
            db.refresh(record)
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
    def delete_inspection_k3l(self, info: strawberry.types.Info, id: int) -> InspectionK3LPayload:
        user = _get_current_user(info)
        if not user:
            return InspectionK3LPayload(success=False, message="Authentication required")

        db = _get_db()
        try:
            record = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == id).first()
            if not record:
                return InspectionK3LPayload(success=False, message="Record not found")

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

            db.delete(record)
            db.commit()

            # Delete from Cloudinary after successful DB delete (best-effort)
            for url in photo_urls:
                try:
                    delete_image(url)
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
                description=description,
                created_by=user.id,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
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
            if description is not None:
                record.description = description
            db.commit()
            db.refresh(record)
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
            video_url = record.video_url
            db.delete(record)
            db.commit()
            if video_url:
                try:
                    delete_video(video_url)
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
        if level_risiko and level_risiko not in ("Rendah", "Sedang", "Tinggi"):
            return HseDailyPayload(success=False, message="Level risiko must be Rendah, Sedang, or Tinggi")
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
            )
            db.add(record)
            db.commit()
            db.refresh(record)
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
            if level_risiko and level_risiko not in ("Rendah", "Sedang", "Tinggi"):
                return HseDailyPayload(success=False, message="Level risiko must be Rendah, Sedang, or Tinggi")
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
            db.commit()
            db.refresh(record)
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
            return HseDailyPayload(success=True, message="HSE Daily Report deleted")
        except Exception as e:
            db.rollback()
            return HseDailyPayload(success=False, message=f"Failed to delete: {str(e)}")
        finally:
            db.close()


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_router = GraphQLRouter(schema)
