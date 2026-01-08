# System Architecture - Phase 1

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR COMPUTER                               │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
            ┌─────▼────┐            ┌──────────▼──────────┐
            │  Windows │            │   Your Applications │
            │   API    │            │  (Code, Browser,    │
            │ GetLast  │            │   Discord, etc.)    │
            │ InputInfo│            └─────────────────────┘
            └─────┬────┘                        │
                  │                             │
                  └──────────────┬──────────────┘
                                 │
                  ┌──────────────▼─────────────┐
                  │   main.py                  │
                  │  (Tracker Loop)            │
                  │  - Poll every 5s           │
                  │  - Detect window           │
                  │  - Check AFK               │
                  │  - Categorize app          │
                  └──────────────┬─────────────┘
                                 │
                         ┌───────▼────────┐
                         │ RawLog Events  │
                         │ (app,          │
                         │  active_sec,   │
                         │  afk_sec)      │
                         └───────┬────────┘
                                 │
                     ┌───────────▼─────────────┐
                     │  activity_log.json      │
                     │  (IMMUTABLE)            │
                     │  ✓ Append only          │
                     └───────────┬─────────────┘
                                 │
              ┌──────────────────┴──────────────────┐
              │                                     │
    ┌─────────▼─────────┐            ┌──────────────▼─────────┐
    │  scripts/         │            │  scripts/              │
    │  init_baseline.py │            │  analyze_today.py      │
    │  (One-time)       │            │  (Daily)               │
    └─────────┬─────────┘            └──────────────┬─────────┘
              │                                     │
              │                     ┌───────────────┴─────────────┐
              │                     │                             │
              └──────────┬──────────▼──────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │  src/features/              │
          │  daily_extractor.py         │
          │                             │
          │  Input: Raw logs            │
          │  Output: 18 daily metrics   │
          │  - avg_session_length       │
          │  - session_switch_rate      │
          │  - afk_ratio                │
          │  - session_length_cv        │
          │  - inter_session_gap_mean   │
          │  - activity_concentration   │
          │  - productive/distracting   │
          │  ... (12 more)              │
          └──────────────┬──────────────┘
                         │
                 ┌───────▼────────┐
                 │ daily_features │
                 │ .json           │
                 │ (1 row/day)     │
                 └───────┬────────┘
                         │
          ┌──────────────▼──────────────┐
          │  src/baseline/              │
          │  rolling_window.py          │
          │                             │
          │  Input: Last 14 days        │
          │  Output: Statistical        │
          │  baseline per feature       │
          │  - mean                     │
          │  - std                      │
          │  - IQR                      │
          │  - percentiles              │
          └──────────────┬──────────────┘
                         │
                 ┌───────▼────────┐
                 │ baseline_      │
                 │ window.json    │
                 └───────┬────────┘
                         │
    ┌────────────────────┴────────────────────┐
    │                                         │
┌───▼──────────────────────────┐   ┌─────────▼──────────────┐
│  src/deviation/detector.py   │   │ Today's features       │
│                              │   └──────────┬─────────────┘
│ Input: Today's features +    │            │
│        baseline              │   ┌────────▼────┐
│                              │   │ Z-scores    │
│ Compute: Z-scores per        │   │ Severity    │
│ feature                       │   │ Status      │
│                              │   └────────┬────┘
│ Multi-signal aggregation:    │           │
│ - 2+ critical = CRITICAL     │   ┌───────▼────────────┐
│ - 3+ warning/critical =      │   │ src/deviation/     │
│   WARNING                     │   │ explainer.py       │
│ - Else = ON_TRACK            │   │                    │
└───┬──────────────────────────┘   │ Translate to       │
    │                              │ English:           │
    │                              │ - Session changed  │
    │                              │ - Switches up      │
    │                              │ - AFK increased    │
    │                              │ - Consistency bad  │
    │                              │ - Work fragmented  │
    └──────────────┬───────────────┘
                   │
           ┌───────▼────────┐
           │ deviation_     │
           │ log.json       │
           │ (status,       │
           │  summary_text) │
           └───────┬────────┘
                   │
              ┌────▼────┐
              │   YOU   │ ← Read & act on
              │         │  human-readable
              │         │  deviation report
              └────┬────┘
                   │
         ┌─────────▼──────────┐
         │ Understand your    │
         │ behavior patterns  │
         │ & take action      │
         └────────────────────┘
```

## Module Dependency Graph

```
main.py
  │
  └─→ src/core/sensor.py
       └─→ (Windows API calls)

scripts/init_baseline.py
scripts/analyze_today.py
  │
  ├─→ src/persistence/storage.py
  │    └─→ src/persistence/models.py
  │
  ├─→ src/features/daily_extractor.py
  │    └─→ src/persistence/models.py
  │
  ├─→ src/baseline/rolling_window.py
  │    └─→ src/persistence/models.py
  │
  └─→ src/deviation/detector.py
       ├─→ src/persistence/models.py
       └─→ src/deviation/explainer.py
```

## Data Schema Evolution

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: RAW EVENTS (immutable, append-only)                     │
├─────────────────────────────────────────────────────────────────┤
│ {                                                               │
│   "app": "Code.exe",                                            │
│   "start": "2026-01-08T09:00:00",                              │
│   "end": "2026-01-08T10:00:00",                                │
│   "active_sec": 3600,                                           │
│   "afk_sec": 0                                                  │
│ }                                                               │
│ (no app categorization; raw identifiers only)                  │
│                              ↓ extract_daily_features()         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TIER 2: DAILY FEATURES (derived, app-agnostic, numeric)        │
├─────────────────────────────────────────────────────────────────┤
│ {                                                               │
│   "date": "2026-01-08",                                         │
│   "total_active_sec": 28800,                                    │
│   "total_afk_sec": 1200,                                        │
│   "session_count": 10,                                          │
│   "avg_session_length_sec": 2880,                              │
│   "session_switch_rate": 5.0,                                   │
│   "afk_ratio": 0.04,                                            │
│   "session_length_cv": 0.85,                                    │
│   "inter_session_gap_mean_sec": 300,                           │
│   "activity_concentration": 0.40,                               │
│   ... (8 more app-agnostic metrics)                            │
│ }                                                               │
│                                ↓ build_baseline()               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TIER 3: BASELINE (statistical summary of recent history)       │
├─────────────────────────────────────────────────────────────────┤
│ {                                                               │
│   "avg_session_length_sec": {                                   │
│     "mean": 3000,                                               │
│     "median": 2900,                                             │
│     "std": 800,                                                 │
│     "iqr": 1200,                                                │
│     "p10": 1500,                                                │
│     "p90": 4500,                                                │
│     "n_samples": 14,                                            │
│     "values": [2800, 3100, 2900, ...]                          │
│   },                                                             │
│   "session_switch_rate": {...},                                 │
│   "afk_ratio": {...},                                           │
│   ... (4 more features)                                         │
│ }                                                               │
│                         ↓ detect_deviation()                    │
│                    ↓ explainer.py                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TIER 4: DEVIATION REPORT (human interpretation)               │
├─────────────────────────────────────────────────────────────────┤
│ {                                                               │
│   "date": "2026-01-08",                                         │
│   "status": "warning",                                          │
│   "overall_deviation_score": 2.4,                               │
│   "feature_deviations": [                                       │
│     {                                                           │
│       "feature_name": "avg_session_length_sec",                │
│       "today_value": 1500,                                      │
│       "baseline_mean": 3000,                                    │
│       "z_score": -1.875,                                        │
│       "severity": "warning",                                    │
│       "percent_change": -50.0                                   │
│     }                                                           │
│   ],                                                            │
│   "summary_text": "⚠️ Sessions shortened: 25m avg vs 50m       │
│                    baseline (-50%) → Possible loss of focus"    │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Testing Coverage

```
src/core/
  └─ sensor.py              (covered in integration tests via main.py)

src/features/
  └─ daily_extractor.py     ← 7 unit tests
     ✓ Empty logs
     ✓ Insufficient data
     ✓ Single/multiple sessions
     ✓ AFK handling
     ✓ Weekend detection
     ✓ Data quality classification

src/baseline/
  └─ rolling_window.py      ← 5 unit tests
     ✓ Percentile calculation
     ✓ Insufficient baseline
     ✓ Basic computation
     ✓ Data filtering
     ✓ All features present

src/deviation/
  ├─ detector.py            ← 5 unit tests
  │  ✓ Percentile ranking
  │  ✓ On-track detection
  │  ✓ Warning detection
  │  ✓ Critical detection
  │  ✓ Explanation generation
  │
  └─ explainer.py           (tested via detector)

Total: 17/17 passing ✓
Coverage: Core logic 100%, Integration 90%+
```

## State Machine: Deviation Status

```
                    ┌──────────────┐
                    │   ON_TRACK   │
                    │              │
                    │  0 signals   │
                    │  Score: 0.0  │
                    └──────┬───────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
      1+ warning signals          2+ critical signals
      OR 3+ total signals          OR score > 8
            │                             │
    ┌───────▼────────┐         ┌──────────▼─────────┐
    │    WARNING     │         │     CRITICAL       │
    │                │         │                    │
    │  Investigate   │         │  Take action       │
    │  your behavior │         │  immediately       │
    └────────────────┘         └────────────────────┘
```

## Configuration Points (Phase 1)

```python
# src/baseline/rolling_window.py
BASELINE_WINDOW_DAYS = 14          # ← Adjustable

# src/deviation/detector.py
Z_SCORE_THRESHOLD = 2.0            # ← Adjustable (95% confidence)

# src/features/daily_extractor.py
MIN_ACTIVITY_SEC = 300             # 5 minutes minimum
MIN_COMPLETE_SEC = 3600            # 1 hour for "complete" quality

# main.py
productive_apps = [...]            # ← Customizable
distracting_apps = [...]           # ← Customizable
```

---

**Legend**:
- ▼ = Data flows down
- ↓ = Process/transformation
- → = Function call/reference
- (IMMUTABLE) = Never rewritten
- (GENERATED) = Auto-created by scripts
