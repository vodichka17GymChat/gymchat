# GymChat — Product Vision

> **One app. Every rep, run, meal, and milestone. An AI that gets smarter with every workout. A community that makes you better.**

---

## 1. Product Identity

### The problem

The average serious athlete uses 4–6 apps to manage their fitness life. Strong or Hevy for lifting. Strava for running. MyFitnessPal for food. Whoop or Oura for sleep and recovery. Apple Health as a data graveyard. None of these apps talk to each other. Progress photos live in a camera roll. PR milestones disappear into a group chat. Training programs get emailed as PDFs.

The data fragmentation is a solved-problem waiting for the right product. Every piece of data already exists in some app on a user's phone. What doesn't exist is a single platform that holds it all, understands the relationships between it, and uses that understanding to make the athlete better.

GymChat is that platform.

### The one-sentence pitch

GymChat is the AI-powered fitness super-app that replaces every fitness tracker you own — logging every rep, run, meal, and body measurement, coaching you based on the full picture, and connecting you to a community that trains alongside you.

### The vision

Make every other fitness app obsolete.

Not through feature stuffing, but through unification. GymChat treats strength, cardio, nutrition, body composition, and biometric data as a single interconnected system — because they are. When you slept poorly, your AI coach knows to reduce intensity today. When your volume has climbed steadily for four weeks, it knows a deload is due. When you hit a PR, your feed knows to celebrate it. No other app sees all of this at once.

The flywheel: more users → richer training data → smarter AI → better outcomes → more users.

---

## 2. Target Users

**Everyone who trains.** GymChat is not a niche tool for powerlifters or competitive athletes. It is for anyone who has a fitness goal and wants to pursue it with better information and better community.

**Primary persona: The dedicated gym-goer.** Trains 3–5 days per week. Tracks some things (maybe a notebook, maybe Strong) but has no unified picture of their health. Motivated by progress and community. Will pay for tools that demonstrably improve their results.

**Secondary persona: The competitive athlete.** Powerlifter, Olympic lifter, endurance athlete, or crossfitter. Sophisticated data needs. High willingness to pay. Strong voice in communities that influence broader adoption.

**Tertiary persona: The fitness beginner.** Just starting out. Overwhelmed by options. Needs structure, not complexity. The social layer and AI program design are key retention hooks here.

**Geography and context:** The primary use surface is a mobile phone in the gym. Every interaction — logging a set, starting a cardio session, checking analytics — must work with one hand, in loud lighting, between sets. Speed and clarity are non-negotiable at the input layer.

---

## 3. Product Pillars

GymChat is organized around four pillars that form a feedback loop:

```
TRACK → ANALYZE → COACH → CONNECT
  ↑                              |
  └──────────────────────────────┘
```

**Track**: Capture every input with minimal friction — sets, reps, pace, calories, weight, sleep, HRV. If logging something takes more than 10 seconds, the design has failed.

**Analyze**: Transform raw data into insight. Volume trends, PR proximity, caloric surplus/deficit, body composition change, recovery scores. Instantly interpretable. No spreadsheets required.

**Coach**: Use the full data picture to tell athletes what to do next. Not just "here is a chart" but "here is why you should go lighter today" and "here is what your next mesocycle should look like." The AI sees everything.

**Connect**: Make progress social. Share workouts, race each other on PRs, challenge friends, follow athletes whose training you admire. The community layer turns isolated tracking into a shared journey.

---

## 4. Feature Domains

### 4.1 Strength Training (current prototype → extended)

The core of GymChat today. Every workout session flows through:
`workout_sessions` → `exercise_executions` → `sets`

**What exists:**
- 56 seeded exercises across 10 muscle groups, tagged compound/isolation
- Per-set logging: weight + reps (required), RPE, RIR, rest override (optional)
- Session context: workout type, gym location, sleep hours, energy level
- Rest timer (live, fragment-based, no full-page rerun)
- Exercise picker with muscle group filtering
- History with per-exercise progression charts
- Dashboard with session summaries and volume stats

**What gets added:**
- Superset and circuit support (group exercises within a session)
- Plate calculator (given a target weight, show what to load)
- Warm-up set tracking (distinct from working sets in volume calculations)
- Custom exercise creation (user-defined movements, muscles)
- Exercise substitution suggestions (AI-driven, based on equipment availability)
- Bodyweight and band-assisted/resisted exercise support
- Workout templates — save any session as a reusable template
- Program builder — a sequence of templates forming a training block (e.g., 12-week strength cycle)

### 4.2 Cardio & Endurance

**Modalities**: Running, cycling, swimming, rowing, HIIT, walking, hiking, and open-ended "activity."

**Tracked per session:**
- Duration, distance, pace (per km/mile)
- Heart rate: average, max, zones (Z1–Z5)
- Elevation gain/loss (where GPS or manual input provides it)
- Perceived effort / RPE
- Cadence (for run/cycle where available)
- Split data (lap-by-lap breakdown)

**Analytics:**
- Pace and distance trends over time
- Time-in-zone distribution
- Estimated VO2max progression (calculated from pace + HR data)
- Integration with training load — cardio volume contributes to weekly fatigue score alongside lifting

**Input methods:**
- Manual entry (distance + duration, optionally pace)
- GPS session (mobile-native, when app moves to native)
- Wearable import (see Section 4.5)

### 4.3 Nutrition & Diet

Nutrition is not an afterthought — it is half of the fitness equation. GymChat connects eating to training in a way that standalone nutrition apps cannot.

**Tracking:**
- Calories, protein, carbohydrates, fat, fiber per meal and per day
- Meal logging: breakfast, lunch, dinner, snacks, pre/post-workout
- Food database: barcode scan (native), search (text), custom foods, frequent/recent foods
- Water intake

**Planning:**
- Daily macro targets (set manually or AI-calculated based on goals and training load)
- Meal plans generated by AI (given training week, body goals, preferences)
- Caloric periodization — AI adjusts targets on rest days vs. heavy training days
- Diet plan types: maintenance, bulk, cut, recomp

**Analytics:**
- Daily/weekly calorie and macro summary
- Trend charts: calories vs. training volume over time
- Protein timing analysis (pre/post-workout windows)
- Consistency score (how often the user hits their targets)

**Integration with training:**
- AI uses training load to adjust daily calorie target dynamically
- Post-workout reminders to log food if post-workout nutrition window has elapsed
- Body composition change correlated with caloric surplus/deficit history

### 4.4 Body Composition & Progress Tracking

**Measurements:**
- Body weight (primary metric; tracked over time with moving average to smooth noise)
- Body fat percentage (manual entry or device-measured)
- Tape measurements: waist, hips, chest, shoulders, arms (L/R), thighs (L/R), calves (L/R)
- Skeletal muscle mass (from compatible scales/devices)

**Progress photos:**
- Stored per date with optional category tag (front, back, side, flex)
- Side-by-side comparison view (any two dates)
- Photo visibility: private by default; opt-in to share to social profile

**Analytics:**
- Weight trend with 7-day moving average
- Body measurement change over custom date ranges
- Correlation view: body weight trend vs. caloric surplus/deficit
- Estimated body recomposition curve

**Unused asset from prototype:**
`body_diagram.py` exists in the codebase but is currently unused. It is a candidate for powering a muscle-group heat map on the body composition page (e.g., "these are the muscles you trained most this week").

### 4.5 Wearables & Biometric Sync

GymChat does not replace wearables — it aggregates them.

**Supported integrations (phased):**
- Apple Health (iOS HealthKit) — primary gateway; pulls steps, HR, sleep, workouts
- Google Fit / Health Connect (Android) — equivalent Android gateway
- Garmin Connect — advanced running/cycling/swim metrics, HRV
- Whoop — recovery score, strain, sleep performance, HRV
- Oura Ring — readiness score, sleep stages, body temperature, HRV
- Polar Flow — HR and training load data
- Fitbit — steps, sleep, HR

**Data imported:**
- Daily HRV (heart rate variability)
- Resting heart rate
- Sleep: total duration, deep/REM/light/awake split, sleep score
- Recovery/readiness score (device's own composite)
- Step count and active energy
- Automatically detected workouts (import or skip, user decides)

**How it feeds the AI:**
- Recovery score is a first-class input to workout intensity recommendations
- HRV trend informs overtraining detection
- Sleep quality correlates with next-day session energy level (which the user also self-reports)
- Resting HR trend is displayed alongside training volume as a recovery proxy

---

## 5. Social Layer

GymChat is a fitness community, not just a fitness tracker. The social layer is what turns individual data into network value — and what makes the AI better for everyone.

### 5.1 Public Profiles

Each user has a public profile with:
- Display name, bio, avatar
- Athlete type and primary goals
- Training stats: total sessions, total volume lifted, longest streak, current streak
- Recent PRs and milestones
- Pinned workout templates ("Here's my current program — try it")
- Followers / following counts
- Activity feed (workouts posted, PRs hit, challenges joined)

Profile privacy: stats are public by default; individual workouts can be marked private per session.

### 5.2 Feed & Posts

A chronological (with optional algorithmic boost) feed showing:
- Completed workout posts — auto-generated from a finished session, editable before posting
- PR announcements — flagged automatically when a new personal record is logged
- Progress photo shares — opt-in per photo
- Challenge updates — milestone completions, leaderboard movements
- Program shares — "I just finished Week 4 of [Program Name]"

Post reactions: lift (equivalent of a like, but in context), fire, impressed.
Comments: threaded, text only in v1.

### 5.3 Following & Discovery

- Follow any public user
- Suggested follows: mutual followers, users in same challenges, users with similar training styles (AI-matched)
- Explore tab: trending workouts, top PRs this week, featured athlete programs, challenge leaderboards

### 5.4 Challenges

Challenges are structured competitions between groups of users over a defined time window. Types:

| Challenge Type | Description |
|---|---|
| **Consistency streak** | Hit X workouts per week for N weeks. Group streak: everyone must contribute. |
| **PR race** | First to hit a target weight on a given lift wins. |
| **Shared volume goal** | Group collectively lifts X kg in a month. |
| **1RM competition** | Highest tested 1RM on a given lift within the challenge window. |
| **Ranking / leaderboard** | Ongoing percentile rank on a chosen metric (volume, frequency, etc.) with weekly resets. |
| **Try my workout** | Creator posts a session template; participants complete it and log results. Top performers ranked. |

Challenge visibility: public (anyone can join) or private (invite-only for teams/friend groups).

### 5.5 Famous Athlete Programs

Curated, structured training programs inspired by or attributed to legendary athletes:
- Arnold Schwarzenegger's Golden Era split
- Ronnie Coleman's volume program
- Ed Coan's powerlifting periodization
- Rich Froning's CrossFit methodology
- (Expandable library, community-nominated)

These serve three purposes: inspiration for newer athletes, proven structure for intermediate athletes, and a social hook ("I'm running the Arnold program — who else is?").

Programs are available to all users. AI can adapt them to an individual's current training level.

---

## 6. AI Layer

The AI is GymChat's long-term moat. It is not a chatbot bolted onto a tracker. It is a coach that sees the complete athlete: their lifts, their runs, their food, their sleep, their body, their recovery. Over time, it becomes the most knowledgeable coach any user has ever had.

### 6.1 Cold Start Protocol

New users are not immediately bombarded with AI recommendations. The AI observes silently for approximately the first 3 workouts (configurable). During this window, GymChat is a clean, fast tracker — no suggestions, no analysis, no nudges.

After the cold start window, the AI begins generating its first insights. This moment is deliberate: the first time the AI says something, it should be specific, accurate, and useful — not generic boilerplate. Trust is built by being right, not by being present.

### 6.2 Proactive Insights (Weekly Reports)

Every week (Sunday or Monday, configurable), each user receives a generated analytics report. Delivered in-app and optionally via push notification / email.

Report contents:
- **Volume summary**: total sets, reps, and kg lifted by muscle group vs. prior week
- **Cardio summary**: total distance, duration, avg pace/HR
- **Nutrition summary**: avg daily calories and macros vs. targets; consistency %
- **Body trends**: weight change (7-day avg vs. prior week's avg)
- **Recovery snapshot**: avg HRV, avg sleep, avg resting HR vs. prior week
- **PR highlights**: any new personal records this week
- **AI commentary**: 2–4 bullet observations and 1–2 concrete recommendations for next week
- **Fatigute / readiness signal**: "Your HRV is down 15% and you've trained 6 days straight. Consider a rest or deload day."

### 6.3 Conversational Coach

A chat interface available at any time: during a workout, between workouts, on the dashboard.

**Mid-workout use cases:**
- "What weight should I open with for bench today?"
- "I'm feeling beat up — should I push through or cut the session?"
- "I have 20 minutes left, what should I prioritize?"

**Between-workout use cases:**
- "Design me a 12-week strength program for intermediate lifters"
- "I've been stuck at 100kg squat for 8 weeks — what's going wrong?"
- "How's my nutrition looking this week?"
- "Compare my progress this month to last month"
- "What do these HRV trends mean?"

The AI has full context: the user's entire training history, nutrition logs, body data, biometrics, and goals. Responses are grounded in the user's real data, not generic advice.

### 6.4 Program Design

The AI can generate a complete training program from a brief:
- Goal (strength, hypertrophy, endurance, fat loss, athletic performance)
- Days per week available
- Equipment access (full gym, home, bodyweight-only)
- Experience level
- Time per session
- Any movement restrictions or injuries

Output: a structured multi-week program (e.g., 4-day upper/lower, 12 weeks) with exercises, sets, rep ranges, and progression rules. Users can edit, override, or ask the AI to revise any element.

Programs can be saved as templates and shared publicly.

### 6.5 Real-Time Workout Coaching

During an active session, the AI operates with full awareness of the session so far:
- "Your RPE was 8.5 on that last set — last week this weight was a 7. Consider staying here or dropping 5% for the next set."
- "You've done 6 exercises. Based on your session history, you typically do 7–8 total exercises. You have time for 1–2 more."
- "Rest time is running long. Your recovery data looks good today — you might be ready sooner than you think."

Coaching frequency is configurable: silent, suggestive (one tip per exercise), or active (tip after every set).

### 6.6 AI Voice Configuration

Users configure the AI's personality to match their preference:
- **Tone**: Supportive / Neutral / Blunt
- **Style**: Concise (short bullets) / Conversational (natural language) / Detailed (explanations with data)
- **Directiveness**: Passive (here's the data, you decide) / Balanced / Directive (here's what you should do)

The default out-of-box experience is: Neutral, Conversational, Balanced.

### 6.7 The Data Moat

GymChat's AI improves as the network grows. Training data from across the platform (anonymized and aggregated) informs:
- Normative performance benchmarks ("You squat more than 73% of users your age and bodyweight")
- "Athletes like you" models — users with similar training history, body composition, and goals
- PR prediction ("Based on your 5-rep history, your estimated 1RM is X")
- Injury risk signals (pattern-matched from volume spikes in training histories that preceded user-reported injuries)

This proprietary structured dataset — sets, reps, RPE, RIR, rest, nutrition, biometrics, all linked and timestamped — is something no existing fitness app has at scale. It is a core component of the long-term competitive moat.

---

## 7. Monetization

### Free Tier

Core tracking is free, always. Removing the paywall from logging ensures the network grows and the data compounds.

Free includes:
- Strength training logging (unlimited sessions, all set fields)
- Cardio session logging (manual entry)
- Nutrition logging (calorie and macro tracking, food database access)
- Body weight and measurement tracking
- Social profile, feed, following, challenges
- Basic history and charts (last 30 days)
- 3 workouts of AI cold start observation (no AI output in free tier beyond this)

### Premium Tier

Premium is where the AI lives. Pricing TBD; target is competitive with MyFitnessPal Premium or Whoop membership.

Premium includes everything in Free, plus:
- Full AI coaching (conversational, proactive, real-time)
- Automated weekly analytics reports
- AI-generated training programs
- Advanced analytics (unlimited history, trend correlation, PR prediction, normative benchmarks)
- Wearable integrations (Whoop, Oura, Garmin, Apple Health deep sync)
- Progress photo storage and comparison
- Caloric periodization (AI-adjusted daily targets)
- Priority support

### Growth Flywheel

Social virality drives free tier growth → free users generate training data → data makes AI better → AI quality justifies premium conversion → premium revenue funds infrastructure → infrastructure scales the network.

The social layer is deliberately free because every post, challenge, and profile is a distribution channel.

---

## 8. Platform Strategy

### Now: Streamlit Prototype

The current Streamlit app is a learning vehicle and internal tool. It has been used to:
- Validate the core workout logging UX
- Build and test the database schema
- Explore session state patterns and component architecture
- Demonstrate the concept to early collaborators

Streamlit is **not** the production platform. It will not be shipped publicly.

### Next: Production Stack (TBD)

The production rebuild will target a mobile-first web app with native apps to follow. Stack decisions are pending and will be informed by the team's strengths and user research findings. Key requirements the stack must satisfy:

- Offline-capable (gym floors often have spotty connectivity)
- Sub-100ms input response for set logging (no user should wait after tapping "log set")
- Real-time UI updates (rest timer, live AI coaching) without full-page reruns
- Push notifications (weekly reports, challenge alerts, social interactions)
- Camera access (progress photos, barcode scan for food)
- GPS access (cardio session tracking)
- Background operation (rest timer continues when app is backgrounded)

The Streamlit prototype's database schema (`db/schema.sql`) and service layer logic are directly referenceable when designing the production data layer.

---

## 9. Data Model Vision

### Existing Tables

| Table | Purpose |
|---|---|
| `users` | Auth, profile, athlete metadata |
| `exercises` | Seeded exercise library (56 exercises, expandable) |
| `workout_sessions` | One row per gym visit |
| `exercise_executions` | One per exercise within a session |
| `sets` | One per logged set; weight, reps, RPE, RIR, rest |

### New Tables (production schema)

| Table | Purpose |
|---|---|
| `cardio_sessions` | One per cardio activity; duration, distance, modality, HR, pace |
| `cardio_laps` | Split data per lap within a cardio session |
| `nutrition_logs` | Daily nutrition summary per user per date |
| `meal_entries` | Individual food entries; meal type, food_item_id, quantity |
| `food_items` | Food database; calories, macros per 100g/unit |
| `body_measurements` | Weight, body fat %, measurements per date per user |
| `progress_photos` | Photo metadata (URL, date, category, visibility) |
| `wearable_syncs` | Raw biometric imports; HRV, sleep, resting HR, steps per day per device |
| `social_posts` | Posts to the feed; type (workout, PR, photo, challenge), linked entity |
| `follows` | Follower/following relationships |
| `workout_templates` | Saved and shareable session templates |
| `programs` | Multi-week training programs (sequence of templates) |
| `program_enrollments` | User-to-program assignments with current week/day |
| `challenges` | Challenge definitions; type, duration, target metric |
| `challenge_memberships` | User participation and score in each challenge |
| `ai_conversations` | Conversation history per user for the AI coach |
| `ai_messages` | Individual messages within a conversation |
| `weekly_reports` | Generated AI weekly report per user per week |

### Key Design Principles for the Schema

- Every event is timestamped and user-scoped — no anonymous aggregation without explicit opt-in
- Soft deletes preferred over hard deletes (keep historical data for AI training)
- RPE, RIR, notes fields are nullable — never required at the DB layer, even if encouraged at the UI layer
- Biometric data from wearables stores the raw value and the source device — never overwrite; append only

---

## 10. Design Principles

**Mobile-first, always.** The primary user is standing in a gym with one free hand. Every screen is designed for this context first. Desktop is a secondary concern.

**Input is sacred.** The act of logging must be fast, clear, and frictionless. Minimize taps. Pre-fill intelligently (last session's weights as starting point). Never make a user hunt for a field.

**Analytics must speak for themselves.** Charts and numbers should not require explanation. If a user needs to read a tooltip to understand what a chart means, the chart has failed.

**The AI earns its place.** No coaching before data. No generic advice. Every AI output should reference the user's actual training history. The AI should feel like a coach who has been watching every session, not a chatbot giving boilerplate.

**Social is motivation, not distraction.** The feed should inspire and connect, not hijack attention. No infinite scroll. No algorithmic rabbit holes. The social layer exists to make training more enjoyable and accountable — not to maximize time-on-app.

**Privacy by default.** Body measurements, weight, and progress photos are private unless the user explicitly shares them. The app never shares health data to the feed without clear user intent.

---

## 11. Current Prototype Status

### What Works

| Feature | Status |
|---|---|
| Authentication (scrypt) | Working |
| Exercise library (56 exercises) | Working |
| Workout session logging | Working |
| Set tracking (weight, reps, RPE, RIR, rest) | Working |
| Rest timer (fragment-based, live) | Working |
| Session history and per-exercise charts | Working |
| Dashboard with session stats | Working |
| User profile (athlete type, goals, metrics) | Working |
| Exercise picker with muscle group filter | Working |

### What Is Missing (vs. Vision)

| Domain | Status |
|---|---|
| Cardio tracking | Not started |
| Nutrition logging | Not started |
| Body composition tracking | Not started |
| Progress photos | Not started |
| Wearable integrations | Not started |
| Social profiles and feed | Not started |
| Challenges system | Not started |
| Workout templates and programs | Not started |
| AI coach (conversational) | Not started |
| AI weekly reports | Not started |
| Real-time AI coaching | Not started |
| Push notifications | Not started |

### Technical Debt to Resolve Before Production Rebuild

- `body_diagram.py`: unused module; evaluate for body composition page or remove
- `database.py` (root): legacy SHA-256 auth; do not extend; deprecate when Streamlit prototype is retired
- History page has inline raw SQL queries (violates the `pages → services → db` layering rule)
- `st.session_state` is the only in-memory persistence; cannot scale to multi-tab or background operations

---

## 12. Decisions Log

| Decision | What was decided | Rationale |
|---|---|---|
| Product scope | All-in-one super-app: strength, cardio, nutrition, body comp, wearables, social | Consolidation is the core investor thesis and user value prop |
| Target user | Any level of athlete, any fitness discipline | Network effects require breadth; AI improves with diverse data |
| Social model | Public profiles + private groups | Public = discovery and virality; private = trust and accountability |
| Monetization | Freemium — tracking free, AI behind paywall | Social virality drives free growth; AI value justifies premium |
| AI cold start | Silent for ~3 workouts, then first insights | Earn trust through data; avoid generic advice that damages credibility |
| AI voice | Configurable by user (tone, style, directiveness) | Athletes have different coaching preferences; one-size-fits-all fails |
| Platform | Streamlit prototype → full production rebuild | Streamlit is a learning vehicle; not suitable for production at scale |
| Phase 1 scope | User-research driven | Data from early users determines what matters most; avoid over-building |
| 12-month goal | 1,000 MAU with >50% 30-day retention | Retention is the leading indicator of product-market fit |
| Non-goals | None — all fitness domains are in scope | The consolidation pitch requires breadth; no intentional exclusions |
| Challenge types | 6 types including "try my workout" and famous athlete programs | User-generated and curated content both needed for community depth |
| AI interaction modes | Proactive (weekly reports) + conversational (anytime chat) | Both modes serve different user needs; neither alone is sufficient |
| Data privacy | Health data private by default, explicit opt-in to share | Trust is mandatory in health; users will not share sensitive data without clear control |
