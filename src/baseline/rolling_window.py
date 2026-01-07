"""Rolling baseline computation."""
from datetime import date, timedelta
from statistics import mean, median, stdev
from typing import List, Optional, Dict
from src.persistence.models import DailyFeatures, Baseline


def percentile(values: List[float], p: int) -> float:
    """Calculate percentile (0-100)."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    rank = (p / 100.0) * len(sorted_vals)
    if rank == int(rank):
        return sorted_vals[int(rank) - 1]
    return sorted_vals[int(rank)]


def build_baseline(daily_features_list: List[DailyFeatures],
                   window_days: int = 14,
                   today: date = None) -> Optional[Dict[str, Dict]]:
    """
    Build rolling baseline from historical daily features.
    
    Args:
        daily_features_list: List of all daily features
        window_days: Number of days to look back
        today: Reference date (default: today)
    
    Returns:
        Dict mapping feature_name -> {mean, median, std, iqr, p10, p90, etc.}
    """
    if not today:
        today = date.today()
    
    # Get last N days of features (exclude insufficient data)
    cutoff = today - timedelta(days=window_days)
    recent = [f for f in daily_features_list 
              if f.date > cutoff and f.data_quality != "insufficient"]
    
    if len(recent) < 3:
        return None  # Not enough data
    
    baselines = {}
    
    feature_names = [
        "avg_session_length_sec",
        "session_switch_rate",
        "afk_ratio",
        "session_length_cv",
        "inter_session_gap_mean_sec",
        "activity_concentration",
    ]
    
    for fname in feature_names:
        values = [getattr(f, fname) for f in recent]
        
        if not values:
            continue
        
        mean_val = mean(values)
        median_val = median(values)
        std_val = stdev(values) if len(values) > 1 else 0.0
        iqr_val = percentile(values, 75) - percentile(values, 25)
        p10_val = percentile(values, 10)
        p90_val = percentile(values, 90)
        
        baselines[fname] = {
            "mean": mean_val,
            "median": median_val,
            "std": std_val,
            "iqr": iqr_val,
            "p10": p10_val,
            "p90": p90_val,
            "n_samples": len(values),
            "values": values  # Keep for debugging
        }
    
    return baselines if baselines else None
