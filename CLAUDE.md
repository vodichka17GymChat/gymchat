# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
streamlit run app.py
```

The app runs at `http://localhost:8501`. The database (`gymchat_data.db`) is created automatically on first launch by `db/connection.py:init_db()` and seeded with exercises from `db/seed_exercises.json`.

To reinitialize the database from scratch, delete `gymchat_data.db` and restart the app.

To run a one-time schema migration (e.g., after pulling changes that alter the DB):
```bash
python fix_database.py
```

There is no test suite and no linter configuration.

## Architecture

GymChat is a Streamlit multi-page app. Streamlit reruns the entire page script on every user interaction, so session state (`st.session_state`) is the only persistent in-memory store between reruns.

### Layered structure

```
pages/ → services/ → db/
```

- **Pages** (`app.py`, `pages/`) own rendering and user interaction. They call services only — never `db/` directly (the History page has a few inline raw queries as an exception).
- **Services** (`services/auth.py`, `services/workout.py`, `services/dashboard.py`) own business rules and raise typed exceptions (`AuthError`, `WorkoutError`) that pages catch and display.
- **DB modules** (`db/users.py`, `db/workouts.py`, `db/sets.py`, `db/exercises.py`) are thin wrappers around raw SQL. `db/connection.py` provides `get_connection()` (returns `sqlite3.Row` rows, enforces foreign keys) and `init_db()`.

### Pages

| File | Route | Purpose |
|------|-------|---------|
| `app.py` | `/` | Login/register tabs when signed out; dashboard when signed in |
| `pages/1_Workout.py` | `/Workout` | Start/manage an active workout session |
| `pages/2_History.py` | `/History` | Browse past sessions; exercise progression chart |
| `pages/3_Profile.py` | `/Profile` | Edit user profile metrics |

Every page starts with an auth gate: `if st.session_state.get("user_id") is None: st.stop()`.

### Components

Reusable UI fragments live in `components/`. They are called by pages and take plain Python arguments — no Streamlit globals:

- `exercise_card.py` — one expanded/collapsed card per exercise in a session; contains set list, rest timer, and set logger
- `set_logger.py` — the form for logging one set (weight, reps, optional RPE/RIR/rest override)
- `rest_timer.py` — `@st.fragment(run_every=1.0)` live timer; auto-measures rest between sets
- `exercise_picker.py` — filterable exercise selector used when adding exercises to a workout

### Session state keys

| Key | Set by | Meaning |
|-----|--------|---------|
| `user_id` | `app.py` login/register | Authenticated user; `None` = logged out |
| `user_email` | `app.py` login/register | Display email |
| `active_session_id` | `1_Workout.py` | Current workout session; synced from DB on every page load |
| `focused_execution_id` | `exercise_card.py` | Which exercise card should render expanded |
| `show_end_form` | `1_Workout.py` | Toggle for the inline "end workout" confirmation |

### Database schema

Five tables: `users`, `exercises`, `workout_sessions`, `exercise_executions`, `sets`. Full DDL in `db/schema.sql`.

A workout session flow: `workout_sessions` (one per gym visit) → `exercise_executions` (one per exercise within a session) → `sets` (one per logged set). Volume is computed as `SUM(weight_kg * reps)`.

### Configuration

All app-wide constants live in `config.py`: paths, dropdown options, validation ranges, and `PROFILE_COMPLETE_MARKER = "athlete_type"` (the single field used to decide if a profile is complete).

### Authentication

`services/auth.py` uses scrypt (OWASP-recommended parameters). The old `database.py` at the root uses plain SHA-256 — it is legacy/unused and should not be modified or extended.

### Design constraints

- Layout is `centered` (not `wide`). The primary user is on a mobile phone in the gym.
- `@st.fragment` is used in `rest_timer.py` to tick every second without triggering a full-page rerun.
- Widgets inside `st.form` cannot react to sibling widget changes mid-form; checkbox state is consulted at submit time instead.
