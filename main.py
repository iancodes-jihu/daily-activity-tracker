import time
from datetime import datetime
from tracker import get_active_window, is_afk, load_logs, save_logs, load_rules, classify_app, load_target, load_offline_schedule

def main():
    rules = load_rules()
    logs = load_logs()
    target = load_target()

    current_app = get_active_window()
    start_time = datetime.now()
    last_check = start_time

    active_sec = 0
    afk_sec = 0

    last_afk = False
    focus_recovery_sec = 0

    distract_limit = target["max_distracting_minutes"] * 60
    total_distract_today = 0
    alert_sent = False
    offline_alert_sent = set()

    print("Tracker jalan. Ctrl+C untuk berhenti.")

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
                event_time = datetime.strptime(event["start"], "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day
                )
                prep_time = event_time.timestamp() - event["prep_minutes"] * 60

                if prep_time <= now.timestamp() < event_time.timestamp():
                    key = f"{event['title']}_{event['start']}"
                    if key not in offline_alert_sent:
                        print(f"ALERT: {event['title']} sebentar lagi. Stop gadget.")
                        offline_alert_sent.add(key)

            # ===== AFK HANDLING =====
            if afk:
                afk_sec += elapsed
                last_afk = True
                focus_recovery_sec = 0
                print("Status: AFK")
                continue

            if last_afk:
                # baru balik dari AFK, jangan hitung waktu palsu
                last_afk = False
                print("Status: Kembali dari AFK")
                continue

            # ===== ACTIVE TIME =====
            active_sec += elapsed

            # ===== APP CHECK =====
            new_app = get_active_window()
            category = classify_app(current_app, rules)

            # ===== DISTRACTION ALERT RESET =====
            if category == "productive":
                focus_recovery_sec += elapsed
                if focus_recovery_sec >= 900:  # 15 menit fokus
                    alert_sent = False
            else:
                focus_recovery_sec = 0

            # ===== APP CHANGE =====
            if new_app != current_app:
                print(f"App berubah: {current_app} -> {new_app}")
                logs.append({
                    "app": current_app,
                    "category": category,
                    "start": start_time.isoformat(),
                    "end": now.isoformat(),
                    "active_sec": active_sec,
                    "afk_sec": afk_sec
                })
                save_logs(logs)

                if category == "distracting":
                    total_distract_today += active_sec
                    if total_distract_today >= distract_limit and not alert_sent:
                        print("ALERT: Distraksi harian melewati batas.")
                        alert_sent = True

                # reset session
                current_app = new_app
                start_time = now
                active_sec = 0
                afk_sec = 0
                focus_recovery_sec = 0

    except KeyboardInterrupt:
        now = datetime.now()
        category = classify_app(current_app, rules)

        logs.append({
            "app": current_app,
            "category": category,
            "start": start_time.isoformat(),
            "end": now.isoformat(),
            "active_sec": active_sec,
            "afk_sec": afk_sec
        })
        save_logs(logs)

        print("Tracker berhenti. Data terakhir aman.")


if __name__ == "__main__":
    main()