"""Human-readable explanations for deviations."""
from typing import List
from src.persistence.models import FeatureDeviation


def generate_summary(feature_devs: List[FeatureDeviation], status: str) -> str:
    """
    Generate English-language interpretation of deviations.
    
    Args:
        feature_devs: List of feature deviations
        status: Overall status (on_track, warning, critical)
    
    Returns:
        Human-readable explanation
    """
    explanations = []
    
    for dev in feature_devs:
        if dev.severity == "normal":
            continue
        
        fname = dev.feature_name
        today = dev.today_value
        baseline = dev.baseline_mean
        pct = dev.percent_change
        
        # Metric-specific explanations
        if fname == "avg_session_length_sec":
            baseline_min = baseline / 60
            today_min = today / 60
            explanations.append(
                f"⚠️  Sessions shortened: {today_min:.0f}m avg vs {baseline_min:.0f}m baseline ({pct:+.0f}%)\n"
                f"   → Possible loss of focus or more fragmentation"
            )
        
        elif fname == "session_switch_rate":
            explanations.append(
                f"⚠️  App switches increased: {today:.1f} per hour vs {baseline:.1f} baseline ({pct:+.0f}%)\n"
                f"   → More context-switching, possible distraction"
            )
        
        elif fname == "afk_ratio":
            pct_afk_today = today * 100
            pct_afk_baseline = baseline * 100
            explanations.append(
                f"⚠️  Off-screen time increased: {pct_afk_today:.0f}% vs {pct_afk_baseline:.0f}% baseline\n"
                f"   → More breaks, fatigue, or system idle"
            )
        
        elif fname == "session_length_cv":
            explanations.append(
                f"⚠️  Session consistency dropped: CV {today:.2f} vs {baseline:.2f}\n"
                f"   → Erratic work rhythm; mixing focused and fragmented sessions"
            )
        
        elif fname == "inter_session_gap_mean_sec":
            gap_min = today / 60
            baseline_min = baseline / 60
            explanations.append(
                f"⚠️  Session gaps increased: {gap_min:.1f}m avg vs {baseline_min:.1f}m baseline\n"
                f"   → More fragmented workflow, longer pauses between tasks"
            )
    
    # Build final message
    status_msg = {
        "critical": "🚨 CRITICAL: Multiple significant deviations detected.",
        "warning": "⚠️ WARNING: Some deviations from your baseline.",
        "on_track": "✅ On track: All metrics within normal range."
    }
    
    if not explanations:
        return status_msg[status]
    
    return status_msg[status] + "\n\n" + "\n\n".join(explanations)
