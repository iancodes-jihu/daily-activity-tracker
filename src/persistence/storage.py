"""File I/O for JSON data."""
import json
from pathlib import Path
from datetime import date
from typing import List, Optional, Dict
from src.persistence.models import RawLog, DailyFeatures, Baseline, DailyDeviation


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

ACTIVITY_LOG_FILE = DATA_DIR / "activity_log.json"
DAILY_FEATURES_FILE = DATA_DIR / "daily_features.json"
BASELINE_FILE = DATA_DIR / "baseline_window.json"
DEVIATION_LOG_FILE = DATA_DIR / "deviation_log.json"


def load_activity_logs() -> List[Dict]:
    """Load raw activity logs from disk."""
    try:
        with open(ACTIVITY_LOG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_activity_logs(logs: List[Dict]) -> None:
    """Save raw activity logs to disk."""
    with open(ACTIVITY_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def append_activity_log(log: Dict) -> None:
    """Append a single log entry."""
    logs = load_activity_logs()
    logs.append(log)
    save_activity_logs(logs)


def load_daily_features() -> List[Dict]:
    """Load daily features from disk."""
    try:
        with open(DAILY_FEATURES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_daily_features(features_list: List[Dict]) -> None:
    """Save daily features to disk."""
    with open(DAILY_FEATURES_FILE, "w") as f:
        json.dump(features_list, f, indent=2, default=str)


def get_daily_features(target_date: date) -> Optional[Dict]:
    """Get features for a specific date."""
    features_list = load_daily_features()
    for f in features_list:
        if f["date"] == target_date.isoformat():
            return f
    return None


def upsert_daily_features(features: DailyFeatures) -> None:
    """Insert or update daily features for a date."""
    features_list = load_daily_features()
    
    # Remove existing entry for this date
    features_list = [f for f in features_list if f["date"] != features.date.isoformat()]
    
    # Add new entry
    features_dict = json.loads(features.json())
    features_dict["date"] = features.date.isoformat()
    features_list.append(features_dict)
    
    # Sort by date
    features_list.sort(key=lambda x: x["date"])
    
    save_daily_features(features_list)


def load_baseline() -> Optional[Dict[str, Dict]]:
    """Load current baseline from disk."""
    try:
        with open(BASELINE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def save_baseline(baseline: Dict[str, Dict]) -> None:
    """Save baseline to disk."""
    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=2, default=str)


def load_deviation_log() -> List[Dict]:
    """Load deviation log from disk."""
    try:
        with open(DEVIATION_LOG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_deviation_log(deviations: List[Dict]) -> None:
    """Save deviation log to disk."""
    with open(DEVIATION_LOG_FILE, "w") as f:
        json.dump(deviations, f, indent=2, default=str)


def append_deviation(deviation: DailyDeviation) -> None:
    """Append deviation report to log."""
    dev_list = load_deviation_log()
    dev_dict = json.loads(deviation.json())
    dev_dict["date"] = deviation.date.isoformat()
    dev_list.append(dev_dict)
    save_deviation_log(dev_list)
