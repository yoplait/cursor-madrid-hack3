import numpy as np
import pytest

from src.models import Detection
from src.renderer import FrameRenderer


def _blank_frame(h: int = 480, w: int = 640) -> np.ndarray:
    return np.zeros((h, w, 3), dtype=np.uint8)


def _det(bbox: list[float], class_name: str = "person") -> Detection:
    return Detection(class_name=class_name, confidence=0.85, bbox=bbox)


def test_render_returns_same_shape():
    renderer = FrameRenderer()
    frame = _blank_frame()
    result = renderer.render(frame, [_det([100.0, 50.0, 300.0, 400.0])])
    assert result.shape == frame.shape


def test_render_does_not_modify_original():
    renderer = FrameRenderer()
    frame = _blank_frame()
    original = frame.copy()
    renderer.render(frame, [_det([100.0, 50.0, 300.0, 400.0])])
    assert np.array_equal(frame, original)


def test_render_empty_detections():
    renderer = FrameRenderer()
    frame = _blank_frame()
    result = renderer.render(frame, [])
    assert result.shape == frame.shape


def test_clamp_bbox_within_frame():
    renderer = FrameRenderer()
    x1, y1, x2, y2 = renderer._clamp_bbox([-50.0, -20.0, 700.0, 500.0], w=640, h=480)
    assert x1 >= 0
    assert y1 >= 0
    assert x2 <= 639
    assert y2 <= 479


def test_clamp_bbox_large_out_of_bounds():
    renderer = FrameRenderer()
    x1, y1, x2, y2 = renderer._clamp_bbox([0.0, 0.0, 9999.0, 9999.0], w=640, h=480)
    assert x2 <= 639
    assert y2 <= 479


def test_render_with_out_of_bounds_bbox_does_not_crash():
    renderer = FrameRenderer()
    frame = _blank_frame()
    det = _det([-999.0, -999.0, 9999.0, 9999.0])
    result = renderer.render(frame, [det])
    assert result is not None


def test_render_with_timestamp():
    renderer = FrameRenderer()
    frame = _blank_frame()
    result = renderer.render(frame, [], timestamp="00:01:14")
    assert result.shape == frame.shape


def test_clamp_bbox_malformed_short():
    renderer = FrameRenderer()
    result = renderer._clamp_bbox([10.0, 20.0], w=640, h=480)
    assert result == (0, 0, 0, 0)
