import os
import cv2
from dataclasses import dataclass


@dataclass
class VideoMetadata:
    path: str
    fps: float
    frame_count: int
    width: int
    height: int
    duration_seconds: float


def open_video(path: str) -> tuple[cv2.VideoCapture, VideoMetadata]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Video file not found: {path}")

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video file: {path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        cap.release()
        raise RuntimeError(f"Invalid FPS ({fps}) in video file: {path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_seconds = frame_count / fps

    metadata = VideoMetadata(
        path=path,
        fps=fps,
        frame_count=frame_count,
        width=width,
        height=height,
        duration_seconds=duration_seconds,
    )

    return cap, metadata
