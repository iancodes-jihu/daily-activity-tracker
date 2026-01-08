"""Pydantic data models for the system."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import List, Optional


class RawLog(BaseModel):
    """Raw event from sensor (one app session)."""
    model_config = ConfigDict(extra="allow")
    
    app: str
    start: str  # ISO format datetime
    end: str  # ISO format datetime
    active_sec: int
    afk_sec: int


class DailyFeatures(BaseModel):
    """Daily behavioral summary (1 row per day)."""
    date: date
    
    # === Time & Activity ===
    total_active_sec: int
    total_afk_sec: int
    session_count: int
    
    # === Session Statistics ===
    avg_session_length_sec: float
    median_session_length_sec: float
    max_session_length_sec: int
    min_session_length_sec: int
    session_stdev_sec: float
    
    # === Temporal ===
    first_active: str  # ISO datetime
    last_active: str  # ISO datetime
    active_span_sec: int
    
    # === AFK & Breaks ===
    afk_ratio: float = Field(ge=0, le=1)
    break_count: int
    avg_break_length_sec: float
    longest_break_sec: int
    
    # === Activity Distribution ===
    session_switch_rate: float
    inter_session_gap_mean_sec: float
    
    # === Temporal Entropy ===
    session_length_cv: float  # Coefficient of variation
    activity_concentration: float = Field(ge=0, le=1)
    
    # (No app-level moral labels — feature set is app-agnostic)
    
    # === Metadata ===
    is_weekend: bool
    data_quality: str  # "complete", "partial", "insufficient"


class Baseline(BaseModel):
    """Per-feature baseline statistics from rolling window."""
    feature_name: str
    values: List[float]
    mean: float
    median: float
    std: float
    iqr: float
    p10: float
    p90: float
    n_samples: int
    last_updated: date


class FeatureDeviation(BaseModel):
    """Single-feature deviation result."""
    feature_name: str
    today_value: float
    baseline_mean: float
    baseline_std: float
    z_score: float
    percentile_rank: int = Field(ge=0, le=100)
    percent_change: float
    # No severity labels or direction fields — numeric-only


class DailyDeviation(BaseModel):
    """Full deviation report for a day."""
    date: date
    feature_deviations: List[FeatureDeviation]
    overall_deviation_score: float
    # No overall status label or free-text explanation stored here
