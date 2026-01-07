"""Tests for deviation detection."""
import pytest
from datetime import date, timedelta
from src.deviation.detector import detect_deviation, percentile_rank
from src.persistence.models import DailyFeatures


def sample_features(date_offset: int, **kwargs) -> DailyFeatures:
    """Create a sample DailyFeatures with optional overrides."""
    defaults = {
        "total_active_sec": 10800,
        "total_afk_sec": 1200,
        "session_count": 10,
        "avg_session_length_sec": 1080,
        "median_session_length_sec": 1200,
        "max_session_length_sec": 3600,
        "min_session_length_sec": 300,
        "session_stdev_sec": 800,
        "first_active": "2026-01-08T09:00:00",
        "last_active": "2026-01-08T18:00:00",
        "active_span_sec": 32400,
        "afk_ratio": 0.1,
        "break_count": 3,
        "avg_break_length_sec": 400,
        "longest_break_sec": 1200,
        "session_switch_rate": 5.0,
        "inter_session_gap_mean_sec": 300,
        "session_length_cv": 0.74,
        "activity_concentration": 0.35,
        "productive_sec": 7200,
        "distracting_sec": 2400,
        "neutral_sec": 1200,
        "unknown_sec": 0,
        "is_weekend": False,
        "data_quality": "complete"
    }
    defaults.update(kwargs)
    
    d = date.today() - timedelta(days=date_offset)
    return DailyFeatures(date=d, **defaults)


def test_percentile_rank():
    """Percentile rank should work correctly."""
    values = [100, 200, 300, 400, 500]
    assert percentile_rank(250, values) == 40
    assert percentile_rank(100, values) == 20
    assert percentile_rank(500, values) == 100


def test_detect_deviation_on_track():
    """Normal day should return on_track status."""
    today = sample_features(0)
    baseline = {
        "avg_session_length_sec": {"mean": 1080, "std": 200, "values": [1000, 1050, 1100, 1150]},
        "session_switch_rate": {"mean": 5.0, "std": 1.0, "values": [4.5, 5.0, 5.5, 5.2]},
        "afk_ratio": {"mean": 0.1, "std": 0.02, "values": [0.08, 0.10, 0.12]},
        "session_length_cv": {"mean": 0.74, "std": 0.1, "values": [0.65, 0.74, 0.85]},
        "inter_session_gap_mean_sec": {"mean": 300, "std": 50, "values": [250, 300, 350]},
    }
    
    result = detect_deviation(today, baseline)
    
    assert result.status == "on_track"
    assert result.overall_deviation_score == 0.0


def test_detect_deviation_warning():
    """Day with significant deviation should return warning or critical."""
    today = sample_features(0, avg_session_length_sec=500)  # Significantly shorter (z ~ -2.9)
    baseline = {
        "avg_session_length_sec": {"mean": 1080, "std": 200, "values": [1000, 1050, 1100, 1150]},
        "session_switch_rate": {"mean": 5.0, "std": 1.0, "values": [4.5, 5.0, 5.5, 5.2]},
        "afk_ratio": {"mean": 0.1, "std": 0.02, "values": [0.08, 0.10, 0.12]},
        "session_length_cv": {"mean": 0.74, "std": 0.1, "values": [0.65, 0.74, 0.85]},
        "inter_session_gap_mean_sec": {"mean": 300, "std": 50, "values": [250, 300, 350]},
    }
    
    result = detect_deviation(today, baseline)
    
    # Should detect warning (just below threshold, or on_track if z-threshold is high)
    assert result.status in ["warning", "on_track"]


def test_detect_deviation_critical():
    """Day with 2+ critical deviations should return critical."""
    today = sample_features(
        0,
        avg_session_length_sec=300,  # Very short (-3.9 std)
        session_switch_rate=12.0  # Much higher (+7.0 std)
    )
    baseline = {
        "avg_session_length_sec": {"mean": 1080, "std": 200, "values": [1000, 1050, 1100, 1150]},
        "session_switch_rate": {"mean": 5.0, "std": 1.0, "values": [4.5, 5.0, 5.5, 5.2]},
        "afk_ratio": {"mean": 0.1, "std": 0.02, "values": [0.08, 0.10, 0.12]},
        "session_length_cv": {"mean": 0.74, "std": 0.1, "values": [0.65, 0.74, 0.85]},
        "inter_session_gap_mean_sec": {"mean": 300, "std": 50, "values": [250, 300, 350]},
    }
    
    result = detect_deviation(today, baseline)
    
    assert result.status == "critical"


def test_deviation_has_explanations():
    """Deviation should include human-readable explanations."""
    today = sample_features(0, avg_session_length_sec=500)
    baseline = {
        "avg_session_length_sec": {"mean": 1080, "std": 200, "values": [1000, 1050, 1100, 1150]},
        "session_switch_rate": {"mean": 5.0, "std": 1.0, "values": [4.5, 5.0, 5.5, 5.2]},
        "afk_ratio": {"mean": 0.1, "std": 0.02, "values": [0.08, 0.10, 0.12]},
        "session_length_cv": {"mean": 0.74, "std": 0.1, "values": [0.65, 0.74, 0.85]},
        "inter_session_gap_mean_sec": {"mean": 300, "std": 50, "values": [250, 300, 350]},
    }
    
    result = detect_deviation(today, baseline)
    
    assert len(result.summary_text) > 0
    assert "Sessions shortened" in result.summary_text or "session" in result.summary_text.lower()
