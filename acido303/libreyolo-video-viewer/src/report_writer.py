import json
import os

from .event_builder import summarize_events
from .models import DetectionEvent


def write_report(
    output_path: str,
    video_meta: dict,
    analysis_settings: dict,
    outputs: dict,
    events: list[DetectionEvent],
) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    report = {
        "video": video_meta,
        "analysis": analysis_settings,
        "outputs": outputs,
        "summary": {
            "total_events": len(events),
            "classes_detected": summarize_events(events),
        },
        "events": [e.model_dump() for e in events],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
