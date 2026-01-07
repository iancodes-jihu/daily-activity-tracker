from datetime import date
from statistics import mean, stdev

class DeviationTracker:
    def __init__(self, daily_target: dict):
        self.productive_target = daily_target["productive_min_minutes"]
        self.max_distracting = daily_target["max_distracting_minutes"]

    def analyze_day(self, today_summary: dict, history: list[dict]) -> dict:
        """
        today_summary:
        {
            "date": "2026-01-06",
            "productive": 130,
            "distracting": 40,
            "afk": 25
        }

        history: list of previous daily summaries (same format)
        """

        signals = []

        # --- 1. Target deviation ---
        if today_summary["productive"] < self.productive_target:
            signals.append("below_productive_target")

        if today_summary["distracting"] > self.max_distracting:
            signals.append("excessive_distraction")

        # --- 2. Trend deviation (last 7 days) ---
        last_7 = history[-7:]
        if len(last_7) >= 3:
            avg_prod = mean(d["productive"] for d in last_7)
            if today_summary["productive"] < avg_prod * 0.85:
                signals.append("productivity_drop_vs_baseline")

        # --- 3. Consistency deviation ---
        if len(last_7) >= 5:
            prod_values = [d["productive"] for d in last_7]
            if stdev(prod_values) > 0.3 * mean(prod_values):
                signals.append("inconsistent_productivity")

        # --- 4. Overall deviation score ---
        deviation_score = len(signals)

        return {
            "date": today_summary["date"],
            "deviation_score": deviation_score,
            "signals": signals,
            "status": self._status_from_score(deviation_score)
        }

    def compare_weeks(self, week1: list[dict], week2: list[dict]) -> dict:
        avg1 = mean(d["productive"] for d in week1)
        avg2 = mean(d["productive"] for d in week2)

        delta = avg2 - avg1

        return {
            "week1_avg": avg1,
            "week2_avg": avg2,
            "delta": delta,
            "trend": "improving" if delta > 0 else "declining"
        }

    def _status_from_score(self, score: int) -> str:
        if score == 0:
            return "on_track"
        elif score <= 2:
            return "warning"
        else:
            return "critical"
