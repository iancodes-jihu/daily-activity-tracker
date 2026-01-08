"""Tests for feature extraction."""
import pytest
from datetime import date
from src.features.daily_extractor import extract_daily_features


def test_extract_empty_logs():
    """Empty logs should return None."""
    result = extract_daily_features([], date.today())
    assert result is None


def test_extract_insufficient_data():
    """Logs with < 5 minutes total activity should return None."""
    logs = [{
        "app": "notepad.exe",
        "start": "2026-01-08T09:00:00",
        "end": "2026-01-08T09:02:00",  # 2 minutes
        "active_sec": 120,
        "afk_sec": 0
    }]
    result = extract_daily_features(logs, date(2026, 1, 8))
    assert result is None


def test_extract_single_session():
    """Single session should compute features correctly."""
    logs = [{
        "app": "Code.exe",
        "start": "2026-01-08T09:00:00",
        "end": "2026-01-08T10:00:00",
        "active_sec": 3600,
        "afk_sec": 0
    }]
    result = extract_daily_features(logs, date(2026, 1, 8))
    assert result is not None
    assert result.session_count == 1
    assert result.avg_session_length_sec == 3600
    assert result.median_session_length_sec == 3600
    assert result.max_session_length_sec == 3600
    assert result.min_session_length_sec == 3600
    assert result.session_stdev_sec == 0.0
    assert result.total_active_sec == 3600
    assert result.total_afk_sec == 0


def test_extract_multiple_sessions():
    """Multiple sessions should aggregate correctly."""
    logs = [
        {
            "app": "Code.exe",
            "start": "2026-01-08T09:00:00",
            "end": "2026-01-08T10:00:00",
            "active_sec": 3600,
            "afk_sec": 0
        },
        {
            "app": "Chrome.exe",
            "start": "2026-01-08T10:00:00",
            "end": "2026-01-08T10:30:00",
            "active_sec": 1800,
            "afk_sec": 0
        },
        {
            "app": "Code.exe",
            "start": "2026-01-08T10:30:00",
            "end": "2026-01-08T11:30:00",
            "active_sec": 3600,
            "afk_sec": 0
        }
    ]
    result = extract_daily_features(logs, date(2026, 1, 8))
    assert result is not None
    assert result.session_count == 3
    assert result.total_active_sec == 9000
    assert result.avg_session_length_sec == 3000


def test_extract_with_afk():
    """AFK periods should be counted separately."""
    logs = [{
        "app": "Code.exe",
        "start": "2026-01-08T09:00:00",
        "end": "2026-01-08T10:00:00",
        "active_sec": 3600,
        "afk_sec": 600  # 10 minutes AFK
    }]
    result = extract_daily_features(logs, date(2026, 1, 8))
    assert result is not None
    assert result.total_active_sec == 3600
    assert result.total_afk_sec == 600
    assert result.afk_ratio == 600 / 4200  # 0.143


def test_weekend_detection():
    """Weekends should be marked."""
    # 2026-01-10 is Saturday
    logs = [{
        "app": "Code.exe",
        "start": "2026-01-10T09:00:00",
        "end": "2026-01-10T10:00:00",
        "active_sec": 3600,
        "afk_sec": 0
    }]
    result = extract_daily_features(logs, date(2026, 1, 10))
    assert result is not None
    assert result.is_weekend is True


def test_data_quality():
    """Data quality should reflect activity level."""
    # Partial data (5-60 minutes)
    logs = [{
        "app": "Code.exe",
        "start": "2026-01-08T09:00:00",
        "end": "2026-01-08T09:30:00",
        "active_sec": 1800,
        "afk_sec": 0
    }]
    result = extract_daily_features(logs, date(2026, 1, 8))
    assert result is not None
    assert result.data_quality == "partial"
    
    # Complete data (>= 1 hour)
    logs[0]["active_sec"] = 3600
    result = extract_daily_features(logs, date(2026, 1, 8))
    assert result is not None
    assert result.data_quality == "complete"
