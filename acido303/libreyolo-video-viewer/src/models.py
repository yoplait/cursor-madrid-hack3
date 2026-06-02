from pydantic import BaseModel


class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float]  # [x1, y1, x2, y2]


class DetectionEvent(BaseModel):
    timestamp: str
    seconds: float
    frame_index: int
    class_name: str
    confidence: float
    bbox: list[float]
    snapshot_path: str | None = None
