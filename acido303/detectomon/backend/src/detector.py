import random
import time
from typing import Any

import numpy as np

from .config import Settings


class DetectionEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.confidence_threshold = settings.default_confidence
        self._model: Any = None
        self._use_mock = settings.mock_detection
        if not self._use_mock:
            self._try_load_model()

    def _try_load_model(self) -> None:
        try:
            from libreyolo import LibreYOLO

            self._model = LibreYOLO(self.settings.model_path)
        except Exception as e:
            print(f"[WARN] LibreYOLO unavailable ({e}); enabling mock detection.")
            self._use_mock = True

    @property
    def is_mock(self) -> bool:
        return self._use_mock

    def detect(
        self,
        frame: np.ndarray,
        classes: list[str],
        confidence: float,
    ) -> list[dict]:
        if self._use_mock:
            return self._mock_detect(frame, classes, confidence)
        return self._real_detect(frame, classes, confidence)

    def _real_detect(
        self,
        frame: np.ndarray,
        classes: list[str],
        confidence: float,
    ) -> list[dict]:
        if self._model is None:
            return []

        try:
            results = self._model(frame, conf=confidence)
        except Exception as e:
            print(f"[WARN] inference error: {e}")
            return []

        out: list[dict] = []
        class_filter = {c.lower() for c in classes} if classes else None

        for result in results:
            boxes = getattr(result, "boxes", None)
            names = getattr(result, "names", {})
            if boxes is None:
                continue
            for box in boxes:
                try:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    if conf < confidence:
                        continue
                    xyxy = box.xyxy[0].tolist()
                    class_name = names.get(cls_id, str(cls_id))
                    if class_filter and class_name.lower() not in class_filter:
                        continue
                    out.append(
                        {
                            "className": class_name,
                            "confidence": conf,
                            "box": {
                                "x1": float(xyxy[0]),
                                "y1": float(xyxy[1]),
                                "x2": float(xyxy[2]),
                                "y2": float(xyxy[3]),
                            },
                        }
                    )
                except Exception:
                    continue
        return out

    def _mock_detect(
        self,
        frame: np.ndarray,
        classes: list[str],
        confidence: float,
    ) -> list[dict]:
        h, w = frame.shape[:2]
        labels = classes or [
            "cup",
            "laptop",
            "cell phone",
            "bottle",
            "person",
        ]
        rng = random.Random(int(time.time() * 1000) % 10000)
        count = rng.randint(1, min(3, len(labels)))
        picked = rng.sample(labels, count)
        out: list[dict] = []
        for label in picked:
            bw = rng.randint(int(w * 0.15), int(w * 0.4))
            bh = rng.randint(int(h * 0.15), int(h * 0.4))
            x1 = rng.randint(0, max(1, w - bw))
            y1 = rng.randint(0, max(1, h - bh))
            conf = round(rng.uniform(confidence, min(0.99, confidence + 0.35)), 2)
            out.append(
                {
                    "className": label,
                    "confidence": conf,
                    "box": {
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x1 + bw),
                        "y2": float(y1 + bh),
                    },
                }
            )
        return out
