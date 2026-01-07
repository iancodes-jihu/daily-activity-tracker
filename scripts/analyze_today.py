"""Daily analysis script: extract features, build baseline, and detect deviations."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date
from src.persistence.storage import (
    load_activity_logs, load_daily_features, upsert_daily_features,
    load_baseline, save_baseline, append_deviation
)
from src.features.daily_extractor import extract_daily_features
from src.baseline.rolling_window import build_baseline
from src.deviation.detector import detect_deviation


def analyze_today():
    """
    Main analysis pipeline for today:
    1. Extract today's features from raw logs
    2. Rebuild baseline from last 14 days
    3. Detect deviations for today
    4. Save results
    """
    from src.persistence.models import DailyFeatures as DF
    from datetime import datetime
    
    today = date.today()
    
    print(f"\n📊 Daily Analysis for {today}")
    print("=" * 60)
    
    # Load raw logs
    logs = load_activity_logs()
    print(f"✓ Loaded {len(logs)} raw log entries")
    
    # Extract today's features
    today_features = extract_daily_features(logs, today)
    
    if not today_features:
        print(f"⚠️  Insufficient data for {today} (< 5 min activity)")
        return
    
    print(f"✓ Extracted today's features")
    print(f"  - Sessions: {today_features.session_count}")
    print(f"  - Active: {today_features.total_active_sec / 60:.0f} minutes")
    print(f"  - Avg session: {today_features.avg_session_length_sec / 60:.1f} min")
    print(f"  - Switch rate: {today_features.session_switch_rate:.1f} /hour")
    print(f"  - AFK ratio: {today_features.afk_ratio * 100:.1f}%")
    
    # Save features
    upsert_daily_features(today_features)
    print(f"✓ Saved daily features")
    
    # Load and convert historical features to objects
    features_dicts = load_daily_features()
    all_features = []
    for f in features_dicts:
        try:
            obj = DF(**f)
            all_features.append(obj)
        except Exception as e:
            print(f"⚠️  Skipping malformed feature: {e}")
    
    print(f"✓ Loaded {len(all_features)} historical feature dates")
    
    # Build baseline
    baseline = build_baseline(all_features, window_days=14, today=today)
    
    if not baseline:
        print(f"⚠️  Insufficient baseline data (need 3+ days)")
        return
    
    print(f"✓ Built baseline from {baseline.get(list(baseline.keys())[0], {}).get('n_samples', 0)} days")
    save_baseline(baseline)
    
    # Detect deviations
    deviation = detect_deviation(today_features, baseline)
    print(f"\n🔍 Deviation Analysis")
    print("=" * 60)
    print(deviation.summary_text)
    print(f"\nStatus: {deviation.status.upper()}")
    print(f"Overall score: {deviation.overall_deviation_score:.2f}")
    
    # Save deviation report
    append_deviation(deviation)
    print(f"\n✓ Deviation report saved")


if __name__ == "__main__":
    analyze_today()
