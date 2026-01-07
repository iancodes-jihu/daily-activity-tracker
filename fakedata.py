from deviation_tracker import DeviationTracker

daily_target = {
    "productive_min_minutes": 180,
    "max_distracting_minutes": 90
}

tracker = DeviationTracker(daily_target)

history = [
    {"date": "2026-01-01", "productive": 190, "distracting": 60, "afk": 20},
    {"date": "2026-01-02", "productive": 185, "distracting": 55, "afk": 25},
    {"date": "2026-01-03", "productive": 200, "distracting": 50, "afk": 15},
    {"date": "2026-01-04", "productive": 195, "distracting": 65, "afk": 18},
    {"date": "2026-01-05", "productive": 180, "distracting": 70, "afk": 22},
]

today = {
    "date": "2026-01-06",
    "productive": 130,
    "distracting": 110,
    "afk": 40
}

result = tracker.analyze_day(today, history)
print(result)
