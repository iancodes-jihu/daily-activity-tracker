import time
import json
from datetime import datetime
from src.core.sensor import get_active_window, is_afk
from src.persistence.storage import load_activity_logs, save_activity_logs, append_activity_log


def load_offline_schedule():
    """Load offline schedule from file."""
    try:
        with open("offline_schedule.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


# No app categorization: raw logs store app identifiers only (no moral labels)


def main():
    """Main tracker loop."""
    logs = load_activity_logs()

    current_app = get_active_window()
    start_time = datetime.now()
    last_check = start_time

    active_sec = 0
    afk_sec = 0

    last_afk = False

    offline_alert_sent = set()

    print("🟢 Tracker running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(5)
            now = datetime.now()
            offline_schedule = load_offline_schedule()

            elapsed = int((now - last_check).total_seconds())
            last_check = now

            afk = is_afk(60)

            # ===== OFFLINE ALERT =====
            for event in offline_schedule:
                try:
                    event_time = datetime.strptime(event["start"], "%H:%M").replace(
                        year=now.year, month=now.month, day=now.day
                    )
                    prep_time = event_time.timestamp() - event["prep_minutes"] * 60

                    if prep_time <= now.timestamp() < event_time.timestamp():
                        key = f"{event['title']}_{event['start']}"
                        if key not in offline_alert_sent:
                            print(f"⏰ ALERT: {event['title']} coming up. Stop screen time.")
                            offline_alert_sent.add(key)
                except Exception:
                    pass

            # ===== AFK HANDLING =====
            if afk:
                afk_sec += elapsed
                last_afk = True
                print(f"⏸ AFK detected ({afk_sec}s total)")
                continue

            if last_afk:
                # Just returned from AFK, don't count false time
                last_afk = False
                print("▶ Back to active")
                continue

            # ===== ACTIVE TIME =====
            active_sec += elapsed

            # ===== APP CHECK =====
            new_app = get_active_window()

            # ===== APP CHANGE =====
            if new_app != current_app:
                print(f"📲 App: {current_app} → {new_app}")
                
                logs.append({
                    "app": current_app,
                    "start": start_time.isoformat(),
                    "end": now.isoformat(),
                    "active_sec": active_sec,
                    "afk_sec": afk_sec
                })
                save_activity_logs(logs)

                # Reset session
                current_app = new_app
                start_time = now
                active_sec = 0
                afk_sec = 0

    except KeyboardInterrupt:
        now = datetime.now()

        if active_sec > 0 or afk_sec > 0:
            logs.append({
                "app": current_app,
                "start": start_time.isoformat(),
                "end": now.isoformat(),
                "active_sec": active_sec,
                "afk_sec": afk_sec
            })
            save_activity_logs(logs)

        print("\n⛔ Tracker stopped. Data saved.")


if __name__ == "__main__":
    main()