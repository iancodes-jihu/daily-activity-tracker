from behavior_deviation import analyze_today
from tracker import load_logs

def main():
    logs = load_logs()
    result = analyze_today(logs, baseline_days=6)

    print("=== DEVIATION RESULT ===")
    for k, v in result.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
