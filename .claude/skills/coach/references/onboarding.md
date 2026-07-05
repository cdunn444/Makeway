# Onboarding Flow

Collect the minimum needed to generate a personalized Day 1. Conversational, one step
at a time — never dump all six steps as one questionnaire. After each answer, reflect
back one concrete implication so it feels like building something, not filling a form.

Do NOT ask for location. Do not ask anything not listed here.

## Step 1 — Goal (ad-lib)

Present the ad-lib and ask them to fill it in:

> **"I want to _[primary goal]_ while _[secondary goal]_ and _[tertiary — optional]_."**

Examples to offer if they hesitate:
- "I want to train for a half marathon while losing weight"
- "I want to build strength while improving my 5K time"
- "I want to lose 20 pounds while staying active"

Primary goal is required and drives plan architecture. If the primary goal is an event
(race, competition), get the date — it anchors periodization. If it's a quantity
(lose 20 lb, bench 225), get the number and, if offered, a rough timeframe.

## Step 2 — About you

Age, height, weight, and sex if they're comfortable sharing it (needed for TDEE; if
declined, use the midpoint of the male/female BMR formulas and say estimates will be
slightly rougher). Used for TDEE calculation and plan intensity only.

## Step 3 — Training history

- How many days per week do you currently train?
- What activities?
- One recent benchmark (5K time, max bench, longest recent run, etc.). Benchmark is
  optional — if skipped, start conservative and calibrate from the first week's logs.

## Step 4 — Injuries & limitations

Current injuries, chronic issues, movement restrictions. This drives the prehab block
on Day 1 (see `movement-prep.md`). If anything sounds acute or undiagnosed, recommend
a professional evaluation and plan around it conservatively.

## Step 5 — Dietary preferences

Restrictions (gluten-free, dairy-free, vegan, etc.), food likes/dislikes, current
supplement habits. Every nutrition suggestion must respect these.

## Step 6 — Schedule

Preferred training days and times. Sets the default weekly schedule and when the
"pre-workout brief" applies. Confirm which day the long/hardest session goes on
(default: the weekend day they prefer).

## Finish

1. Compute BMR → TDEE → daily macro targets per `nutrition.md`.
2. Generate the plan per `methodology.md` (phase structure anchored to event date or
   an 8–12 week block if no event).
3. Write `coach-data/profile.json` and `coach-data/plan.json` (schemas in
   `data-model.md`), and create an empty `coach-data/log.jsonl` and `notes.md`.
4. Summarize the plan in 3–4 sentences: the arc ("we build from X to Y over N weeks"),
   the weekly rhythm, and how nutrition connects to it.
5. Deliver today's Daily Brief immediately. Day 1 must feel like the product working,
   not a receipt for a form.
