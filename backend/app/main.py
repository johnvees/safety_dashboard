from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.schema import graphql_router
from app.cloudinary_utils import upload_image

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
