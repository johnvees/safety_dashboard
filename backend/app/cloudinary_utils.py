import os
import re
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


def upload_image(file_bytes: bytes, folder: str = "safety_dashboard") -> str:
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type="image",
    )
    return result["secure_url"]


def _extract_public_id(url: str) -> str | None:
    # Cloudinary URL: .../upload/v1234567890/folder/name.ext  OR  .../upload/folder/name.ext
    match = re.search(r"/upload/(?:v\d+/)?(.+?)(?:\.[a-zA-Z0-9]+)?$", url)
    return match.group(1) if match else None


def delete_image(url: str) -> None:
    public_id = _extract_public_id(url)
    if public_id:
        cloudinary.uploader.destroy(public_id, resource_type="image")


def upload_video(file_bytes: bytes, folder: str = "safety_dashboard/videos") -> str:
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type="video",
    )
    return result["secure_url"]


def delete_video(url: str) -> None:
    public_id = _extract_public_id(url)
    if public_id:
        cloudinary.uploader.destroy(public_id, resource_type="video")


def upload_document(file_bytes: bytes, folder: str = "safety_dashboard/documents") -> str:
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type="raw",
    )
    return result["secure_url"]


def delete_document(url: str) -> None:
    public_id = _extract_public_id(url)
    if public_id:
        cloudinary.uploader.destroy(public_id, resource_type="raw")
