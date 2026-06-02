from .models import Detection, DetectionEvent
from .time_utils import format_seconds


def filter_detections(
    detections: list[Detection], classes: list[str]
) -> list[Detection]:
    if not classes:
        return detections
    lower = {c.lower() for c in classes}
    return [d for d in detections if d.class_name.lower() in lower]


def build_events(
    detections: list[Detection],
    frame_index: int,
    fps: float,
    snapshot_paths: dict[str, str] | None = None,
) -> list[DetectionEvent]:
    seconds = frame_index / fps if fps > 0 else 0.0
    timestamp = format_seconds(seconds)
    events: list[DetectionEvent] = []

    for det in detections:
        snapshot_path = (snapshot_paths or {}).get(det.class_name)
        events.append(
            DetectionEvent(
                timestamp=timestamp,
                seconds=round(seconds, 3),
                frame_index=frame_index,
                class_name=det.class_name,
                confidence=det.confidence,
                bbox=det.bbox,
                snapshot_path=snapshot_path,
            )
        )

    return events


def summarize_events(events: list[DetectionEvent]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        counts[event.class_name] = counts.get(event.class_name, 0) + 1
    return counts
