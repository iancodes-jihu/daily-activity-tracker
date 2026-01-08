"""Daily feature extraction from raw logs."""
from datetime import datetime, date, timedelta
from statistics import mean, median, stdev
from typing import List, Optional, Dict
from src.persistence.models import DailyFeatures


def parse_iso(ts: str) -> datetime:
    """Parse ISO format datetime."""
    return datetime.fromisoformat(ts)


def is_same_day(ts: str, target_date: date) -> bool:
    """Check if timestamp is on target date."""
    return parse_iso(ts).date() == target_date


def get_day_logs(logs: List[Dict], target_date: date) -> List[Dict]:
    """Filter logs for a specific date."""
    return [log for log in logs if is_same_day(log["start"], target_date)]


def extract_daily_features(logs: List[Dict], target_date: date) -> Optional[DailyFeatures]:
    """
    Convert raw logs to daily features.
    
    Returns None if insufficient data.
    """
    # Filter logs for target date
    day_logs = get_day_logs(logs, target_date)
    
    if not day_logs:
        return None
    
    # === Basic time calculations ===
    total_active = sum(log.get("active_sec", 0) for log in day_logs)
    total_afk = sum(log.get("afk_sec", 0) for log in day_logs)
    session_count = len(day_logs)
    
    # === Require minimum activity ===
    if (total_active + total_afk) < 300:  # Less than 5 minutes
        return None
    
    # === Session statistics ===
    session_lengths = [log.get("active_sec", 0) for log in day_logs]
    if not session_lengths:
        return None
    
    avg_session = mean(session_lengths)
    median_session = median(session_lengths)
    max_session = max(session_lengths)
    min_session = min(session_lengths)
    session_stdev = stdev(session_lengths) if len(session_lengths) > 1 else 0.0
    session_cv = session_stdev / avg_session if avg_session > 0 else 0.0
    
    # === Temporal span ===
    first_log = min(day_logs, key=lambda x: parse_iso(x["start"]))
    last_log = max(day_logs, key=lambda x: parse_iso(x["end"]))
    first_active = first_log["start"]
    last_active = last_log["end"]
    active_span = int((parse_iso(last_log["end"]) - parse_iso(first_log["start"])).total_seconds())
    
    # === AFK analysis ===
    afk_periods = [log.get("afk_sec", 0) for log in day_logs if log.get("afk_sec", 0) > 0]
    break_count = sum(1 for log in day_logs if log.get("afk_sec", 0) > 300)
    avg_break = mean(afk_periods) if afk_periods else 0.0
    longest_break = max(afk_periods) if afk_periods else 0
    
    afk_ratio = total_afk / (total_active + total_afk) if (total_active + total_afk) > 0 else 0.0
    
    # === Inter-session gaps ===
    gaps = []
    sorted_logs = sorted(day_logs, key=lambda x: parse_iso(x["end"]))
    for i in range(len(sorted_logs) - 1):
        gap = (parse_iso(sorted_logs[i + 1]["start"]) - parse_iso(sorted_logs[i]["end"])).total_seconds()
        gaps.append(gap)
    avg_gap = mean(gaps) if gaps else 0.0
    
    # === Session switch rate (per active hour) ===
    active_hours = total_active / 3600 if total_active > 0 else 0.0
    switch_rate = session_count / max(1, active_hours)
    
    # === Activity concentration (top 3 sessions) ===
    sorted_sessions = sorted(session_lengths, reverse=True)
    top_3_sum = sum(sorted_sessions[:3])
    activity_concentration = top_3_sum / total_active if total_active > 0 else 0.0
    
    # === Data quality ===
    if total_active >= 3600:  # >= 1 hour
        data_quality = "complete"
    elif total_active >= 300:  # >= 5 minutes
        data_quality = "partial"
    else:
        data_quality = "insufficient"
    
    return DailyFeatures(
        date=target_date,
        total_active_sec=total_active,
        total_afk_sec=total_afk,
        session_count=session_count,
        avg_session_length_sec=avg_session,
        median_session_length_sec=median_session,
        max_session_length_sec=max_session,
        min_session_length_sec=min_session,
        session_stdev_sec=session_stdev,
        first_active=first_active,
        last_active=last_active,
        active_span_sec=active_span,
        afk_ratio=afk_ratio,
        break_count=break_count,
        avg_break_length_sec=avg_break,
        longest_break_sec=longest_break,
        session_switch_rate=switch_rate,
        inter_session_gap_mean_sec=avg_gap,
        session_length_cv=session_cv,
        activity_concentration=activity_concentration,
        is_weekend=target_date.weekday() >= 5,
        data_quality=data_quality
    )
