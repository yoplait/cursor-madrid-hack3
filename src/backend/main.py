from __future__ import annotations

import io
import sys
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from model.service import detect, get_model, resolve_weights, result_to_dict  # noqa: E402

app = FastAPI(title="Hack3 Vision API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/model")
def model_info():
    get_model()
    weights = resolve_weights()
    return {"weights": str(weights), "ready": weights.exists()}


@app.post("/detect")
async def detect_image(file: UploadFile = File(...), conf: float = 0.25):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Expected an image upload")

    raw = await file.read()
    try:
        image = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image file") from exc

    result = detect(image, conf=conf, save=False)
    return result_to_dict(result)
