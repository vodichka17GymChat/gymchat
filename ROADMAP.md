# GymChat — Execution Roadmap

## Strategy

**Two-stage approach: validate in Streamlit, then rebuild in production.**

The Streamlit prototype already has a working core (auth, workout logging, history, profile). Rather than rebuilding immediately on React Native, we extend Streamlit aggressively to validate every UX decision and data model before committing to the production stack. When the product is fully mapped in Streamlit, the React Native rebuild becomes translation work, not design work.

```
Stage 1: Streamlit (now)           Stage 2: Production (later)
─────────────────────────────      ──────────────────────────────────
Validate features fast             React Native + Expo (iOS + Android)
Cheap to iterate with Claude Code  Supabase (Postgres + auth + storage)
Investor demo quality              Real users, real retention
No app store friction              App store launch
```

**Why this order saves time and money:**
- Building a feature wrong in Streamlit costs 30 minutes to fix. Building it wrong in React Native costs days.
- Every layout decision, every data model change, every interaction pattern gets proven before a line of RN is written.
- Claude Code can iterate on Streamlit at high speed; the production rebuild becomes mostly "port this validated UX."

---

## Phase 1 — Complete the Tracking Foundation
**Streamlit | Goal: All 5 data domains working**

The first phase fills the gaps in the existing prototype so GymChat can capture a complete picture of any athlete's week.

### 1.1 Strengthen workout tracking (extend what exists)

| Feature | Description |
|---|---|
| Workout templates | Save any completed session as a reusable template. Relaunch it with one tap, pre-filled with last session's weights. |
| Program builder | Chain templates into a multi-week block (e.g., "12-week hypertrophy: 4 days/week, progressive overload built in"). Each session links to a program day. |
| Superset / circuit support | Group 2+ exercises inside a session. Rest timer counts down between rounds, not between individual exercises. |
| Plate calculator | Given a target weight and bar weight, show which plates to load. Configurable for standard and metric plates. |
| Custom exercises | User can create an exercise not in the seeded library. Stored per user, not globally. |
| Bodyweight / assisted exercises | Support weight = 0 for bodyweight. Support negative weight for band-assisted or machine-assisted movements. |

### 1.2 Body composition tracking

New page: **Body**. Accessible from sidebar.

| Feature | Description |
|---|---|
| Weight log | Daily body weight entry. Chart: raw weight + 7-day moving average. |
| Body measurements | Tape measurements: waist, hips, chest, arms (L/R), thighs (L/R). Logged per date. Trend charts per measurement. |
| Body fat % | Manual entry from any measurement method (DEXA, calipers, scale). Optional. |
| Progress photos | Upload a photo per date with a category tag (front, back, side). Side-by-side comparison of any two dates. Private by default. |
| Muscle heatmap | Repurpose the existing `body_diagram.py` component to show which muscle groups were trained most this week (volume-weighted heat map). |

### 1.3 Cardio & endurance tracking

New section within the Workout page or new page: **Cardio**.

| Feature | Description |
|---|---|
| Manual session entry | Log: activity type, duration, distance, avg heart rate, perceived effort (RPE). Stored per session per user. |
| Activity types | Running, cycling, swimming, rowing, HIIT, walking, hiking, other. |
| Cardio history | List view of past cardio sessions. Per-activity trend charts (pace over time, distance over time). |
| Training load | Cardio volume contributes to the weekly fatigue/load score alongside lifting. Shown on dashboard. |

### 1.4 Nutrition tracking

New page: **Nutrition**.

| Feature | Description |
|---|---|
| Daily macro targets | User sets daily calorie, protein, carb, fat targets (manually or from a simple TDEE calculator: weight + activity level + goal). |
| Meal logging | Log food entries per meal (breakfast, lunch, dinner, snacks, pre/post-workout). Each entry: food name, calories, protein, carbs, fat, quantity. |
| Food database | Searchable, seeded with common foods. User can add custom foods. |
| Daily summary | Calories and macros consumed vs. target. Visual progress bar per macro. |
| Nutrition history | 7-day and 30-day charts: calories vs. target, protein consistency. |
| Water intake | Simple counter (glasses or ml). Optional but useful. |

**AI budget note:** Nutrition targets are calculated with deterministic formulas (Mifflin-St Jeor TDEE + goal adjustment). No AI API calls needed for this phase.

### 1.5 Dashboard redesign

Expand the existing dashboard to show all 5 domains at a glance:
- Weekly training summary (sessions, volume, sets) — exists today
- Weekly cardio summary (sessions, total distance/time) — new
- Weekly nutrition average (avg calories vs. target, avg protein) — new
- Body weight trend (this week vs. last week) — new
- Recovery snapshot (sleep hours logged, avg energy pre-workout) — already collected, just not surfaced

**Success criteria for Phase 1:** A user can log a full week of training, cardio, meals, and body weight — and see a coherent summary of it all on one screen.

---

## Phase 2 — Rule-Based Analytics & Intelligence
**Streamlit | Goal: The app feels smart without AI API costs**

Most of what users call "AI" in fitness apps is actually deterministic analytics. Phase 2 builds that layer using pure Python logic — no API calls, no variable costs.

### 2.1 PR detection and celebration

- After every set is logged, check if it is a new personal record for that exercise at that rep range.
- PR tiers: 1RM estimated (Epley formula), 3RM, 5RM, 8RM, 10RM+.
- Surface: a highlighted card on the workout page ("New PR: 120kg × 3 on Squat 🏆"), and in the post-workout summary.
- Store PR history per user per exercise.

### 2.2 Progressive overload tracker

- For each exercise, compare this session's top set to the same exercise's top set in the previous session.
- Flag: increased weight (+), same weight (=), decreased weight (−).
- Surface on history and exercise detail: "You've progressed on bench press 4 sessions in a row."

### 2.3 Volume trend analysis

- Weekly volume per muscle group (sum of weight × reps × sets, normalized).
- Chart: current week vs. 4-week rolling average.
- Flag: volume spike (>20% above average) or volume drop (>20% below average).
- Surface on dashboard: "Your quad volume this week is 40% above your recent average. Consider a deload soon."

### 2.4 Weekly analytics report

A generated report available every Monday. Built from deterministic queries, no AI.

Contents:
- Top PRs this week
- Volume by muscle group vs. prior week
- Cardio summary
- Nutrition consistency (% of days hitting protein target)
- Body weight change (7-day avg vs. prior 7-day avg)
- Training streak
- 2–3 observations (rule-based: "You haven't trained legs in 9 days." / "You've hit your protein target 6 out of 7 days this week.")

### 2.5 AI cold start counter

Track how many completed workouts a user has. Store as `workouts_completed` on the user record (or count from DB).

- Below 3 workouts: UI shows no AI nudges. App is a clean tracker.
- At 3 workouts: First analytics unlock. Surface a message: "GymChat now has enough data to start giving you insights."
- This logic will be repurposed in production to gate AI API calls the same way.

### 2.6 Fatigue / readiness signal

From existing data (energy pre-workout, sleep hours, HRV if available, recent volume):
- Compute a simple readiness score (0–10) using a weighted formula.
- Surface on the workout start page: "Your readiness score today is 6/10. You've trained 5 days straight and slept under 7 hours. Consider a lighter session."

**Success criteria for Phase 2:** A user opening the app on Monday morning sees a weekly report that feels personalized and accurate — with zero AI API calls.

---

## Phase 3 — Social Layer
**Streamlit | Goal: GymChat becomes a community, not just a tracker**

Social features are the primary driver of retention and viral growth. Phase 3 builds the social foundation.

### 3.1 Public profiles

Each user gets a public profile page at `/user/{username}`:
- Display name, bio, avatar (uploaded or initials fallback)
- Training stats: total sessions, total volume, longest streak, current streak
- Recent PRs
- Activity feed (recent workouts posted)
- Followers / following counts

### 3.2 Following and social feed

- Follow any public user.
- A **Feed** page shows recent activity from followed users:
  - Completed workout posts (auto-generated from session end, user opts in to post)
  - PR announcements
  - Progress photo shares (explicit opt-in)
- Post reactions: "Lift" (thumbs up), "Fire", "Impressed" (3 reactions, no open-ended likes to avoid engagement dark patterns).
- Comments: basic threaded text.

### 3.3 Workout sharing

- When ending a workout, offer "Share this session."
- Generates a shareable summary card: exercises, total volume, top sets, any PRs.
- Card is posted to feed and optionally shareable as a static image (export).

### 3.4 Challenges (v1)

Start with the two most tractable challenge types:

| Challenge Type | How it works |
|---|---|
| Consistency challenge | Creator sets: "5 workouts per week for 4 weeks." Participants track against this. Live leaderboard. |
| Volume race | Creator picks a muscle group (e.g., chest). First to hit X kg total volume wins. |

Challenge creation: any user can create a challenge and invite friends by username or link.

### 3.5 "Try my workout" template sharing

- Any workout template can be published publicly.
- Other users can copy it, run it, and log their results against it.
- Leaderboard: who lifted the most total volume on this template, who completed it fastest.
- **Famous athlete programs**: First batch of templates hand-curated (Arnold split, Ronnie Coleman program, etc.) and featured on an Explore page.

**Success criteria for Phase 3:** A user can see their friends' workouts, react to PRs, and challenge a friend to a consistency race — all within the app.

---

## Phase 4 — Production Setup
**Goal: Stand up the Supabase + React Native foundation**

Phase 4 runs in parallel with Phase 3 (or immediately after), establishing the production infrastructure while Streamlit is still being refined.

### 4.1 Supabase setup

| Task | Detail |
|---|---|
| Project creation | Supabase project, region selection (closest to target users) |
| Schema migration | Translate `db/schema.sql` (SQLite) to Postgres. Add new tables from the vision data model. |
| Row-level security | Every table has RLS policies: users can only read/write their own data; public profiles are readable by all. |
| Auth | Email + password (Supabase Auth). OAuth (Google, Apple) — essential for mobile. |
| Storage | Supabase Storage buckets: `progress-photos` (private), `avatars` (public), `exercise-media` (public). |
| Realtime | Enable Postgres realtime for social feed (new posts trigger live feed updates). |

### 4.2 React Native / Expo project setup

| Task | Detail |
|---|---|
| Expo project init | `npx create-expo-app gymchat --template` with TypeScript |
| Expo Router | File-based routing (same mental model as Next.js App Router) |
| Supabase client | `@supabase/supabase-js` configured with Expo SecureStore for token persistence |
| NativeWind | Tailwind CSS for React Native — consistent styling system |
| Design tokens | Port the existing CSS tokens from `components/theme.py` into a NativeWind config |
| Navigation structure | Tab bar: Feed / Workout / Track / Analytics / Profile |

### 4.3 Auth flow

- Onboarding screens: splash → email/password registration → profile setup (mirrors existing `3_Profile.py`) → first workout prompt
- Login screen with "forgot password" (Supabase handles email reset)
- OAuth: Sign in with Google and Sign in with Apple (required for App Store)

### 4.4 CI/CD pipeline

| Tool | Purpose |
|---|---|
| GitHub Actions | Run type checks and lint on every PR |
| Expo EAS Build | Cloud builds for iOS and iOS Simulator, Android APK |
| EAS Update | OTA updates for JS-only changes (no app store review needed) |
| TestFlight | iOS beta distribution to friends and community |
| Supabase CLI | Schema migrations versioned in git |

**Success criteria for Phase 4:** A team member can install the app on their iPhone via TestFlight, create an account, and see an empty home screen — auth working end-to-end.

---

## Phase 5 — React Native Core App
**Goal: Port the validated Streamlit UX into production**

With the Streamlit prototype fully validating the UX, Phase 5 is translation work. The data model, interaction patterns, and business logic are already proven.

### 5.1 Strength tracking (port from Streamlit)

Port order follows the existing Streamlit component structure:

1. Exercise picker → `ExercisePicker` component
2. Set logger → `SetLogger` component (weight, reps, RPE/RIR/rest)
3. Rest timer → `RestTimer` component (uses `setInterval`, not `@st.fragment`)
4. Exercise card → `ExerciseCard` component
5. Workout session page → `WorkoutScreen`
6. Start workout form → `StartWorkoutModal`
7. End workout flow → `EndWorkoutSheet`

### 5.2 History and analytics screens

1. Session list with expandable session cards
2. Per-exercise progression chart (Victory Native or Recharts-native)
3. PR history per exercise

### 5.3 Profile and settings

1. Profile form (port from `3_Profile.py`)
2. Settings: units (kg/lbs), AI voice preferences, notification preferences
3. Account management: change password, delete account

### 5.4 Body composition screens

1. Weight log entry + history chart (moving average)
2. Measurements entry + history
3. Progress photos grid + comparison view
4. Body muscle heatmap (SVG repurposed from `body_diagram.py`)

### 5.5 Cardio screens

1. Log cardio session form
2. Cardio history list
3. Cardio trend charts

### 5.6 Nutrition screens

1. Daily nutrition dashboard (macros vs. target, visual progress bars)
2. Meal entry form (food search, custom food entry)
3. Nutrition history charts
4. Daily targets setup

**Success criteria for Phase 5:** A user can use the React Native app as a complete replacement for the Streamlit prototype — all 5 tracking domains working on mobile.

---

## Phase 6 — Social and Engagement Layer (RN)
**Goal: Build network effects into the production app**

Port and extend the social features validated in Streamlit Phase 3.

### 6.1 Social infrastructure

- User search and discovery
- Follow / unfollow
- Push notifications: new follower, post reaction, PR congratulation
- Deep linking: every post and profile is a shareable URL

### 6.2 Feed

- Chronological feed of followed users' activity
- Post types: workout, PR, progress photo, challenge milestone
- Reactions and comments
- "Explore" tab: trending workouts, featured challenges, top PRs this week

### 6.3 Challenges system

All challenge types from the vision (consistency, PR race, volume, 1RM, try-my-workout, leaderboard). Challenge creation wizard, live leaderboards, completion badges.

### 6.4 Workout templates and programs

- Template library (personal + public)
- Program browser (personal + featured)
- Famous athlete programs (Arnold, Coleman, etc.)
- Program enrollment: today's session auto-suggested from enrolled program

**Success criteria for Phase 6:** A user posts a workout, a friend reacts to their PR, and three friends join a consistency challenge together.

---

## Phase 7 — AI Coaching Layer
**Goal: Add the AI features that justify the premium subscription. Execute when funded.**

This phase is gated on having AI API budget. The rule-based analytics from Phase 2 provide real value in the interim; Phase 7 upgrades them with genuine AI reasoning.

### 7.1 AI backend service

A dedicated AI service (Python, FastAPI) that calls the Claude API. Reasons for a separate service:
- Control costs (rate limiting per user, per tier)
- Cache responses where appropriate (weekly reports are generated once, not per request)
- Async generation (weekly report runs as a background job, not on request)

### 7.2 Weekly AI report (Phase 2 upgrade)

Swap the deterministic report generator for a Claude-powered version:
- Pass the week's structured data as context
- Claude writes the observations and recommendations in the user's configured voice
- Generated once per week as a background job (low API cost: ~1 call per active user per week)
- Store the generated report; serve from cache on subsequent reads

**Cost estimate:** ~$0.01–0.03 per report per user per week (Haiku-class model). At 1,000 MAU, ~$10–30/week.

### 7.3 Conversational coach

In-app chat interface (bottom sheet accessible from any screen during a workout):
- System prompt includes: user's full training history summary, current session data, recent body/nutrition/cardio data, goals
- Streaming responses for low perceived latency
- Conversation history stored in `ai_conversations` table
- Rate limited: free tier gets 5 messages/day; premium gets unlimited

**Cost estimate:** ~$0.02–0.10 per conversation (Sonnet-class). Design system prompt carefully to minimize tokens.

### 7.4 AI program design

A dedicated screen: "Generate my next training program."
- User inputs: goal, days/week, equipment, experience, time per session, any injuries
- Claude generates a structured program (multi-week, day-by-day, with sets/reps/progression rules)
- Output parsed into the program data model and saved as a template
- One API call per program generation; result stored and reused

**Cost estimate:** ~$0.05–0.20 per program (longer context + structured output). Users generate programs infrequently.

### 7.5 Wearable integrations

- Apple Health (HealthKit) — priority; required for iOS
- Garmin Connect API
- Whoop API
- Oura API
- Daily sync job: pull HRV, sleep, resting HR. Store in `wearable_syncs`. Feed into readiness score.

**Success criteria for Phase 7:** A premium user receives a weekly AI report that references their actual data by name, gets coaching advice during a workout that acknowledges their fatigue from last week, and has an AI-generated 8-week program they are currently running.

---

## Phase 8 — Scale to 1K MAU
**Goal: Grow, retain, and measure**

### 8.1 App store launch

- App Store (iOS): requires Apple Developer account ($99/year), TestFlight beta → production
- Google Play (Android): requires Google Play Console account ($25 one-time), internal testing → production
- App store optimization (ASO): screenshots, preview video, keyword-optimized description

### 8.2 Referral and sharing mechanics

- Share a PR as an image to Instagram/Twitter/iMessage (custom card with GymChat branding)
- Invite a friend to a challenge (link-based, opens app or app store)
- "Share your stats" — shareable year-in-review card (Spotify Wrapped model)

### 8.3 Onboarding optimization

- Measure: what % of installs complete profile setup? What % log a first workout within 24 hours?
- Test: different onboarding flows using Expo EAS Channels (A/B test new users)
- Goal: >60% of registrations log a first workout within 48 hours

### 8.4 Retention mechanics

- Day 1 / Day 3 / Day 7 push notifications (contextual, not generic): "You haven't logged a session in 4 days. Your last squat was 100kg. Ready to beat it?"
- Weekly report notification: "Your GymChat weekly report is ready."
- Streak counter: visible on profile and in notifications
- Challenge deadline alerts: "Your challenge ends in 2 days. You need 1 more session."

### 8.5 Analytics and measurement

Set up telemetry from day 1 in production:

| Metric | Tool |
|---|---|
| MAU / DAU | PostHog (open source, self-host or cloud) |
| Retention cohorts | PostHog |
| Funnel: install → first workout → Day-7 active | PostHog |
| Error tracking | Sentry |
| API performance | Supabase dashboard |
| Revenue | RevenueCat (manages App Store + Play subscriptions) |

**Success criteria for Phase 8:** 1,000 monthly active users, >50% still active 30 days after registration, and at least 100 paying premium subscribers.

---

## AI Cost Strategy (Low Budget)

Given low initial budget, follow this cost ladder:

| Phase | AI approach | Cost |
|---|---|---|
| Phases 1–3 | Zero AI API calls. All analytics are deterministic Python. | $0 |
| Phase 7 launch | Weekly reports only. Haiku-class model, batched, cached. | ~$10–30/mo at 1K MAU |
| Phase 7 growth | Add conversational coach, rate-limited for free tier. | ~$50–200/mo at 1K MAU |
| Post-funding | Lift rate limits, add program design, real-time coaching. | Scales with revenue |

The rule-based analytics from Phase 2 are not a compromise — they are the product until the AI layer is funded. Many users will not notice the difference between a well-crafted deterministic report and an AI-written one. The AI layer upgrades the quality and personalization, not the fundamental value.

---

## Claude Code Execution Model

Since Claude Code is writing the code, each session should follow this pattern:

1. **One phase at a time.** Don't jump ahead. Finish Phase 1 before starting Phase 3.
2. **Feature by feature.** Tackle one table item at a time. Smaller scope = higher quality output.
3. **Validate before moving on.** After each feature, run the Streamlit app and test it manually before asking Claude Code to build the next thing.
4. **Commit frequently.** Every working feature gets a commit. This creates a clean history and easy rollback points.
5. **Keep CLAUDE.md updated.** As the architecture evolves (new tables, new services, new pages), update `CLAUDE.md` so Claude Code always has accurate context.

---

## Current State vs. Roadmap

```
Phase 1 (Streamlit tracking)
  [✓] Auth (scrypt)
  [✓] Strength workout logging
  [✓] Per-set: weight, reps, RPE, RIR, rest
  [✓] Rest timer
  [✓] Exercise library (66 exercises)
  [✓] History + progression charts
  [✓] Dashboard (weekly stats)
  [✓] Profile
  [✓] Body diagram component (unused, available)
  [ ] Workout templates
  [ ] Program builder
  [ ] Superset support
  [ ] Plate calculator
  [ ] Custom exercises
  [ ] Body composition page
  [ ] Cardio logging
  [ ] Nutrition logging
  [ ] Dashboard redesign (all 5 domains)

Phase 2 (Rule-based analytics)
  [ ] PR detection
  [ ] Progressive overload tracker
  [ ] Volume trend analysis
  [ ] Weekly report (deterministic)
  [ ] Readiness score
  [ ] AI cold start counter

Phase 3 (Social)
  [ ] Public profiles
  [ ] Following / feed
  [ ] Workout sharing
  [ ] Challenges (v1)
  [ ] Template sharing

Phase 4–8: Not started
```

---

## Next Session

The natural next step is **Phase 1.1 — workout templates**. It extends what already works (workout sessions) and unlocks program builder. Suggested prompt for the next Claude Code session:

> "Build workout template support in the Streamlit app. A user should be able to save any completed session as a named template, see a list of their templates, and relaunch a template to start a new session pre-populated with the same exercises and last-used weights."
