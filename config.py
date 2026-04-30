"""
GymChat configuration - paths, constants, and lookup values used across the app.
Edit values here rather than hardcoding them in pages or services.
"""

from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "gymchat_data.db"
SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"

# --- App metadata ---
APP_NAME = "GymChat"
APP_ICON = "💪"

# --- Lookup values for dropdowns and validation ---
GENDERS = ["Male", "Female", "Other"]

FITNESS_LEVELS = ["Beginner", "Intermediate", "Advanced", "Elite"]

ATHLETE_TYPES = [
    "Powerlifter",
    "Bodybuilder / Hypertrophy",
    "General strength",
    "CrossFit / Conditioning",
    "Endurance athlete",
    "General fitness",
]

PRIMARY_GOALS = [
    "Muscle Growth (Hypertrophy)",
    "Strength",
    "Endurance",
    "Weight Loss",
    "General Fitness",
]

WORKOUT_TYPES = ["Push", "Pull", "Legs", "Upper", "Lower", "Full Body", "Other"]

# --- Validation ranges ---
AGE_MIN, AGE_MAX = 13, 100
HEIGHT_CM_MIN, HEIGHT_CM_MAX = 100, 250
WEIGHT_KG_MIN, WEIGHT_KG_MAX = 30.0, 300.0
EXPERIENCE_MONTHS_MAX = 600

# Per-set input ranges
WEIGHT_INPUT_MIN, WEIGHT_INPUT_MAX = 0.0, 500.0
REPS_MIN, REPS_MAX = 1, 100
RPE_MIN, RPE_MAX = 1, 10
RIR_MIN, RIR_MAX = 0, 10
REST_SECONDS_MAX = 1200  # 20-minute cap on rest input

# --- Workout defaults ---
# Default rest target shown in the timer UI. The actual logged rest is
# always whatever we measured between sets - this is just the visual
# "you're aiming for" reference.
DEFAULT_REST_SECONDS = 90

# --- Profile completion ---
# A profile is considered "complete" when athlete_type is set. We picked
# this single field as the marker because (a) it's the most useful for
# future analytics/coaching, and (b) it's not a free-text field, so a
# user filling it in always means a deliberate choice.
PROFILE_COMPLETE_MARKER = "athlete_type"
