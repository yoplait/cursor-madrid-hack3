from pydantic import BaseModel, Field


class Box(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class DetectionOut(BaseModel):
    id: str
    className: str
    confidence: float
    box: Box
    knownObject: bool = False
    cardId: str | None = None


class DetectFrameRequest(BaseModel):
    frameId: int
    imageBase64: str
    classes: list[str] = Field(default_factory=list)
    confidence: float | None = None


class DetectFrameResponse(BaseModel):
    frameId: int
    sourceFrameWidth: int
    sourceFrameHeight: int
    detections: list[DetectionOut]
    processingMs: int


class GenerateCardRequest(BaseModel):
    detectionId: str
    className: str
    confidence: float
    box: Box


class CardOut(BaseModel):
    cardId: str
    name: str
    className: str
    detectionId: str
    reused: bool = False
    imageUrl: str | None = None


class GenerateCardResponse(BaseModel):
    card: CardOut
    message: str
