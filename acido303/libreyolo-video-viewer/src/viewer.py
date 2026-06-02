from typing import Callable

import cv2
import numpy as np


class VideoViewer:
    WINDOW_NAME = "LibreYOLO Video-Viewer"

    def __init__(
        self,
        fps: float,
        snapshot_callback: Callable[[np.ndarray], None] | None = None,
    ) -> None:
        self.fps = fps
        self.snapshot_callback = snapshot_callback
        self._paused = False
        self._frame_delay_ms = max(1, int(1000.0 / fps))
        self._initialized = False

    def init(self) -> None:
        try:
            cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Viewer-Fenster kann nicht geöffnet werden: {e}") from e

    def show(self, frame: np.ndarray) -> bool:
        """Display frame; returns False when the user requests quit."""
        if not self._initialized:
            self.init()

        cv2.imshow(self.WINDOW_NAME, frame)

        if self._paused:
            while True:
                key = cv2.waitKey(50) & 0xFF
                if key == ord("q"):
                    return False
                if key == ord(" "):
                    self._paused = False
                    break
                if key == ord("s") and self.snapshot_callback is not None:
                    self.snapshot_callback(frame)
                if cv2.getWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                    return False
        else:
            key = cv2.waitKey(self._frame_delay_ms) & 0xFF
            if key == ord("q"):
                return False
            if key == ord(" "):
                self._paused = True
            elif key == ord("s") and self.snapshot_callback is not None:
                self.snapshot_callback(frame)

        if cv2.getWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            return False

        return True

    def close(self) -> None:
        if self._initialized:
            cv2.destroyWindow(self.WINDOW_NAME)
            self._initialized = False
