"""Tests for baseline computation."""
import pytest
from datetime import date, timedelta
from src.baseline.rolling_window import build_baseline, percentile
from src.persistence.models import DailyFeatures


def sample_features(date_offset: int, total_active: int = 10800) -> DailyFeatures:
    """Create a sample DailyFeatures for testing."""
    d = date.today() - timedelta(days=date_offset)
    return DailyFeatures(
        date=d,
        total_active_sec=total_active,
        total_afk_sec=1200,
        session_count=10,
        avg_session_length_sec=1080,
        median_session_length_sec=1200,
        max_session_length_sec=3600,
        min_session_length_sec=300,
        session_stdev_sec=800,
        first_active="2026-01-08T09:00:00",
        last_active="2026-01-08T18:00:00",
        active_span_sec=32400,
        afk_ratio=0.1,
        break_count=3,
        avg_break_length_sec=400,
        longest_break_sec=1200,
        session_switch_rate=5.0,
        inter_session_gap_mean_sec=300,
        session_length_cv=0.74,
        activity_concentration=0.35,
        productive_sec=7200,
        distracting_sec=2400,
        neutral_sec=1200,
        unknown_sec=0,
        is_weekend=False,
        data_quality="complete"
    )


def test_percentile():
    """Percentile function should work correctly."""
    values = [1, 2, 3, 4, 5]
    assert percentile(values, 10) >= 1
    assert percentile(values, 50) == 3
    assert percentile(values, 90) <= 5


def test_build_baseline_insufficient_data():
    """Should return None with < 3 days."""
    features = [sample_features(1), sample_features(2)]
    result = build_baseline(features, window_days=14)
    assert result is None


def test_build_baseline_basic():
    """Should compute baseline from 7 days of data."""
    features = [sample_features(i) for i in range(1, 8)]
    result = build_baseline(features, window_days=14)
    
    assert result is not None
    assert "avg_session_length_sec" in result
    assert result["avg_session_length_sec"]["mean"] == 1080
    assert result["avg_session_length_sec"]["n_samples"] == 7


def test_build_baseline_filters_insufficient():
    """Should skip days with insufficient data."""
    features = [
        sample_features(1),
        sample_features(2),
        sample_features(3),
        sample_features(4, total_active=10800)  # Sufficient
    ]
    features[1].data_quality = "insufficient"  # This one will be skipped
    
    result = build_baseline(features, window_days=14)
    
    assert result is not None
    # Should include 3 days with sufficient data
    assert result["avg_session_length_sec"]["n_samples"] >= 3


def test_build_baseline_all_features():
    """Baseline should include all monitored features."""
    features = [sample_features(i) for i in range(1, 8)]
    result = build_baseline(features, window_days=14)
    
    expected_features = [
        "avg_session_length_sec",
        "session_switch_rate",
        "afk_ratio",
        "session_length_cv",
        "inter_session_gap_mean_sec",
        "activity_concentration",
    ]
    
    for fname in expected_features:
        assert fname in result
