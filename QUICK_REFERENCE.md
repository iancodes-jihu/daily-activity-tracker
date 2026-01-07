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

**Category Breakdown**
- `productive_sec` — Work/code time
- `distracting_sec` — Social media/games
- `neutral_sec` — System/admin
- `unknown_sec` — Uncategorized

**Plus 6 more**: spans, totals, metadata...

## Deviation Signals

The system alerts you when:
- Sessions got **shorter** (loss of focus)
- **More app switching** (distracted)
- **More AFK** (fatigue or break)
- **Inconsistent rhythm** (erratic day)
- **Fragmented work** (interrupted)

## Example Output

**Normal Day:**
```
✅ On track: All metrics within normal range.
Status: ON_TRACK
```

**Bad Day:**
```
⚠️ WARNING: Some deviations from your baseline.

⚠️ Sessions shortened: 8m avg vs 16m baseline (-48%)
   → Possible loss of focus or more fragmentation

⚠️ App switches increased: 12.4 per hour vs 7.2 baseline (+72%)
   → More context-switching, possible distraction
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

**In `main.py`:**
```python
productive_apps = ["Code.exe", "ChatGPT.exe", ...]
distracting_apps = ["Instagram", "Twitter", ...]
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
