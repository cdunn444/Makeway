# Coach

An adaptive AI fitness coach, built as a **Claude Agent Skill**. Coach replaces the
fragmented stack of training apps, nutrition trackers, and static plans with one
system: a training plan that talks to your nutrition, adapts when life happens, and
remembers what you did last Tuesday.

Based on [Coach PRD v0.1](docs/Coach_PRD_v0.1.md). Claude (chat or Claude Code) is
the entire backend — no app build required.

## What it does

- **Onboarding** — six conversational steps: ad-lib goal setting ("I want to train
  for a half marathon *while* losing weight"), stats, training history, injuries,
  dietary preferences, schedule. Generates your plan and delivers Day 1 immediately.
- **Daily Brief** — the core surface: today's workout, movement prep (including
  prehab for your injuries), and workout-specific nutrition timing. A tempo day and
  a rest day are different nutrition days.
- **Logging** — tell it how the workout went (completed / partial / skipped) in
  plain language. Skips get one "what happened?" prompt that feeds adaptation.
- **Adaptation engine** — rule-based: skips redistribute volume, partials step down
  intensity, missed days trigger a check-in, overperformance progresses the plan
  early. Every change is explained.
- **Schedule & Progress** — week view with move/swap/edit, consistency and volume
  trends, streaks, PRs, and progress anchored against 4 weeks ago.

## Using it in Claude Code

Clone this repo and start Claude Code in it. Then:

```
/coach              # onboard (first time) or today's Daily Brief
/coach log done, 4 miles at 10:30 pace
/coach schedule     # view/edit the week ("move Thursday's run to Friday")
/coach progress     # trends, streaks, milestones
```

Your state lives in `coach-data/` as plain JSON/markdown (`profile.json`,
`plan.json`, `log.jsonl`, `notes.md`) — human-readable, editable, and yours. Commit
the directory to keep history, or gitignore it to keep it private.

## Using it in Claude chat (claude.ai)

Zip the skill and upload it as a Skill (Settings → Capabilities → Skills):

```
cd .claude/skills && zip -r coach.zip coach/
```

In chat, Claude keeps your coach state in the conversation and gives you a JSON
block to save between sessions; for persistent memory, use it inside a Project and
keep `profile.json` / `plan.json` as project files. Claude Code is the best
experience because state persists automatically on disk.

## Repo layout

```
.claude/skills/coach/
  SKILL.md                    # the coach: persona, commands, workflows
  references/
    onboarding.md             # 6-step onboarding flow
    data-model.md             # schemas for profile/plan/log files
    methodology.md            # plan architecture, periodization, goal conflicts
    nutrition.md              # TDEE, macros, session-specific nutrient timing
    movement-prep.md          # warmups by session type + prehab menus
    adaptation.md             # the rule-based adaptation engine
coach-data/                   # your profile, plan, and logs (created at onboarding)
docs/Coach_PRD_v0.1.md        # the product spec this implements
```

## PRD → skill mapping

| PRD feature | Where it lives |
|---|---|
| Onboarding flow (6 screens) | `references/onboarding.md` |
| Daily Brief (workout / prep / nutrition / log CTA) | `SKILL.md` + nutrition & movement-prep references |
| Workout-specific nutrient timing | `references/nutrition.md` |
| Rule-based adaptation engine | `references/adaptation.md` |
| Schedule editing, Progress tracking | `SKILL.md` + `data-model.md` |
| Expert methodology layer | `references/methodology.md` (encoded coaching rules; swap in credentialed-expert content as partnerships land) |
| Push notifications, paywall, RevenueCat, etc. | N/A — out of scope for the skill form factor |

*Coach is a training aid, not medical advice. It will tell you the same thing.*
