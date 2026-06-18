from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, date, timedelta, timezone
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.schema import graphql_router, _notify_users
from app.cloudinary_utils import upload_image, upload_video, upload_document
from app.database import get_db
from app import models as _models
from app import auth as _auth

load_dotenv()

_WIB = timezone(timedelta(hours=7))


def _run_overdue_notifications() -> None:
    db = next(get_db())
    try:
        today = datetime.now(_WIB).date()
        records = (
            db.query(_models.InspectionK3L)
            .filter(
                _models.InspectionK3L.status != "Closed",
                _models.InspectionK3L.target_selesai.isnot(None),
            )
            .all()
        )
        for record in records:
            days_left = (record.target_selesai - today).days
            if days_left == 3:
                notif_type = "overdue_warning_3d"
                title = "Temuan Mendekati Batas Waktu"
                message = (
                    f'Temuan "{record.deskripsi_temuan or record.kategori_temuan}" '
                    f"akan overdue dalam 3 hari (target: {record.target_selesai})"
                )
            elif days_left == 1:
                notif_type = "overdue_warning_1d"
                title = "Temuan Hampir Overdue"
                message = (
                    f'Temuan "{record.deskripsi_temuan or record.kategori_temuan}" '
                    f"akan overdue besok (target: {record.target_selesai})"
                )
            elif days_left < 0:
                days_overdue = -days_left
                desc = record.deskripsi_temuan or record.kategori_temuan
                if days_overdue >= 3:
                    notif_type = "overdue_critical"
                    title = "URGENT — Temuan K3L Belum Ditindaklanjuti"
                else:
                    notif_type = "overdue_daily"
                    title = "Tindakan Segera: Temuan K3L Melewati Batas Waktu"
                message = (
                    f'Temuan "{desc}" telah melewati target selesai selama '
                    f'{days_overdue} hari (target: {record.target_selesai}) dan masih '
                    f'berstatus {record.status}. Tindakan perbaikan segera diperlukan.'
                )
            else:
                continue

            link = f"/dashboard/reports/inspection-k3l?view={record.id}"
            today_start = datetime.combine(today, datetime.min.time())
            already = (
                db.query(_models.Notification)
                .filter(
                    _models.Notification.type == notif_type,
                    _models.Notification.link == link,
                    _models.Notification.created_at >= today_start,
                )
                .first()
            )
            if already:
                continue

            user_ids: set[int] = set()
            if record.department_id:
                for u in (
                    db.query(_models.User)
                    .filter(
                        _models.User.department_id == record.department_id,
                        _models.User.is_active == True,
                    )
                    .all()
                ):
                    user_ids.add(u.id)
            for u in (
                db.query(_models.User)
                .join(_models.Role)
                .filter(_models.Role.level <= 3, _models.User.is_active == True)
                .all()
            ):
                user_ids.add(u.id)

            if user_ids:
                _notify_users(db, list(user_ids), notif_type, title, message, link)

        case_records = (
            db.query(_models.CaseIncident)
            .filter(
                _models.CaseIncident.status != "Closed",
                _models.CaseIncident.target_penyelesaian.isnot(None),
            )
            .all()
        )
        for record in case_records:
            days_left = (record.target_penyelesaian - today).days
            if days_left == 3:
                notif_type = "overdue_warning_3d"
                title = "Tindak Lanjut Kasus Mendekati Batas Waktu"
                message = (
                    f'Tindak lanjut kasus "{record.nama_korban}" '
                    f"akan overdue dalam 3 hari (target: {record.target_penyelesaian})"
                )
            elif days_left == 1:
                notif_type = "overdue_warning_1d"
                title = "Tindak Lanjut Kasus Hampir Overdue"
                message = (
                    f'Tindak lanjut kasus "{record.nama_korban}" '
                    f"akan overdue besok (target: {record.target_penyelesaian})"
                )
            elif days_left < 0:
                days_overdue = -days_left
                if days_overdue >= 3:
                    notif_type = "overdue_critical"
                    title = "URGENT — Kasus Belum Ditindaklanjuti"
                else:
                    notif_type = "overdue_daily"
                    title = "Tindakan Segera: Tindak Lanjut Kasus Melewati Batas Waktu"
                message = (
                    f'Tindak lanjut kasus "{record.nama_korban}" telah melewati target '
                    f'penyelesaian selama {days_overdue} hari (target: {record.target_penyelesaian}) '
                    f'dan masih berstatus {record.status}. Penyelesaian segera diperlukan.'
                )
            else:
                continue

            link = f"/dashboard/reports/case-incident?view={record.id}"
            today_start = datetime.combine(today, datetime.min.time())
            already = (
                db.query(_models.Notification)
                .filter(
                    _models.Notification.type == notif_type,
                    _models.Notification.link == link,
                    _models.Notification.created_at >= today_start,
                )
                .first()
            )
            if already:
                continue

            user_ids = set()
            if record.korban_dept_id:
                for u in (
                    db.query(_models.User)
                    .filter(
                        _models.User.department_id == record.korban_dept_id,
                        _models.User.is_active == True,
                    )
                    .all()
                ):
                    user_ids.add(u.id)
            for u in (
                db.query(_models.User)
                .join(_models.Role)
                .filter(_models.Role.level <= 3, _models.User.is_active == True)
                .all()
            ):
                user_ids.add(u.id)

            if user_ids:
                _notify_users(db, list(user_ids), notif_type, title, message, link)

        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"[overdue-notif] error: {exc}")
    finally:
        db.close()


async def _overdue_scheduler() -> None:
    # Run shortly after startup so overdue items surface promptly, then re-check
    # every hour. Notifications are de-duplicated to once per report per day,
    # so hourly polling will not spam users.
    await asyncio.sleep(10)
    while True:
        try:
            _run_overdue_notifications()
        except Exception as exc:
            print(f"[overdue-notif] scheduler error: {exc}")
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_overdue_scheduler())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Safety Dashboard API", lifespan=lifespan)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

_origins = list({FRONTEND_URL, "http://localhost:5173", "http://localhost:5174"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"http://(localhost|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_router, prefix="/graphql")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    try:
        contents = await file.read()
        url = upload_image(contents)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-video")
async def upload_video_file(request: Request, file: UploadFile = File(...)):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    email = _auth.decode_token(token) if token else None
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = next(get_db())
    try:
        user = db.query(_models.User).filter(_models.User.email == email).first()
    finally:
        db.close()

    if not user or user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin access required")

    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files are allowed")

    try:
        contents = await file.read()
        url = upload_video(contents)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


CHAT_IMAGE_MAX_BYTES = 8 * 1024 * 1024    # 8 MB
CHAT_VIDEO_MAX_BYTES = 50 * 1024 * 1024   # 50 MB


@app.post("/upload-chat-media")
async def upload_chat_media(request: Request, file: UploadFile = File(...)):
    """Authenticated users (any role) upload an image or video for a chat message."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    email = _auth.decode_token(token) if token else None
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = next(get_db())
    try:
        user = db.query(_models.User).filter(_models.User.email == email).first()
    finally:
        db.close()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")

    ctype = (file.content_type or "").lower()
    if ctype.startswith("image/"):
        kind = "image"
        max_bytes = CHAT_IMAGE_MAX_BYTES
    elif ctype.startswith("video/"):
        kind = "video"
        max_bytes = CHAT_VIDEO_MAX_BYTES
    else:
        raise HTTPException(status_code=400, detail="Only image or video files are allowed")

    contents = await file.read()
    if len(contents) > max_bytes:
        limit_mb = max_bytes // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"File too large (max {limit_mb} MB)")

    try:
        url = upload_image(contents, folder="safety_dashboard/chat") if kind == "image" \
            else upload_video(contents, folder="safety_dashboard/chat")
        return {"url": url, "type": kind}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


ALLOWED_DOC_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


@app.post("/upload-document")
async def upload_document_file(request: Request, file: UploadFile = File(...)):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    email = _auth.decode_token(token) if token else None
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = next(get_db())
    try:
        user = db.query(_models.User).filter(_models.User.email == email).first()
    finally:
        db.close()

    if not user or user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin access required")

    if file.content_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(status_code=400, detail="Only document files are allowed (PDF, Word, Excel, PowerPoint)")

    try:
        contents = await file.read()
        url = upload_document(contents)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
