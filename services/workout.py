"""
Workout service. Owns the rules of the workout flow on top of
db/workouts.py and db/sets.py. Pages call this module instead of
talking to the db modules directly.

Rules enforced here:
- A user can have at most one active session at a time.
- You can't add exercises or log sets to a session that has ended.
- Set numbers within an execution always go up - no duplicates,
  no reordering when a set is deleted.
"""

from typing import Optional

from db import sets as sets_db
from db import workouts as workouts_db


class WorkoutError(Exception):
    """Raised when a workout operation violates a business rule."""
    pass


# ============================================================
# Session lifecycle
# ============================================================

def start_session(
    user_id: int,
    workout_type: str,
    gym_location: Optional[str] = None,
    sleep_hours: Optional[float] = None,
    energy_pre_workout: Optional[int] = None,
) -> int:
    """
    Begin a new workout session. Returns the new session_id.
    Raises WorkoutError if the user already has an active session.
    """
    existing = workouts_db.get_active_session_for_user(user_id)
    if existing is not None:
        raise WorkoutError(
            "You already have an active workout. End it before starting a new one."
        )

    return workouts_db.create_session(
        user_id=user_id,
        workout_type=workout_type,
        gym_location=gym_location or None,
        sleep_hours=sleep_hours,
        energy_pre_workout=energy_pre_workout,
    )


def end_session(session_id: int, notes: Optional[str] = None) -> None:
    """
    End an active session. Raises WorkoutError if the session doesn't
    exist or has already been ended.
    """
    session = workouts_db.get_session(session_id)
    if session is None:
        raise WorkoutError("Session not found.")
    if session["end_time"] is not None:
        raise WorkoutError("This workout has already been ended.")

    workouts_db.end_session(session_id, notes=notes or None)


def get_active_session(user_id: int):
    """Return the user's active session row, or None."""
    return workouts_db.get_active_session_for_user(user_id)


def get_user_sessions(user_id: int, limit: Optional[int] = None):
    """Return the user's past sessions, newest first. Used by the History page."""
    return workouts_db.get_sessions_for_user(user_id, limit=limit)


# ============================================================
# Exercises within a session
# ============================================================

def add_exercise(
    session_id: int,
    exercise_id: int,
    equipment_brand: Optional[str] = None,
    equipment_model: Optional[str] = None,
) -> int:
    """
    Add an exercise to an active session. Returns the new execution_id.
    Raises WorkoutError if the session doesn't exist or is already ended.
    """
    session = workouts_db.get_session(session_id)
    if session is None:
        raise WorkoutError("Session not found.")
    if session["end_time"] is not None:
        raise WorkoutError("Cannot add exercises to a workout that has ended.")

    return workouts_db.add_execution(
        session_id=session_id,
        exercise_id=exercise_id,
        equipment_brand=equipment_brand or None,
        equipment_model=equipment_model or None,
    )


def get_execution_details(execution_id: int):
    """
    Return execution row joined with its exercise (name, muscle_group, type).
    Used by the active workout page to display the current exercise.
    """
    return workouts_db.get_execution_with_exercise(execution_id)


def get_session_exercises(session_id: int):
    """
    Return all executions in a session in performed order, each with
    its exercise details. Used by the History page.
    """
    return workouts_db.get_executions_for_session(session_id)


# ============================================================
# Set logging
# ============================================================

def log_set(
    execution_id: int,
    weight_kg: float,
    reps: int,
    rpe: Optional[int] = None,
    rir: Optional[int] = None,
    rest_seconds: Optional[int] = None,
) -> int:
    """
    Log a set for the given execution. Set number is auto-assigned as
    one more than the highest existing set number for this execution,
    so deleting a set in the middle won't cause a future collision.
    Returns the new set_id.
    """
    existing = sets_db.get_sets_for_execution(execution_id)
    next_set_number = max((s["set_number"] for s in existing), default=0) + 1

    return sets_db.add_set(
        execution_id=execution_id,
        set_number=next_set_number,
        weight_kg=weight_kg,
        reps=reps,
        rpe=rpe,
        rir=rir,
        rest_seconds=rest_seconds,
    )


def get_sets(execution_id: int):
    """Return all logged sets for this execution, ordered by set number."""
    return sets_db.get_sets_for_execution(execution_id)


def remove_set(set_id: int) -> None:
    """Delete a set. Used when a user mis-logs and wants to undo."""
    sets_db.delete_set(set_id)


def get_last_performance(user_id: int, exercise_id: int):
    """
    Return the user's most recent set for this exercise across all
    sessions, or None if they've never done it. Used by the active
    workout page to show 'last time: 80kg x 8'.
    """
    return sets_db.get_last_set_for_user_and_exercise(user_id, exercise_id)