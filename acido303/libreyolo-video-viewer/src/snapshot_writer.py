import os

import cv2
import numpy as np

from .models import Detection
from .renderer import FrameRenderer


class SnapshotWriter:
    def __init__(self, snapshots_dir: str, annotate: bool = True) -> None:
        self.snapshots_dir = snapshots_dir
        self.annotate = annotate
        self._renderer = FrameRenderer() if annotate else None
        os.makedirs(snapshots_dir, exist_ok=True)
        self._counters: dict[str, int] = {}
        self._manual_counter = 0

    def save(
        self,
        frame: np.ndarray,
        detections: list[Detection],
        seconds: float,
    ) -> dict[str, str]:
        sec_int = int(seconds)
        saved: dict[str, str] = {}

        for det in detections:
            key = f"{sec_int}_{det.class_name}"
            self._counters[key] = self._counters.get(key, 0) + 1
            count = self._counters[key]

            if count == 1:
                fname = f"{sec_int:06d}_{det.class_name}.jpg"
            else:
                fname = f"{sec_int:06d}_{det.class_name}_{count}.jpg"

            fpath = os.path.join(self.snapshots_dir, fname)

            snap = (
                self._renderer.render(frame, [det])
                if self.annotate and self._renderer is not None
                else frame.copy()
            )

            cv2.imwrite(fpath, snap)
            saved[det.class_name] = fpath

        return saved

    def save_manual(self, frame: np.ndarray) -> str:
        self._manual_counter += 1
        fname = f"manual_{self._manual_counter:06d}.jpg"
        fpath = os.path.join(self.snapshots_dir, fname)
        cv2.imwrite(fpath, frame)
        return fpath
