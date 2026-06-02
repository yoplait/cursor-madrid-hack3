import colorsys

import cv2
import numpy as np

from .models import Detection


class FrameRenderer:
    def __init__(self) -> None:
        self._colors: dict[str, tuple[int, int, int]] = {}

    def _get_color(self, class_name: str) -> tuple[int, int, int]:
        if class_name not in self._colors:
            hue = (hash(class_name) & 0xFFFF) / 0xFFFF
            r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
            self._colors[class_name] = (int(b * 255), int(g * 255), int(r * 255))
        return self._colors[class_name]

    def render(
        self,
        frame: np.ndarray,
        detections: list[Detection],
        timestamp: str | None = None,
    ) -> np.ndarray:
        out = frame.copy()
        h, w = out.shape[:2]

        for det in detections:
            color = self._get_color(det.class_name)
            x1, y1, x2, y2 = self._clamp_bbox(det.bbox, w, h)

            if x2 <= x1 or y2 <= y1:
                continue

            cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)

            label = f"{det.class_name} {det.confidence:.2f}"
            (tw, th), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            label_y = max(y1 - 4, th + 4)
            cv2.rectangle(
                out,
                (x1, label_y - th - 4),
                (x1 + tw + 2, label_y + baseline),
                color,
                -1,
            )
            cv2.putText(
                out,
                label,
                (x1 + 1, label_y - 1),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        if timestamp is not None:
            self._put_outlined_text(out, timestamp, (10, 25), 0.7)

        self._put_outlined_text(out, f"Détections : {len(detections)}", (10, 50), 0.5)

        return out

    def _clamp_bbox(
        self, bbox: list[float], w: int, h: int
    ) -> tuple[int, int, int, int]:
        if len(bbox) < 4:
            return 0, 0, 0, 0
        x1 = max(0, min(int(bbox[0]), w - 1))
        y1 = max(0, min(int(bbox[1]), h - 1))
        x2 = max(0, min(int(bbox[2]), w - 1))
        y2 = max(0, min(int(bbox[3]), h - 1))
        return x1, y1, x2, y2

    def _put_outlined_text(
        self,
        frame: np.ndarray,
        text: str,
        pos: tuple[int, int],
        scale: float,
    ) -> None:
        cv2.putText(
            frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA
        )
        cv2.putText(
            frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 1, cv2.LINE_AA
        )
