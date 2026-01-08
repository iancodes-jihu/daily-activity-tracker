# QUICK REFERENCE CARD - Phase 1

## What Was Delivered

✅ **Statistical Deviation Detection System**
   - Analyzes your daily behavior
   - Detects deviations from YOUR baseline
   - Generates human-readable explanations
   - 100% tested (17/17 passing)

## How to Use

### First Time Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Extract historical features (one-time)
python scripts/init_baseline.py
```

### Daily Usage
```bash
# Run daily analysis
python scripts/analyze_today.py
```
→ Produces human-readable deviation report

### Verify Everything Works
```bash
# Run tests
pytest tests/ -v
```

## Key Files

| File | Purpose |
|------|---------|
| `src/features/daily_extractor.py` | Extract 18 daily metrics |
| `src/baseline/rolling_window.py` | Compute rolling baseline |
| `src/deviation/detector.py` | Detect deviations |
| `src/deviation/explainer.py` | Generate explanations |
| `data/daily_features.json` | Daily metrics (output) |
| `data/baseline_window.json` | Statistics (output) |
| `data/deviation_log.json` | Reports (output) |

## 18 Daily Metrics

**Focus & Session Quality**
- `avg_session_length_sec` — Longer = better focus
- `session_length_cv` — Lower = more consistent
- `activity_concentration` — Lower = more balanced

**Distraction & Context-Switching**
- `session_switch_rate` — Lower = fewer switches
- `inter_session_gap_mean_sec` — Lower = continuous work

**Off-Screen Time**
- `afk_ratio` — Time idle
- `break_count` — Long AFK periods
- `avg_break_length_sec` — Break duration

**Plus 7 more**: spans, totals, metadata...

## Deviation Signals

The system reports numeric deviations when:
- Sessions got **shorter** than baseline (z-score or % change)
- **More app switching** (z-score or % change)
- **More AFK** (z-score or % change)
- **Inconsistent rhythm** (z-score or % change)
- **Fragmented work** (z-score or % change)

All outputs are numeric (z-scores, percent change, percentile rank) — **no moral judgments**.

## Example Output

**Normal Day:**
```
- avg_session_length_sec: today=1200, baseline_mean=1080, z=-0.18, pct_change=11.1%
- session_switch_rate: today=5.0, baseline_mean=5.0, z=0.0, pct_change=0.0%
- afk_ratio: today=0.1, baseline_mean=0.1, z=0.0, pct_change=0.0%

Overall numeric score (sum |z|): 0.18
```

**Deviation Day:**
```
- avg_session_length_sec: today=500, baseline_mean=1080, z=-2.9, pct_change=-53.7%
- session_switch_rate: today=12.0, baseline_mean=5.0, z=7.0, pct_change=140.0%
- afk_ratio: today=0.25, baseline_mean=0.1, z=7.5, pct_change=150.0%

Overall numeric score (sum |z|): 17.4
```

## Configuration

**In `src/baseline/rolling_window.py`:**
```python
BASELINE_WINDOW_DAYS = 14  # Look back 14 days
```

**In `src/deviation/detector.py`:**
```python
Z_SCORE_THRESHOLD = 2.0    # 95% statistical confidence
```

## Data Flow (Simplified)

```
Raw app logs (activity_log.json)
    ↓
Extract daily metrics (daily_features.json)
    ↓
Compute baseline stats (baseline_window.json)
    ↓
Detect deviations vs baseline
    ↓
Generate explanations (deviation_log.json)
    ↓
You read & act on report
```

## Troubleshooting

**No data generated?**
- Check `data/activity_log.json` exists
- Need at least 300 seconds (5 min) per day

**Baseline not building?**
- Need 3+ days of activity data
- Run: `python scripts/init_baseline.py`

**Tests failing?**
- Ensure dependencies installed: `pip install -r requirements.txt`
- Run: `pytest tests/ -v`

## What's NOT Included

❌ Prediction (not forecasting future behavior)
❌ Moral judgment (system is neutral)
❌ ML models (statistical only)
❌ Cloud sync (all local)
❌ Real-time alerts (daily batch analysis)

## Next Phase Ideas

- 📊 Web dashboard & visualizations
- 📈 Weekly/monthly summaries
- 🔗 Feature correlation analysis
- 🤖 Isolation Forest anomaly detection (Phase 3)

## Documentation

Read these in order:
1. `PHASE_1_GUIDE.md` ← Start here
2. `SYSTEM_ARCHITECTURE.md` ← Understand design
3. `IMPLEMENTATION_DETAILS.md` ← Deep dive
4. `PHASE_1_STATUS_REPORT.txt` ← Current status

---

**Status**: ✅ Production Ready (Phase 1)
**Tests**: 17/17 passing
**Code**: ~1,500 lines (core + tests)
**Last Updated**: January 8, 2026
