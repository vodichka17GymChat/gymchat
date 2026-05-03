-- GymChat database schema
-- All CREATE statements use IF NOT EXISTS so this file is safe to re-run.

-- ============================================================
-- Users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    email                       TEXT UNIQUE NOT NULL,
    password_hash               TEXT NOT NULL,
    password_salt               TEXT NOT NULL,
    age                         INTEGER,
    gender                      TEXT,
    height_cm                   REAL,
    weight_kg                   REAL,
    training_experience_months  INTEGER,
    fitness_level               TEXT,
    athlete_type                TEXT,
    primary_goal                TEXT,
    created_at                  TEXT NOT NULL,
    updated_at                  TEXT
);

-- ============================================================
-- Exercises (seeded once at startup from a JSON file)
-- ============================================================
CREATE TABLE IF NOT EXISTS exercises (
    exercise_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_name   TEXT UNIQUE NOT NULL,
    muscle_group    TEXT NOT NULL,
    exercise_type   TEXT NOT NULL  -- 'compound' or 'isolation'
);

-- ============================================================
-- Workout sessions (one per gym visit)
-- ============================================================
CREATE TABLE IF NOT EXISTS workout_sessions (
    session_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL,
    workout_type            TEXT,
    gym_location            TEXT,
    sleep_hours             REAL,           -- hours slept previous night
    energy_pre_workout      INTEGER,        -- 1-10 scale, asked at session start
    start_time              TEXT NOT NULL,
    end_time                TEXT,
    notes                   TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ============================================================
-- Exercise executions (one per exercise within a session)
-- ============================================================
CREATE TABLE IF NOT EXISTS exercise_executions (
    execution_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id          INTEGER NOT NULL,
    exercise_id         INTEGER NOT NULL,
    equipment_brand     TEXT,
    equipment_model     TEXT,
    execution_order     INTEGER,            -- 1, 2, 3... order within session
    FOREIGN KEY (session_id) REFERENCES workout_sessions(session_id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
);

-- ============================================================
-- Sets (one per logged set)
-- ============================================================
CREATE TABLE IF NOT EXISTS sets (
    set_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id    INTEGER NOT NULL,
    set_number      INTEGER NOT NULL,
    timestamp       TEXT NOT NULL,
    weight_kg       REAL NOT NULL,
    reps            INTEGER NOT NULL,
    rpe             INTEGER,                -- 1-10, optional
    rir             INTEGER,                -- reps in reserve, optional
    rest_seconds    INTEGER,                -- rest BEFORE this set
    FOREIGN KEY (execution_id) REFERENCES exercise_executions(execution_id)
);

-- ============================================================
-- Workout templates (saved sessions the user can relaunch)
-- ============================================================
CREATE TABLE IF NOT EXISTS workout_templates (
    template_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    name            TEXT NOT NULL,
    workout_type    TEXT,
    created_at      TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ============================================================
-- Template exercises (ordered list of exercises in a template)
-- ============================================================
CREATE TABLE IF NOT EXISTS template_exercises (
    template_exercise_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id             INTEGER NOT NULL,
    exercise_id             INTEGER NOT NULL,
    equipment_brand         TEXT,
    equipment_model         TEXT,
    exercise_order          INTEGER NOT NULL,
    FOREIGN KEY (template_id) REFERENCES workout_templates(template_id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
);

-- ============================================================
-- Programs (ordered sequences of templates)
-- ============================================================
CREATE TABLE IF NOT EXISTS programs (
    program_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    name            TEXT NOT NULL,
    description     TEXT,
    cycles          INTEGER NOT NULL DEFAULT 1,  -- times to repeat the session sequence
    created_at      TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ============================================================
-- Program sessions (ordered slots within a program)
-- ============================================================
CREATE TABLE IF NOT EXISTS program_sessions (
    program_session_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id          INTEGER NOT NULL,
    position            INTEGER NOT NULL,   -- 1-based; order to perform the templates
    template_id         INTEGER NOT NULL,
    FOREIGN KEY (program_id) REFERENCES programs(program_id),
    FOREIGN KEY (template_id) REFERENCES workout_templates(template_id)
);

-- ============================================================
-- Program enrollments (one active enrollment per user at a time)
-- ============================================================
CREATE TABLE IF NOT EXISTS program_enrollments (
    enrollment_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    program_id          INTEGER NOT NULL,
    enrolled_at         TEXT NOT NULL,
    next_position       INTEGER NOT NULL DEFAULT 1,  -- position within the sequence
    current_cycle       INTEGER NOT NULL DEFAULT 1,  -- which repeat of the sequence
    status              TEXT NOT NULL DEFAULT 'active',  -- 'active'|'completed'|'paused'
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
);

-- ============================================================
-- Indexes for query performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_sessions_user        ON workout_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time  ON workout_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_executions_session   ON exercise_executions(session_id);
CREATE INDEX IF NOT EXISTS idx_executions_exercise  ON exercise_executions(exercise_id);
CREATE INDEX IF NOT EXISTS idx_sets_execution       ON sets(execution_id);
CREATE INDEX IF NOT EXISTS idx_templates_user       ON workout_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_template_exercises   ON template_exercises(template_id);
CREATE INDEX IF NOT EXISTS idx_programs_user        ON programs(user_id);
CREATE INDEX IF NOT EXISTS idx_program_sessions     ON program_sessions(program_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_user     ON program_enrollments(user_id);