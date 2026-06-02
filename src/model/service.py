"""LibreYOLO inference helpers shared by CLI scripts and the backend."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LIBREYOLO_ROOT = ROOT / "vendor" / "libreyolo"
DEFAULT_MODEL = os.environ.get("LIBREYOLO_MODEL", "LibreYOLO9t.pt")


def resolve_weights(name: str | None = None) -> Path:
    model_name = name or DEFAULT_MODEL
    for candidate in (
        Path(model_name),
        LIBREYOLO_ROOT / "weights" / model_name,
        LIBREYOLO_ROOT / model_name,
    ):
        if candidate.is_file():
            return candidate.resolve()
    return (LIBREYOLO_ROOT / "weights" / model_name).resolve()


@lru_cache(maxsize=1)
def get_model(model_name: str | None = None):
    from libreyolo import LibreYOLO

    weights = resolve_weights(model_name)
    return LibreYOLO(str(weights))


def detect(source: Any, *, conf: float = 0.25, save: bool = False, model_name: str | None = None):
    return get_model(model_name)(source, conf=conf, save=save)


def result_to_dict(result) -> dict:
    boxes = []
    if result.boxes is not None and len(result.boxes):
        for i in range(len(result.boxes)):
            cls_id = int(result.boxes.cls[i].item())
            boxes.append(
                {
                    "class_id": cls_id,
                    "class_name": result.names.get(cls_id, str(cls_id)),
                    "confidence": float(result.boxes.conf[i].item()),
                    "bbox": [float(v) for v in result.boxes.xyxy[i].tolist()],
                }
            )
    payload: dict = {
        "path": result.path,
        "count": len(boxes),
        "boxes": boxes,
    }
    saved_path = getattr(result, "saved_path", None)
    if saved_path:
        payload["saved_path"] = saved_path
    return payload
