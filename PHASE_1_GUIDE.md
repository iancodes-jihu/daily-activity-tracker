"""
Daily Behavior Deviation Detection System

Phase 1 - Architecture implemented:
✓ Sensor layer (raw app tracking with AFK detection)
✓ Feature extraction (14+ daily behavioral metrics)
✓ Baseline computation (rolling 14-day statistical window)
✓ Deviation detection (z-score based anomaly detection)
✓ Human-readable explanations (English interpretation of deviations)
✓ Unit tests (17/17 passing)
✓ Data persistence (JSON-based storage)
✓ Backfill script (historical feature extraction)
✓ Daily analysis pipeline (end-to-end)

"""

### Quick Start

1. **Extract historical features** (run once):
   ```bash
   python scripts/init_baseline.py
   ```
   This scans your raw activity_log.json and computes daily features for 
   the last 30 days, storing them in data/daily_features.json.

2. **Run daily analysis** (run daily):
   ```bash
   python scripts/analyze_today.py
   ```
   This:
   - Extracts today's features from raw logs
   - Rebuilds rolling baseline (last 14 days)
   - Detects deviations vs baseline
   - Saves deviation report with explanations

3. **Run unit tests**:
   ```bash
   pytest tests/ -v
   ```
   All 17 tests pass ✓

### Data Flow

```
Raw activity logs (activity_log.json)
  ↓
Feature extraction (daily_features.json)
  1 row per day
  14+ behavioral metrics
  ↓
Rolling baseline (baseline_window.json)
  Mean, std, IQR, percentiles per metric
  Updated daily
  ↓
Deviation detection
  Z-score comparison vs baseline
  Explainable thresholding
  ↓
Deviation report (deviation_log.json)
  Status (on_track / warning / critical)
  English explanations
  ↓
Human (you read it and understand your behavior)
```

### Project Structure

```
src/
├── core/              → Low-level sensor (app tracking, AFK)
├── features/          → Daily metric extraction (14+ features)
├── baseline/          → Rolling window statistics
├── deviation/         → Anomaly detection + explanations
└── persistence/       → Data models & I/O

tests/                 → 17 unit tests (100% passing)

scripts/
├── init_baseline.py   → One-time historical extraction
└── analyze_today.py   → Daily analysis pipeline

data/
├── activity_log.json  → Raw sensor events (IMMUTABLE)
├── daily_features.json → Daily aggregates (GENERATED)
├── baseline_window.json → Current baseline (GENERATED)
└── deviation_log.json → Deviation reports (GENERATED)
```

### Daily Features Explained

**Time & Activity:**
- `total_active_sec` - Seconds in front of screen
- `total_afk_sec` - Seconds idle
- `session_count` - Number of app switches

**Focus:**
- `avg_session_length_sec` - Average app duration (longer = better focus)
- `session_length_cv` - Consistency (lower = more predictable)
- `activity_concentration` - Top 3 apps domination (lower = more balance)

**Fragmentation:**
- `session_switch_rate` - App switches per hour (higher = more distracted)
- `inter_session_gap_mean_sec` - Average break between apps

**Off-screen:**
- `afk_ratio` - Percentage idle
- `break_count` - Number of 5+ minute breaks

**Categories:**
- `productive_sec`, `distracting_sec`, `neutral_sec`, `unknown_sec`

### Deviation Alerts

The system monitors these features for significant deviations:

| Feature | Alert Direction | Means |
|---------|-----------------|-------|
| avg_session_length | Below baseline | Loss of deep work |
| session_switch_rate | Above baseline | Increased distraction |
| afk_ratio | Above baseline | Fatigue or system idle |
| session_length_cv | Above baseline | Erratic work rhythm |
| inter_session_gap | Above baseline | Fragmented workflow |

Example output:
```
⚠️ WARNING: Some deviations from your baseline.

⚠️ Sessions shortened: 8m avg vs 16m baseline (-48%)
   → Possible loss of focus or more fragmentation

⚠️ App switches increased: 12.4 per hour vs 7.2 baseline (+72%)
   → More context-switching, possible distraction
```

### Configuration

**Baseline window**: 14 days (adjustable in code)
**Z-score threshold**: 2.0 (95% confidence, adjustable)
**Minimum data quality**: "partial" (5+ minutes activity)

### Limitations & Future Work

**Phase 1 (Current - Statistical Only):**
- ✓ Z-score based detection
- ✓ No ML models
- ✓ Explainable results
- ✓ Fast & deterministic

**Phase 2 (Roadmap - Visualization):**
- Dashboard with charts
- Weekly/monthly summaries
- Feature correlations
- Trend analysis

**Phase 3 (Roadmap - ML Detection):**
- Isolation Forest for multivariate anomalies
- SHAP values for explanations
- Requires: 2+ months historical data

### Development

Run tests after any change:
```bash
pytest tests/ -v
```

Add new features to `DailyFeatures` model:
1. Add field to `src/persistence/models.py`
2. Compute it in `src/features/daily_extractor.py`
3. Add baseline monitoring in `src/baseline/rolling_window.py`
4. Add detection logic in `src/deviation/detector.py`
5. Write tests in `tests/test_*.py`

### Important Notes

- **Not a prediction system**: This detects *your* deviation from *yourself*, not predicting future behavior
- **No moral judgments**: "Productive" and "distraction" are YOUR categories, the system is neutral
- **Privacy first**: All analysis is local, no data sent anywhere
- **Statistical foundation**: Z-scores are scientifically sound; no magic

---

For questions, check ARCHITECTURE.md for detailed design rationale.
