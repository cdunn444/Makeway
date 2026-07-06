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
/coach import garmin-week.csv   # weekly Garmin Connect export → auto-logged with real pace/HR
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

## The dashboard (iPhone home-screen app)

`index.html` at the repo root is a self-contained PWA that renders your coach data as
the PRD's app screens — **Daily Brief**, **Schedule**, and **Progress** — with a
floating whistle button (lower right) that deep-links into your most recent Claude
Code coach chat (it reads `coach-data/session.json`, which the skill keeps updated).
Data is fetched live from GitHub on each open, so it shows whatever the coach last
pushed. If the repo is private, tap the gear icon once and paste a fine-grained PAT
with read-only Contents access (stored only on your device).

**Deploy (one-time):** GitHub → repo **Settings → Pages → Source: Deploy from a
branch** → pick `main` (after merging) or this branch, folder `/ (root)`. Your app
URL will be `https://<user>.github.io/Coach/`.

**Install on iPhone:** open that URL in Safari → Share → **Add to Home Screen**.
You get the whistle icon, full-screen app, the works.

**Daily loop:** glance at the dashboard → tap the whistle → tell Coach how the
workout went → Coach logs, adapts, and pushes → pull down to refresh the dashboard.

## Automatic Strava sync

Your Garmin already pushes activities to Strava; a scheduled GitHub Action
(`.github/workflows/strava-sync.yml`) pulls new ones from the official Strava API
every 4 hours, auto-logs them into `coach-data/log.jsonl` with real pace/HR, marks
plan sessions completed/partial, and pushes — so the dashboard updates itself.

One-time setup:

1. Create an API application at [strava.com/settings/api](https://www.strava.com/settings/api)
   (Category: Data Importer, Authorization Callback Domain: `localhost`). Note the
   **Client ID** and **Client Secret**.
2. Authorize it — visit (with your client ID):
   `https://www.strava.com/oauth/authorize?client_id=YOUR_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all`
   Approve; the browser lands on a dead localhost page — copy the `code=...` value
   from the address bar.
3. Exchange the code for a refresh token (one `curl`, or ask Coach to do it):
   `curl -X POST https://www.strava.com/oauth/token -d client_id=YOUR_ID -d client_secret=YOUR_SECRET -d code=THE_CODE -d grant_type=authorization_code`
   — grab `refresh_token` from the response.
4. Add three repo secrets (Settings → Secrets and variables → Actions):
   `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, `STRAVA_REFRESH_TOKEN`.
5. Test it: Actions tab → Strava sync → Run workflow.

Secrets stay in GitHub's encrypted vault — never in the repo files.

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
    garmin-import.md          # wearable export import (CSV/TCX/GPX) + device-data insights
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
