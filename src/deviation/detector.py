"""Deviation detection logic."""
from typing import List, Dict, Optional
from src.persistence.models import DailyFeatures, FeatureDeviation, DailyDeviation


def percentile_rank(value: float, values: List[float]) -> int:
    """Calculate percentile rank of value within list (0-100)."""
    if not values:
        return 50
    sorted_vals = sorted(values)
    rank = sum(1 for v in sorted_vals if v <= value) / len(sorted_vals) * 100
    return int(rank)


def detect_deviation(today_features: DailyFeatures,
                     baseline: Dict[str, Dict],
                     z_threshold: float = 2.0) -> DailyDeviation:
    """
    Detect deviations using z-scores.
    
    Args:
        today_features: Today's computed features
        baseline: Rolling baseline stats {feature_name: {mean, std, ...}}
        z_threshold: Z-score threshold for alerting
    
    Returns:
        DailyDeviation with severity and explanation
    """
    feature_devs = []
    weighted_score = 0.0
    
    # Define which features to monitor and their alert direction
    feature_specs = [
        ("avg_session_length_sec", "below"),      # Alert if sessions got shorter
        ("session_switch_rate", "above"),         # Alert if switching increased
        ("afk_ratio", "above"),                   # Alert if AFK increased
        ("session_length_cv", "above"),           # Alert if inconsistency increased
        ("inter_session_gap_mean_sec", "above"),  # Alert if gaps increased (fragmented)
    ]
    
    for fname, alert_direction in feature_specs:
        today_val = getattr(today_features, fname)
        base = baseline.get(fname)
        
        if not base or base.get("std", 0) == 0:
            continue  # Skip if no baseline
        
        mean_val = base["mean"]
        std_val = base["std"]
        baseline_values = base.get("values", [])
        
        # Calculate z-score
        if std_val > 0:
            z = (today_val - mean_val) / std_val
        else:
            z = 0.0
        
        # Calculate percent change
        if mean_val != 0:
            percent_chg = (today_val - mean_val) / mean_val * 100
        else:
            percent_chg = 0.0
        
        # Get percentile rank
        pctl = percentile_rank(today_val, baseline_values) if baseline_values else 50

        feature_devs.append(FeatureDeviation(
            feature_name=fname,
            today_value=round(today_val, 2),
            baseline_mean=round(mean_val, 2),
            baseline_std=round(std_val, 2),
            z_score=round(z, 2),
            percentile_rank=pctl,
            percent_change=round(percent_chg, 1),
        ))

        # Accumulate absolute z for an overall numeric score
        weighted_score += abs(z)
    
    # Return numeric-only deviation report (no moral labels)
    return DailyDeviation(
        date=today_features.date,
        feature_deviations=feature_devs,
        overall_deviation_score=weighted_score,
    )
