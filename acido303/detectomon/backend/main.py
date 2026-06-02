import json
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.card_registry import CardRegistry
from src.config import get_settings
from src.detector import DetectionEngine
from src.image_utils import decode_jpeg_base64, resize_frame
from src.schemas import (
    Box,
    CardOut,
    DetectFrameRequest,
    DetectFrameResponse,
    DetectionOut,
    GenerateCardRequest,
    GenerateCardResponse,
)

settings = get_settings()
registry = CardRegistry()
engine: DetectionEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    engine = DetectionEngine(settings)
    mode = "mock" if engine.is_mock else "libreyolo"
    print(f"DetectoMon backend ready ({mode}, model={settings.model_path})")
    yield


app = FastAPI(title="DetectoMon API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _enrich_detections(
    frame_id: int,
    raw: list[dict],
) -> list[DetectionOut]:
    out: list[DetectionOut] = []
    for i, d in enumerate(raw, start=1):
        det_id = f"frame-{frame_id}-det-{i}"
        card = registry.lookup_by_class(d["className"])
        out.append(
            DetectionOut(
                id=det_id,
                className=d["className"],
                confidence=d["confidence"],
                box=Box(**d["box"]),
                knownObject=card is not None,
                cardId=card.card_id if card else None,
            )
        )
    return out


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mockDetection": engine.is_mock if engine else True,
        "modelPath": settings.model_path,
    }


@app.post("/api/cards/generate", response_model=GenerateCardResponse)
def generate_card(body: GenerateCardRequest):
    card, reused = registry.generate(
        body.detectionId,
        body.className,
        body.box.model_dump(),
    )
    message = "Existing card found" if reused else "New card generated"
    return GenerateCardResponse(
        card=CardOut(
            cardId=card.card_id,
            name=card.name,
            className=card.class_name,
            detectionId=body.detectionId,
            reused=reused,
        ),
        message=message,
    )


@app.get("/api/cards/{card_id}", response_model=CardOut)
def get_card(card_id: str):
    card = registry.get(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return CardOut(
        cardId=card.card_id,
        name=card.name,
        className=card.class_name,
        detectionId=card.detection_id or "",
        reused=True,
    )


@app.websocket("/ws/detect")
async def ws_detect(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            start = time.perf_counter()
            try:
                payload = json.loads(raw)
                req = DetectFrameRequest(**payload)
            except Exception:
                await websocket.send_json({"error": "Invalid request payload"})
                continue

            frame = decode_jpeg_base64(req.imageBase64)
            if frame is None:
                await websocket.send_json(
                    {"error": "Failed to decode frame", "frameId": req.frameId}
                )
                continue

            frame = resize_frame(frame, settings)
            h, w = frame.shape[:2]
            conf = (
                req.confidence
                if req.confidence is not None
                else settings.default_confidence
            )
            raw_dets = engine.detect(frame, req.classes, conf) if engine else []
            detections = _enrich_detections(req.frameId, raw_dets)
            elapsed = int((time.perf_counter() - start) * 1000)

            resp = DetectFrameResponse(
                frameId=req.frameId,
                sourceFrameWidth=w,
                sourceFrameHeight=h,
                detections=detections,
                processingMs=elapsed,
            )
            await websocket.send_text(resp.model_dump_json(by_alias=False))
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
