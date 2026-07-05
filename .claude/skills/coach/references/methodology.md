# Training Methodology

Plan-generation rules. These encode established coaching methodology (periodization,
80/20 intensity distribution, progressive overload) — follow them rather than
improvising, and keep plans conservative by default: the adaptation engine will
progress a user who overperforms, but an injury from an overcooked plan loses them.

## Plan architecture

The **primary goal** picks the architecture; secondary/tertiary goals shape volume,
session selection, and nutrition.

| Primary goal | Architecture |
|---|---|
| Endurance event (5K → marathon) | Base → Build → Peak → Taper, anchored to event date |
| Strength milestone | Linear or 3-week-wave progression on the main lifts, 8–12 wk blocks |
| Weight/body-comp target | Consistent weekly training rhythm + caloric deficit; progression = consistency and volume, not intensity |
| General fitness / "stay active" | 8-week repeating block, undulating intensity, variety-forward |

### Endurance phases (event-anchored)

Work backward from event date. Minimum viable: 8 weeks; ideal 12–16.

- **Base** (~40% of weeks): easy volume, one light quality session/wk, weekly long
  run grows ~10%/wk. Strength 1–2×/wk.
- **Build** (~35%): add race-specific quality (tempo, intervals at goal pace), long
  run continues growing, every 4th week is a down week (-30% volume).
- **Peak** (~15%): highest volume + race-pace work, long run peaks (half marathon:
  10–12 mi; marathon: 18–20 mi).
- **Taper** (final 1.5–2 wk): volume drops 40–60%, intensity stays, freshness up.

**Intensity distribution:** ~80% of running time easy (conversational, RPE 3–4),
~20% quality (RPE 6–8). Beginners who run every run "medium" get injured — enforce
easy days.

### Strength progression

- Novice: linear — add 2.5–5 lb per session on main lifts while form holds.
- Intermediate: weekly wave (e.g. 3×8 → 3×5 → 5×3 across a 3-week wave, then deload).
- Every 4th–6th week: deload (-40% volume, same movements).
- Structure: 2–4 sessions/wk, main lift + 2–4 accessories, accessories chosen to
  support the goal lift and address injury history.

## Volume rules

- Start at or slightly below the user's current training history — never more days
  per week than they reported, week one.
- Progress total weekly volume ≤10%/week. Down week every 4th week.
- Respect the schedule from the profile: sessions land on their chosen days, hardest
  session on their chosen long-session day, no back-to-back high-intensity days.
- If benchmark was skipped at onboarding: set week 1 deliberately easy and calibrate
  pace/load targets from the first week's logged RPE and actuals.

## Pacing & load targets from benchmarks

- From a 5K time: easy pace ≈ 5K pace + 90–120 s/mi; tempo ≈ 5K pace + 25–35 s/mi;
  interval pace ≈ 5K pace. Long-run pace = easy pace or slower.
- From a rep max: work sets at 65–80% of estimated 1RM (Epley: 1RM ≈ weight × (1 + reps/30)).
- State targets as ranges plus RPE so users self-regulate on bad days.

## Hybrid goals & conflict resolution

Resolve in the user's stated priority order, and say the trade-off out loud.

- **Endurance + weight loss:** modest deficit (300–500 kcal) on rest/easy days;
  maintenance on long-run and quality days. Never deficit the day before or of the
  long run. Protein high (see `nutrition.md`) to protect muscle.
- **Strength + endurance:** separate hard days; lift after runs or on separate days;
  expect slower progress on both and set that expectation early.
- **Weight loss primary + training secondary:** deficit is protected; training volume
  moderate and consistent rather than progressive; strength work 2×/wk minimum to
  protect lean mass.

## Injury accommodations

- Never program a movement that loads a reported injury through pain. Substitute
  (e.g. knee issues: step-downs and split squats before deep bilateral squats; hill
  repeats before downhill running).
- Every plan for a user with logged injuries includes 2–3 prehab exercises in
  movement prep (see `movement-prep.md`), tied to the specific issue.
- Pain (sharp, joint, worsening) ≠ soreness (dull, muscular, improving). Pain stops
  the session and triggers a plan adjustment; recommend professional evaluation for
  anything persistent.
