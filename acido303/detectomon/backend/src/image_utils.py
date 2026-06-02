import base64

import cv2
import numpy as np

from .config import Settings


def decode_jpeg_base64(image_b64: str) -> np.ndarray | None:
    try:
        raw = base64.b64decode(image_b64)
        arr = np.frombuffer(raw, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None


def resize_frame(frame: np.ndarray, settings: Settings) -> np.ndarray:
    h, w = frame.shape[:2]
    max_w, max_h = settings.max_frame_width, settings.max_frame_height
    if w <= max_w and h <= max_h:
        return frame
    scale = min(max_w / w, max_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
