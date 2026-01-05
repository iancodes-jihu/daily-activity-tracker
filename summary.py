import json
from datetime import date
from tracker import load_logs, load_target

def daily_summary(logs):
    today = date.today().isoformat()
    summary = {
        "productive": 0,
        "distracting": 0,
        "neutral": 0,
        "unknown": 0
    }

    for log in logs:
        # Validate required fields
        if "category" not in log or "active_sec" not in log:
            continue

        # Check if the log is from today
        if not log.get("start", "").startswith(today):
            continue

        # Add active time to the appropriate category
        category = log["category"]
        summary[category] = summary.get(category, 0) + log["active_sec"]

    return summary

def print_summary(summary):
    def to_min(sec): 
        return round(sec / 60, 1)

    print("\n=== DAILY SUMMARY ===")
    print(f"Produktif : {to_min(summary['productive'])} menit")
    print(f"Distraksi : {to_min(summary['distracting'])} menit")
    print(f"Netral    : {to_min(summary['neutral'])} menit")

    if summary["distracting"] > summary["productive"]:
        print("Kesimpulan: kamu sibuk, tapi bukan maju.")
    else:
        print("Kesimpulan: masih ada niat hidup lebih baik.")

    
def evaluate_target(summary, target):
    prod_min = summary["productive"] / 60
    dist_min = summary["distracting"] / 60

    if prod_min < target["productive_min_minutes"]:
        return "Target produktif gagal. Kamu aktif, tapi gak efektif."
    if dist_min > target["max_distracting_minutes"]:
        return "Distraksi kebanyakan. Fokus kamu bocor di mana-mana."
    return "Target aman. Disiplin hari ini masih hidup."


logs = load_logs()
summary = daily_summary(logs)
print_summary(summary)

target = load_target()
result = evaluate_target(summary, target)
print(result)
