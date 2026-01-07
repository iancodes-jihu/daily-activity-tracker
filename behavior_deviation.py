from datetime import datetime, date, timedelta
from collections import defaultdict
import math

# -----------------------------
# Helpers
# -----------------------------

def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts)

def is_same_day(ts: str, target_date: date) -> bool:
    return parse_iso(ts).date() == target_date

def get_day_logs(logs, target_date: date):
    return [log for log in logs if is_same_day(log["start"], target_date)]

def seconds(log):
    return log.get("active_sec", 0), log.get("afk_sec", 0)

# -----------------------------
# Metric extraction
# -----------------------------

def extract_metrics(logs):
    """
    Returns behavior metrics for a set of logs (1 day).
    """
    if not logs:
        return None

    total_active = 0
    total_afk = 0
    sessions = []
    app_switches = 0

    last_app = None

    for log in logs:
        active, afk = seconds(log)
        total_active += active
        total_afk += afk

        duration = active + afk
        if duration > 0:
            sessions.append(duration)

        if last_app and log["app"] != last_app:
            app_switches += 1
        last_app = log["app"]

    avg_session = sum(sessions) / len(sessions) if sessions else 0

    return {
        "total_active": total_active,
        "afk_ratio": total_afk / (total_active + total_afk) if (total_active + total_afk) else 0,
        "avg_session": avg_session,
        "switch_rate": app_switches / max(1, total_active / 3600)  # per active hour
    }

# -----------------------------
# Baseline computation
# -----------------------------

def build_baseline(logs, days: int, today: date):
    """
    Rolling baseline from previous N days.
    """
    metrics = defaultdict(list)

    for i in range(1, days + 1):
        d = today - timedelta(days=i)
        day_logs = get_day_logs(logs, d)
        m = extract_metrics(day_logs)
        if not m:
            continue
        for k, v in m.items():
            metrics[k].append(v)

    if not metrics:
        return None

    baseline = {}
    for k, values in metrics.items():
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = math.sqrt(variance)
        baseline[k] = {
            "mean": mean,
            "std": std
        }

    return baseline

# -----------------------------
# Deviation detection
# -----------------------------

def detect_deviation(today_metrics, baseline, z_threshold=2.0):
    """
    Z-score based deviation detection.
    """
    deviations = []

    for key, base in baseline.items():
        mean = base["mean"]
        std = base["std"]

        if std == 0:
            continue

        z = (today_metrics[key] - mean) / std

        if abs(z) >= z_threshold:
            deviations.append({
                "metric": key,
                "z_score": round(z, 2),
                "today": round(today_metrics[key], 2),
                "baseline_mean": round(mean, 2)
            })

    return deviations

# -----------------------------
# Public API
# -----------------------------

def analyze_today(logs, baseline_days=6):
    today = date.today()

    today_logs = get_day_logs(logs, today)
    today_metrics = extract_metrics(today_logs)

    if not today_metrics:
        return {
            "status": "no_data",
            "message": "Tidak ada data hari ini."
        }

    baseline = build_baseline(logs, baseline_days, today)

    if not baseline:
        return {
            "status": "no_baseline",
            "message": "Baseline belum cukup."
        }

    deviations = detect_deviation(today_metrics, baseline)

    return {
        "status": "deviation_detected" if deviations else "stable",
        "today": today_metrics,
        "deviations": deviations
    }
