# Nutrition

The differentiator: **workout-specific nutrient timing**, not generic daily macro
math. A rest day and a long-run day are different nutrition days. Every suggestion
must respect the profile's dietary restrictions — check before naming any food.

## TDEE

1. **BMR (Mifflin-St Jeor):**
   - Male: `10×kg + 6.25×cm − 5×age + 5`
   - Female: `10×kg + 6.25×cm − 5×age − 161`
   - Sex not shared: use the midpoint, note the estimate is rougher.
2. **TDEE = BMR × activity factor** from *baseline daily life* (1.3–1.4 for desk
   job, 1.5 for active job) — then add training on top per session (below), rather
   than baking a generic 1.55 "moderately active" into every day.
3. **Session energy cost** added to that day's target: easy run ≈ 100 kcal/mi;
   quality run ≈ 110–120 kcal/mi; strength session ≈ 250–350 kcal; scale by body
   weight (±10% per 15 lb from 155 lb).

## Daily macro targets

- **Protein:** 1.8–2.2 g/kg (top of range in a deficit) — constant every day.
- **Fat:** 0.7–0.9 g/kg floor.
- **Carbs:** the remainder — this is the lever that moves with training load.
- **Deficit** (when weight loss is a goal): 300–500 kcal below that day's TDEE,
  placed on rest/easy days per the conflict rules in `methodology.md`. Target rate
  ≤0.5–1% body weight/week.

Compute a training-day and a rest-day macro set and store both in `profile.json`;
the Daily Brief picks per today's session and states which one applies.

## Timing by session type

### Endurance — quality (tempo, intervals) or long run
- **Pre (2–3 h before, or ~60 min for something light):** carb-forward, moderate
  protein, low fat/fiber. E.g. "60 min before: rolled oats + banana + black coffee."
  Long runs >90 min: practice in-run fueling, 30–60 g carbs/hr.
- **Post (within ~30–60 min):** 20–40 g protein + fast carbs (~0.5–1 g/kg). E.g.
  "protein shake + a bagel" — adjust for restrictions.
- Context line for the brief: carbs are the story today.

### Endurance — easy run
- No special pre-fuel needed under 60 min (a small carb snack if training fasted
  feels bad). Normal post-meal timing; protein at the next meal.

### Strength
- **Pre (1–2 h):** balanced meal, protein + carbs (e.g. eggs + toast, or rice +
  chicken). Caffeine 30–45 min before if the user uses it.
- **Post (within ~2 h):** 30–40 g protein; carbs normal. The recovery window is
  more forgiving than endurance glycogen replenishment — total daily protein
  matters more than the clock.

### Rest / active recovery
- Rest-day macros: carbs drop (the lever), protein constant, fat can rise slightly.
- This is where the deficit lives for weight-loss goals.
- Frame it positively: "recovery day — protein keeps rebuilding, carbs come down
  because we're not fueling a session."

## Adherence logging & adaptation

When the user reports being significantly over/under target (±300 kcal or more),
log it (`kind: "nutrition"`) and shift the *next day's* targets to partially
compensate — spread half the surplus/shortfall over the next 1–2 days, never crash
tomorrow's carbs below what tomorrow's session needs. One over day is noise; a
week-long pattern means recompute the targets, not scold the user.

## Supplements

Only reference what the user already takes (from profile) plus the boring, evidenced
basics if asked: creatine 3–5 g/day, caffeine pre-workout, whey/plant protein for
convenience, vitamin D if low sun. No exotic recommendations; flag anything
prescription-adjacent to a professional.
