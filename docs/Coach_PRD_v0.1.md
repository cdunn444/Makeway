# COACH — Product Requirements Document

**v0.1 — MVP**

## 1. Overview

Coach is a consumer AI fitness app that replaces the fragmented ecosystem of training apps, nutrition trackers, and static plans with a single adaptive system. It delivers the experience of a full-service personal coach — training plan, nutritional guidance, movement prep, and real-time adaptation — at a fraction of the cost of hiring one.

The core insight: fitness coaching is not just a workout plan. It is a workout plan that talks to your nutrition, adapts when life happens, and remembers what you did last Tuesday. Coach is the first consumer app to integrate all three in a unified daily experience.

## 2. Problem

Serious fitness enthusiasts without access to a personal coach currently manage their training across 4–6 disconnected tools:

- Training plans from Hal Higdon, Nike Run Club, or YouTube
- Workout tracking via Garmin or Strava
- Nutrition logging via MyFitnessPal or Cronometer
- Injury and rehab guidance from ChatGPT or YouTube
- Supplement and recovery notes in spreadsheets or Notes apps

None of these tools talk to each other. A rest day does not adjust your macros. A missed long run does not shift next week's schedule. A tempo run does not trigger a pre-workout carb recommendation. The user carries all of that context in their head — or they don't, and they underperform.

A full-service personal coach solves this. But at $150–$300/month, real coaching is inaccessible to most people. Coach closes that gap.

## 3. Product Vision

**The coach you would have if you could afford one.**

Coach is your daily training partner. It knows your goals, tracks your progress, and adapts your plan in real time when life gets in the way. It tells you not just what to do today, but what to eat before and after — and why. It is built on expert-trained methodology, not generic web data.

## 4. Target User

**Primary** — The committed fitness enthusiast who cannot afford a personal coach. They train consistently, have real goals (a race, a body composition target, a strength milestone), and are frustrated by the overhead of managing multiple apps. They are willing to pay for something that actually works.

**Secondary** — The beginner with a specific goal. They need structure and don't know where to start. Coach removes the guesswork entirely from day one.

**Not the target user (MVP)** — Elite athletes with existing coaching relationships. Casual gym-goers with no specific goal. Users who want community or social features as the primary value.

## 5. Goal Structure

Users define their goals at onboarding using an ad-lib format that naturally establishes priority order:

> I want to **[primary goal]** while **[secondary goal]** and **[tertiary goal — optional]**

Examples:

- I want to train for a half marathon while losing weight
- I want to build strength while improving my 5K time
- I want to lose 20 pounds while staying active

The primary goal drives plan architecture. Secondary and tertiary goals inform nutrition targets, session selection, and weekly volume. The AI resolves conflicts between goals (e.g. caloric deficit vs. training load) using the priority order the user set.

## 6. Onboarding Flow

Onboarding collects the minimum data needed to generate a personalized Day 1 experience. Every screen must feel like it is building something, not filling out a form.

| Screen | Content |
|---|---|
| 1 — Goal | Ad-lib goal builder. Primary goal required. Up to two additional goals optional. |
| 2 — About You | Age, height, weight. Used for TDEE calculation and plan intensity. |
| 3 — Training History | How many days per week do you currently train? What activities? One recent benchmark (5K time, max bench, etc.) |
| 4 — Injuries & Limitations | Any current injuries, chronic issues, or movement restrictions. Drives pre/rehab block on Day 1. |
| 5 — Dietary Preferences | Restrictions (gluten-free, dairy-free, vegan, etc.). Food preferences. Supplement habits. |
| 6 — Schedule | Preferred training days and times. Sets the default weekly schedule. |

Fields explicitly excluded from onboarding: location.

## 7. App Structure

Four primary screens accessed via bottom tab navigation. No fifth tab.

| Tab | Purpose |
|---|---|
| Daily Brief | Today's workout, movement prep, and nutrition — the primary daily surface |
| Schedule | Weekly and monthly training calendar with editing and planning tools |
| Progress | History, trends, consistency tracking, and goal milestones |
| Profile | Goals, personal stats, dietary preferences, notification settings |

## 8. Daily Brief Screen

The Daily Brief is the core product surface. It answers one question: what do I do today, and how do I fuel it? Every element on this screen connects to the user's primary goal and today's training session.

### 8.1 Header

- Date and greeting
- One-line context sentence tied to session type — e.g. "Tempo run day — load up on carbs this morning"

### 8.2 Workout Block

- Today's session with type, distance or volume, and estimated duration
- Tap to expand: full workout detail, sets/reps, pacing targets, or run structure
- Session type drives nutrition block content (endurance vs. strength vs. rest vs. active recovery)

### 8.3 Movement Prep Block

- Pre-workout activation and mobility work tied to today's session type
- Pre/rehab exercises based on user's injury history and logged limitations
- Expandable with video or instruction detail

### 8.4 Nutrition Block

This is the primary differentiator. Nutrition is not generic daily macro math — it is workout-specific nutrient timing.

- Daily macro targets (calories, protein, carbs, fat) calculated from TDEE + training load
- Pre-workout meal suggestion with specific timing — e.g. "60 min before: rolled oats, banana, black coffee"
- Post-workout recovery window — e.g. "Within 30 min: protein shake + fast carbs"
- Adjusts automatically based on session type — rest day macros differ from long run macros
- Respects dietary restrictions set in profile

### 8.5 Log CTA

- Single tap to log workout as: Completed / Partial / Skipped
- Partial log captures what was actually done (distance, sets completed, etc.)
- Skipped triggers a micro-prompt: what happened? — feeds adaptation engine
- Log state persists and is visible on Schedule screen

## 9. Adaptation Engine

The adaptation engine is what separates Coach from a static plan generator. It responds to logged data and adjusts future sessions and nutrition targets accordingly.

**MVP Adaptation Rules (rule-based)**

- Skipped session → volume redistributed across next 2–3 days based on priority
- Partial session → following session intensity adjusted down by one tier
- Logged nutrition significantly over/under target → next day macro targets shift to compensate
- Missed workout 2+ days in a row → check-in prompt, potential week restructure
- Consistent overperformance → plan progression triggered ahead of schedule

Note: MVP adaptation is rule-based logic, not ML. True adaptive AI is a post-MVP milestone once sufficient user data exists to train on.

## 10. Schedule Screen

- Default view: current week, with swipe navigation forward and back
- Each day shows session type and volume at a glance
- Tap any day to see full detail or edit inline
- Drag to reschedule — swap two days or move a session
- Edit distance, duration, or intensity on any future session
- Rest days visible and labeled — not empty
- Completed sessions marked, skipped sessions flagged
- Toggle to month view for longer-range planning

## 11. Progress Screen

- Training consistency: sessions completed vs. planned, rolling 4-week view
- Volume trends: weekly mileage, total lifting volume, or combined load
- Goal milestone tracking: progress toward primary goal with projected timeline
- Streak tracking: consecutive days trained, consecutive weeks on plan
- Nutrition adherence: macro targets hit over time
- Personal records: auto-detected from logged sessions

## 12. Accountability & Retention

Push notifications are table stakes. The retention mechanics that matter:

- Streak integrity — missing a session has visible consequence on the Progress screen, not just a missed day
- Check-in friction on skipped sessions — logging why you missed feeds the engine and builds habit
- Progress anchoring — weekly summary shows where you were 4 weeks ago so quitting feels costly
- Pre-workout brief notification — delivered based on user's scheduled training time, not a generic daily push
- Nutrition timing nudge — "Your tempo run starts in 90 min. Did you eat?"

## 13. Expert Methodology Layer

Coach is not built on generic AI-generated fitness content. The plan architecture, periodization logic, and nutritional timing guidance are built in collaboration with credentialed experts — running coaches, strength and conditioning specialists, and registered dietitians — whose methodology trains the AI layer.

This serves two purposes:

- Credibility and differentiation in a crowded market
- Legal and medical defensibility — plans are grounded in established, attributed methodology

Expert partnerships are a pre-launch requirement, not a post-MVP addition. The brand story depends on it.

## 14. Monetization

**Primary: Subscription**

| Tier | Description |
|---|---|
| Free | Goal setting, static weekly plan, basic macro targets. No AI adaptation. No workout-specific nutrition timing. |
| Coach Pro (~$19.99/mo) | Full adaptive plan, workout-specific nutrition brief, movement prep, progress tracking, push notifications. |
| Coach + Human (~$49.99/mo) | Everything in Pro plus monthly check-in with a real certified coach. Plan review, goal adjustment, Q&A. |

The free tier demonstrates the value of the plan. The paywall is the adaptation engine and the nutrition brief — the two things users cannot replicate easily in another app.

**Future Revenue Vectors**

- Expert coach marketplace — subscribe to a specific coach's program
- Corporate wellness partnerships
- Supplement or nutrition brand integrations (non-advertising, curated)

## 15. Competitive Landscape

| Competitor | Overlap | Gap Coach fills |
|---|---|---|
| Future / Ladder | Human coach + adaptive plan | No workout-specific nutrition brief. Expensive ($19–$200/mo for human access). |
| Whoop Coach | Recovery-based AI coaching | Whoop hardware required. No training plan generation or nutrition. |
| Hoola | Training + macro-matched nutrition | New (2025), unproven methodology. No expert IP layer. |
| BodBot | Workout-nutrition sync | Nutrition is macro math, not periodization-aware timing. Weak UX. |
| MyFitnessPal + Garmin | Nutrition + training tracking | No integration. User carries all context. No adaptation. |
| Purple Patch | Full-service coaching with nutrition | $300/mo, triathlon-specific. Not accessible to general consumer. |

## 16. MVP Scope

**In scope**

- Onboarding flow (6 screens)
- Daily Brief screen with workout, movement prep, and nutrition blocks
- Manual workout logging (completed / partial / skipped)
- Basic rule-based adaptation engine
- Schedule screen with week view and basic editing
- Push notification for daily brief and workout timing
- Subscription paywall (free vs. Pro)
- Claude API integration for plan generation and nutrition guidance

**Out of scope for MVP**

- Wearable integrations (Garmin, Apple Health, Google Fit) — defer to v1.1
- True ML adaptation engine — defer until sufficient user data
- Human coach tier — defer to v1.2
- Social or community features
- In-app food logging / barcode scanning
- Month view on Schedule screen

## 17. Suggested Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React Native (Expo) — iOS + Android from one codebase |
| AI layer | Claude API (Anthropic) — plan generation, nutrition guidance, adaptation logic |
| Backend / DB | Supabase — auth, database, real-time |
| Notifications | Expo Notifications |
| Payments | RevenueCat — subscription management across iOS and Android |
| Analytics | PostHog or Mixpanel — retention and funnel tracking |

## 18. Open Questions

- App name — "Coach" has trademark risk. Final name TBD.
- Expert partner strategy — who are the credentialed co-creators for launch? Running, strength, and nutrition covered separately or one generalist?
- Free tier paywall placement — confirm that adaptation engine and nutrition brief are the right features to gate, not the plan itself.
- Onboarding benchmark field — mandatory or optional? Skipping it reduces personalization on Day 1.
- AI model prompting strategy — how is expert methodology encoded into Claude API system prompts? Needs architecture decision before build.

---

*Coach — Product Requirements Document v0.1 — Confidential*
