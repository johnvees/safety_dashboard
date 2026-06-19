import os
import uuid
from datetime import datetime, date
from pathlib import Path

UPLOAD_DIR = os.getenv("UPLOAD_DIR")
BASE_URL = os.getenv("BASE_URL")


def _date_path() -> str:
    today = date.today()
    return f"{today.year}/{today.month:02d}/{today.day:02d}"


def _save(file_bytes: bytes, kind: str, ext: str, prefix: str = "") -> str:
    rel = f"{_date_path()}/{kind}"
    dest = Path(UPLOAD_DIR) / rel
    dest.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    uid = uuid.uuid4().hex[:6]
    base = f"{prefix}_{ts}_{uid}" if prefix else f"{ts}_{uid}"
    filename = f"{base}{ext}"
    (dest / filename).write_bytes(file_bytes)
    return f"{BASE_URL}/uploads/{rel}/{filename}"


def _ext_from_bytes(file_bytes: bytes, default: str = "") -> str:
    if file_bytes[:4] == b"\x89PNG":
        return ".png"
    if file_bytes[:2] == b"\xff\xd8":
        return ".jpg"
    if file_bytes[:4] in (b"GIF8", b"GIF9"):
        return ".gif"
    if file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP":
        return ".webp"
    if file_bytes[:4] in (b"\x00\x00\x00\x18", b"\x00\x00\x00\x20") or file_bytes[4:8] == b"ftyp":
        return ".mp4"
    if file_bytes[:3] == b"ID3" or file_bytes[:2] == b"\xff\xfb":
        return ".mp3"
    return default


def upload_image(file_bytes: bytes, folder: str = "", prefix: str = "") -> str:
    ext = _ext_from_bytes(file_bytes, ".jpg")
    return _save(file_bytes, "images", ext, prefix)


def delete_image(url: str) -> None:
    _delete_by_url(url)


def upload_video(file_bytes: bytes, folder: str = "", prefix: str = "") -> str:
    ext = _ext_from_bytes(file_bytes, ".mp4")
    return _save(file_bytes, "videos", ext, prefix)


def delete_video(url: str) -> None:
    _delete_by_url(url)


def upload_document(file_bytes: bytes, folder: str = "", ext: str = ".bin", prefix: str = "") -> str:
    return _save(file_bytes, "documents", ext, prefix)


def delete_document(url: str) -> None:
    _delete_by_url(url)


def _delete_by_url(url: str) -> None:
    prefix = f"{BASE_URL}/uploads/"
    if url.startswith(prefix):
        rel = url[len(prefix):]
        path = Path(UPLOAD_DIR) / rel
        if path.exists():
            path.unlink()
