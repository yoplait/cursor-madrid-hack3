from src.time_utils import format_seconds


def test_format_seconds_basic():
    assert format_seconds(74) == "00:01:14"


def test_format_seconds_zero():
    assert format_seconds(0) == "00:00:00"


def test_format_seconds_hours():
    assert format_seconds(3661) == "01:01:01"


def test_format_seconds_float_truncated():
    assert format_seconds(74.9) == "00:01:14"


def test_format_seconds_exact_minute():
    assert format_seconds(60) == "00:01:00"


def test_format_seconds_exact_hour():
    assert format_seconds(3600) == "01:00:00"
