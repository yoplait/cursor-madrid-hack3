from src.event_builder import build_events, filter_detections, summarize_events
from src.models import Detection, DetectionEvent


def _det(class_name: str, confidence: float = 0.9) -> Detection:
    return Detection(class_name=class_name, confidence=confidence, bbox=[0.0, 0.0, 10.0, 10.0])


def test_filter_keeps_matching_class():
    dets = [_det("Person"), _det("car"), _det("dog")]
    result = filter_detections(dets, ["person", "dog"])
    names = [d.class_name for d in result]
    assert "Person" in names
    assert "dog" in names
    assert "car" not in names


def test_filter_case_insensitive():
    dets = [_det("Person")]
    assert filter_detections(dets, ["person"]) == dets
    assert filter_detections(dets, ["PERSON"]) == dets


def test_filter_empty_classes_keeps_all():
    dets = [_det("person"), _det("car")]
    assert filter_detections(dets, []) == dets


def test_filter_rejects_unmatched():
    dets = [_det("car")]
    assert filter_detections(dets, ["person", "dog"]) == []


def test_build_events_count():
    dets = [_det("person"), _det("dog")]
    events = build_events(dets, frame_index=90, fps=30.0)
    assert len(events) == 2


def test_build_events_timestamp():
    dets = [_det("person")]
    events = build_events(dets, frame_index=90, fps=30.0)
    assert events[0].timestamp == "00:00:03"
    assert events[0].seconds == 3.0


def test_summarize_events():
    events = [
        DetectionEvent(
            timestamp="00:00:01", seconds=1.0, frame_index=30,
            class_name="person", confidence=0.9, bbox=[0, 0, 10, 10],
        ),
        DetectionEvent(
            timestamp="00:00:02", seconds=2.0, frame_index=60,
            class_name="person", confidence=0.8, bbox=[0, 0, 10, 10],
        ),
        DetectionEvent(
            timestamp="00:00:03", seconds=3.0, frame_index=90,
            class_name="dog", confidence=0.7, bbox=[0, 0, 10, 10],
        ),
    ]
    summary = summarize_events(events)
    assert summary == {"person": 2, "dog": 1}


def test_summarize_empty():
    assert summarize_events([]) == {}
