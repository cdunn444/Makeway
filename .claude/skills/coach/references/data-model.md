# Data Model

All state lives in `coach-data/`. Keep files small and human-readable — the user may
open and edit them by hand. Dates are ISO `YYYY-MM-DD`. Always determine "today" from
the environment (e.g. `date` command or the conversation context), never guess.

## profile.json

```json
{
  "created": "2026-07-05",
  "goals": {
    "primary":   { "text": "train for a half marathon", "event_date": "2026-10-04", "metric": "finish, target 1:55" },
    "secondary": { "text": "lose weight", "metric": "-10 lb" },
    "tertiary":  null
  },
  "stats": { "age": 38, "sex": "male", "height_cm": 178, "weight_kg": 84, "weigh_ins": [ { "date": "2026-07-05", "kg": 84 } ] },
  "training_history": {
    "days_per_week": 3,
    "activities": ["running", "occasional lifting"],
    "benchmark": { "type": "5k_time", "value": "26:30", "date": "2026-06-20" }
  },
  "injuries": [
    { "area": "left knee", "detail": "mild patellar tendinopathy, flares on downhills", "status": "managing" }
  ],
  "diet": {
    "restrictions": ["dairy-free"],
    "preferences": { "likes": ["oats", "rice", "chicken"], "dislikes": ["fish"] },
    "supplements": ["whey isolate (lactose-free)", "creatine 5g/day"]
  },
  "schedule": {
    "training_days": ["Mon", "Wed", "Fri", "Sat"],
    "preferred_time": "06:30",
    "long_session_day": "Sat"
  },
  "targets": {
    "tdee_baseline": 2750,
    "macros_training_day": { "kcal": 2600, "protein_g": 168, "carbs_g": 300, "fat_g": 72 },
    "macros_rest_day":     { "kcal": 2300, "protein_g": 168, "carbs_g": 220, "fat_g": 75 },
    "fuel": {
      "pre":  { "quality": "…", "long": "…", "easy": "…", "strength": "…" },
      "post": { "quality": "…", "long": "…", "easy": "…", "strength": "…" }
    }
  }
}
```

## plan.json

```json
{
  "generated": "2026-07-05",
  "goal_summary": "Half marathon 2026-10-04 (~1:55) while losing ~10 lb",
  "phase_map": [
    { "phase": "base",  "weeks": [1, 4] },
    { "phase": "build", "weeks": [5, 9] },
    { "phase": "peak",  "weeks": [10, 11] },
    { "phase": "taper", "weeks": [12, 13] }
  ],
  "current_week": 1,
  "weeks": [
    {
      "week": 1,
      "phase": "base",
      "focus": "aerobic base, tendon loading",
      "sessions": [
        { "date": "2026-07-06", "day": "Mon", "type": "easy_run",  "detail": "3 mi easy, conversational (RPE 3-4)", "duration_min": 35, "status": "upcoming" },
        { "date": "2026-07-08", "day": "Wed", "type": "strength",  "detail": "Lower A: goblet squat 3x8, RDL 3x8, step-down 3x10/leg, calf raise 3x15", "duration_min": 40, "status": "upcoming" },
        { "date": "2026-07-10", "day": "Fri", "type": "tempo_run", "detail": "4 mi: 1 easy + 2 @ tempo (RPE 6-7) + 1 easy", "duration_min": 42, "status": "upcoming" },
        { "date": "2026-07-11", "day": "Sat", "type": "long_run",  "detail": "5 mi easy, fuel practice", "duration_min": 60, "status": "upcoming" },
        { "date": "2026-07-07", "day": "Tue", "type": "rest", "detail": "Rest — mobility optional", "status": "upcoming" },
        { "date": "2026-07-09", "day": "Thu", "type": "rest", "detail": "Rest", "status": "upcoming" },
        { "date": "2026-07-12", "day": "Sun", "type": "rest", "detail": "Rest — easy walk encouraged", "status": "upcoming" }
      ]
    }
  ]
}
```

Run sessions carry a numeric `miles` field and each week carries a 1–2 sentence
`summary` — the dashboard's Schedule header totals the miles and shows the summary,
so keep both current when adapting the plan.

Session `status`: `upcoming | completed | partial | skipped`. Session `type` values:
`easy_run, tempo_run, interval_run, long_run, strength, cross_train, active_recovery,
rest` (extend as needed for the user's activities). Only generate detailed sessions
2–3 weeks ahead; keep later weeks as phase-level sketches and fill them in as they
approach — adaptation makes far-future detail stale anyway.

## log.jsonl — one JSON object per line, append-only

```jsonl
{"date": "2026-07-06", "kind": "workout", "session_date": "2026-07-06", "type": "easy_run", "result": "completed", "actual": "3 mi @ 10:45/mi", "rpe": 4, "note": "felt good"}
{"date": "2026-07-08", "kind": "workout", "session_date": "2026-07-08", "type": "strength", "result": "partial", "actual": "squats + RDL only, ran out of time", "note": ""}
{"date": "2026-07-10", "kind": "workout", "session_date": "2026-07-10", "type": "tempo_run", "result": "skipped", "reason": "sick kid, no sleep"}
{"date": "2026-07-10", "kind": "nutrition", "kcal": 610, "protein_g": 42, "carbs_g": 55, "fat_g": 22, "desc": "eggs + rice + avocado"}
{"date": "2026-07-12", "kind": "weigh_in", "kg": 83.4}
{"date": "2026-07-12", "kind": "adaptation", "action": "moved tempo to Sun, reduced to 3 mi", "trigger": "skipped 2026-07-10"}
```

Log adaptations you make as `kind: "adaptation"` lines so there's an audit trail of
what the engine changed and why.

`kind: "week_history"` lines (`week` = Monday date, `miles`, `source`) backfill
weekly mileage totals from before Coach existed — the dashboard chart uses them
only for weeks with no logged runs, so they never double-count synced data.

## notes.md

Free-form coach memory in short bullets: things the user mentioned (travel next week,
new shoes, race registered), flags to watch (knee felt off twice this month), and
anything that should influence future briefs. Prune stale items when you touch it.
