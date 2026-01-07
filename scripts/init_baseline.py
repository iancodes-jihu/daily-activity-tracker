"""Backfill historical daily features from raw logs."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, timedelta
from src.persistence.storage import load_activity_logs, load_daily_features, upsert_daily_features
from src.features.daily_extractor import extract_daily_features


def backfill_features(days_back: int = 30):
    """
    Extract daily features from raw logs for the last N days.
    
    Args:
        days_back: Number of days to backfill
    """
    logs = load_activity_logs()
    existing_features = load_daily_features()
    existing_dates = {f["date"] for f in existing_features}
    
    today = date.today()
    
    print(f"Backfilling last {days_back} days...")
    print(f"Found {len(logs)} raw log entries")
    print(f"Found {len(existing_dates)} existing feature dates")
    
    count = 0
    for i in range(days_back, 0, -1):
        d = today - timedelta(days=i)
        
        if d.isoformat() in existing_dates:
            print(f"  {d}: already exists, skipping")
            continue
        
        features = extract_daily_features(logs, d)
        
        if features:
            upsert_daily_features(features)
            print(f"  {d}: {features.session_count} sessions, {features.total_active_sec}s active")
            count += 1
        else:
            print(f"  {d}: insufficient data (< 5min)")
    
    print(f"\nBackfill complete: {count} new days added")


if __name__ == "__main__":
    backfill_features(days_back=30)
