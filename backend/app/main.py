"""
landmark_project/backend/app/main.py
"""
import io
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

from app.inference import LandmarkClassifier

MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
DEFAULT_ORIGINS = (
    "http://localhost:3000,http://127.0.0.1:3000,"
    "http://localhost:5173,http://127.0.0.1:5173"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.classifier = LandmarkClassifier(
        MODEL_DIR / "landmarks.onnx", MODEL_DIR / "classes.json"
    )
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    o.strip()
    for o in os.environ.get("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(request: Request, file: UploadFile = File(...)):
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image is larger than 10 MB.")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="File is not a valid image.")
    predictions = request.app.state.classifier.predict(img)
    return {"predictions": predictions}


#EOF