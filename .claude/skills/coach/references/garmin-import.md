# Garmin / Wearable Import

**Automatic path (preferred):** the Strava sync Action
(`.github/workflows/strava-sync.yml` + `scripts/strava_sync.py`) pulls activities
from the official Strava API every 4 hours (Garmin auto-syncs to Strava), logs them
with `"source": "strava"`, dedupes by `strava_id`, and updates plan statuses. The
manual flows below remain for wellness data, gaps, or when Strava sync is down.

Handles `/coach import <file>` (or the user pasting/uploading an export). Purpose:
turn a weekly Garmin Connect export into logged sessions with real actuals — pace,
heart rate, duration — instead of self-reported estimates. Works the same for exports
from Strava, Apple Health, or any CSV/TCX/GPX with per-activity rows.

## Supported formats

| Format | Source | How to read |
|---|---|---|
| CSV | Garmin Connect → Activities → Export CSV | Parse directly (best option — one file, many activities) |
| TCX / GPX | Per-activity export | XML — parse with python stdlib (`xml.etree`); one activity per file |
| FIT | Watch raw files | Binary — don't hand-parse. Ask the user to export CSV/TCX instead |
| Screenshot / pasted text | Garmin app | Read the values shown; confirm date and distance before logging |

Garmin CSV columns vary by language/settings but typically include: `Activity Type,
Date, Title, Distance, Time, Avg HR, Max HR, Avg Pace, Total Ascent, Calories`.
Parse defensively: check the header row, don't assume column order, and watch units
(km vs mi — infer from the profile or ask once and note it in `notes.md`).

## Import flow

1. **Parse** the file into activities: date, type, distance, duration, avg/max HR,
   avg pace, calories.
2. **Dedupe** against `log.jsonl`: skip any activity whose date + type + distance
   (±2%) already has a `kind: "workout"` entry. This makes overlapping weekly
   exports safe to re-upload. Report what was skipped: "3 new, 2 already logged."
3. **Match** each new activity to the planned session on that date in `plan.json`:
   - Same date + compatible type → log against that session. Compare actual vs.
     planned volume: ≥90% → `completed`; <90% → `partial` with actuals.
   - No planned session that day → log as unplanned (`"planned": false`) — it still
     counts toward volume and streaks. If unplanned sessions are frequent, ask
     whether the schedule needs to change.
   - Planned session with no matching activity, and the date has passed → ask
     before marking skipped (they may have done it without the watch).
4. **Write** one `kind: "workout"` line per activity with the device actuals:

```jsonl
{"date": "2026-07-11", "kind": "workout", "session_date": "2026-07-11", "type": "long_run", "result": "completed", "source": "garmin", "actual": "5.02 mi in 54:12", "avg_pace": "10:48/mi", "avg_hr": 152, "max_hr": 168, "calories": 610}
```

5. **Adapt**: run the adaptation rules (`adaptation.md`) over the imported results,
   oldest first — a partial from Tuesday should influence the plan before Saturday's
   result is considered.
6. **Summarize**: one compact table of what was imported and logged, then any
   adaptation made, then one insight (see below). Don't dump raw rows.

## What device data unlocks (use it in `/coach progress`)

- **Aerobic trend — the headline metric:** pace at a given heart rate on easy runs.
  Same effort getting faster = fitness improving, even when workouts feel the same.
  Compare easy-run `avg_pace`/`avg_hr` pairs across weeks: "Easy pace at ~150 bpm
  was 11:10/mi four weeks ago, 10:45 this week."
- **Intensity discipline:** easy runs with high avg HR (roughly >75% of observed
  max) mean the user is running easy days too hard — flag it and restate the 80/20
  rule from `methodology.md`.
- **Honest volume:** weekly mileage from device data, not plan assumptions.
- **PR detection:** fastest 5K-distance run, longest run, biggest week — announce
  them when they happen.

Store durable observations (e.g. "easy HR ceiling ~155", "units: miles") in
`notes.md` so future briefs use them.

## Habits

- Never overwrite a manual log with an import silently — if they conflict (user said
  completed, watch says 60%), keep the device actuals but ask about the gap.
- If the user mentions they upload weekly, remind them at the weekly review only if
  the week has passed with no import and no manual logs — once, not naggingly.
