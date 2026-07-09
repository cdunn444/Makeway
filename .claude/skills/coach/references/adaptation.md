# Adaptation Engine (rule-based, MVP)

Run this check after **every** log entry. Adaptation is what separates Coach from a
static plan. Two principles: (1) act on the rules below deterministically, (2) always
tell the user what changed and why, in 1–2 sentences — it should feel like a coach
paying attention, not silent plan mutation. Record every change as a
`kind: "adaptation"` line in `log.jsonl` and update `plan.json`.

**Division of labor with the sync's volume guard:** the activity-sync job runs a
bounded, mechanical volume reconcile every few hours (trim remaining runs when the
week tracks >10% over `miles_target`, pad when >15% under — see `data-model.md`).
Its adaptation lines carry `"source": "auto"`. That guard only moves *mileage
numbers*; everything structural — rescheduling, intensity tiers, skip handling,
restructuring a week — is yours. Read its auto lines when you review the log so
you don't double-compensate, and override its numbers freely: your judgment wins,
just update `miles_target` to match your new intent.

## Rules

### 1. Skipped session → redistribute volume
Redistribute the skipped session's training stimulus across the next 2–3 days,
weighted by goal priority:
- **Key session for the primary goal** (long run, main lift day): reschedule it into
  the next available slot, pushing lesser sessions; if no slot this week, replace the
  lowest-priority session.
- **Secondary session:** fold ~50% of its volume into adjacent sessions (e.g. +1 mi
  on two runs) or let it go if the week is already full. Never stack two hard days
  back-to-back to make up volume.
- One skip is never "made up" by making another day brutally hard.

### 2. Partial session → step down next intensity
The next session **of the same type** drops one intensity tier (interval → tempo →
easy; or -10–15% load / -1 set for strength). One tier only; restore after the next
completed session at the reduced level. Use the partial's actuals to judge — 90%
completed is basically complete; don't penalize it.

### 3. Nutrition significantly over/under → compensate gently
±300 kcal or more vs. target: shift the next 1–2 days' targets to absorb about half
the difference. Never cut tomorrow below what tomorrow's session requires (see
`nutrition.md`). A repeated pattern (4+ days in a week) means the targets are wrong —
recompute them instead of chasing daily corrections.

### 4. Missed 2+ days in a row → check in
Send a check-in, not a guilt trip: "Two days off plan — everything okay? Want me to
restructure the week?" Offer a concrete restructured week (usually: drop the
lowest-priority session, keep the key session, shrink volume ~20%). If the reason
given is illness or injury, restructure conservatively and don't resume quality work
until they report feeling normal.

### 5. Consistent overperformance → progress early
Trigger: 2 consecutive weeks of all sessions completed with logged RPE at or below
target (or actuals beating targets). Advance the progression ahead of schedule — one
notch only (~5–10% volume or one intensity tier), and say why: "You've cruised
through two straight weeks, so I'm bumping your tempo pace 10 s/mi early."
Never break the ≤10%/week volume rule or skip a scheduled down week.

## Skip-reason handling

The micro-prompt answer ("what happened?") routes the response:

| Reason | Response |
|---|---|
| Life logistics (work, kids, travel) | Rule 1 redistribution, no other change. If recurring on the same weekday, propose moving that slot permanently. |
| Fatigue / soreness | Redistribute + downgrade the next quality session one tier. Two fatigue-skips in a week → insert a down week now. |
| Pain / injury | Stop-and-assess: remove aggravating sessions, add relevant prehab (`movement-prep.md`), recommend professional eval if persistent. Do not redistribute the lost volume. |
| Illness | Pause plan; resume at ~70% volume after symptom-free, rebuild over a week. |
| Motivation | Keep it light, shrink the next session so it's easy to win, anchor to the goal ("10 weeks to race day — tomorrow's 3 easy miles keeps you on track"). |

## Weekly review (run when a week's last session is logged, or on request)

1. Completed vs. planned; volume actual vs. planned.
2. Apply rule 5 (progress early) or its inverse (a rough week → hold progression
   flat, don't advance).
3. Regenerate detail for the next 1–2 weeks in `plan.json`.
4. Progress-anchor message: one sentence comparing to 4 weeks ago
   ("A month ago your long run was 4 miles — Saturday you did 7").
