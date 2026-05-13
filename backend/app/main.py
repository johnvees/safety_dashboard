from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.schema import graphql_router
from app.cloudinary_utils import upload_image, upload_video
from app.database import get_db
from app import models as _models
from app import auth as _auth

load_dotenv()

app = FastAPI(title="Safety Dashboard API")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

_origins = list({FRONTEND_URL, "http://localhost:5173", "http://localhost:5174"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
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
