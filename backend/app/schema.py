import strawberry
import json
from strawberry.fastapi import GraphQLRouter
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import date

from app import models, auth
from app.database import get_db
from app.cloudinary_utils import delete_image


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


@strawberry.type
class UserType:
    id: int
    email: str
    role: str
    business_unit: str


@strawberry.type
class AuthPayload:
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[UserType] = None


@strawberry.type
class BusinessUnitType:
    id: int
    name: str


@strawberry.type
class PlantType:
    id: int
    name: str
    business_unit_id: Optional[int] = None


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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@strawberry.type
class InspectionK3LPayload:
    success: bool
    message: str
    inspection: Optional[InspectionK3LType] = None


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
        created_at=str(record.created_at) if record.created_at else None,
        updated_at=str(record.updated_at) if record.updated_at else None,
    )


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
            records = db.query(models.InspectionK3L).order_by(models.InspectionK3L.created_at.desc()).all()
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
            return [BusinessUnitType(id=r.id, name=r.name) for r in records]
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
            return [PlantType(id=r.id, name=r.name, business_unit_id=r.business_unit_id) for r in records]
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
            return AuthPayload(
                success=True,
                message="Registration successful",
                token=token,
                user=UserType(id=user.id, email=user.email, role=user.role, business_unit=user.business_unit),
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
            return AuthPayload(
                success=True,
                message="Login successful",
                token=token,
                user=UserType(id=user.id, email=user.email, role=user.role, business_unit=user.business_unit),
            )
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
                tanggal=date.fromisoformat(tanggal),
                kategori_temuan=kategori_temuan,
                deskripsi_temuan=deskripsi_temuan,
                foto_sebelum=foto_sebelum,
                foto_sesudah=foto_sesudah,
                lokasi=lokasi,
                tindakan_perbaikan=tindakan_perbaikan,
                target_selesai=date.fromisoformat(target_selesai) if target_selesai else None,
                status=status or "Open",
                aktual_close=date.fromisoformat(aktual_close) if aktual_close else None,
                created_by=user.id,
                business_unit_id=business_unit_id,
                plant_id=plant_id,
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
    ) -> InspectionK3LPayload:
        user = _get_current_user(info)
        if not user:
            return InspectionK3LPayload(success=False, message="Authentication required")

        db = _get_db()
        try:
            record = db.query(models.InspectionK3L).filter(models.InspectionK3L.id == id).first()
            if not record:
                return InspectionK3LPayload(success=False, message="Record not found")

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
                record.tanggal = date.fromisoformat(tanggal)
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
                record.aktual_close = date.fromisoformat(aktual_close)
            if business_unit_id is not None:
                record.business_unit_id = business_unit_id
            if plant_id is not None:
                record.plant_id = plant_id

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


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_router = GraphQLRouter(schema)
