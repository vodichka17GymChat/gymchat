"""
Workout sessions and exercise executions data access.

A 'session' is one gym visit (start to end). An 'execution' is one
exercise performed during a session - e.g. Bench Press on a specific
piece of equipment. Sets attach to executions, not sessions directly.
"""

from datetime import datetime
from typing import Optional

from db.connection import get_connection


# ============================================================
# Sessions
# ============================================================

def create_session(
    user_id: int,
    workout_type: str,
    gym_location: Optional[str] = None,
    sleep_hours: Optional[float] = None,
    energy_pre_workout: Optional[int] = None,
) -> int:
    """
    Start a new workout session. Returns the new session_id.

    sleep_hours and energy_pre_workout are the wellness fields captured
    when the user begins the session - both optional so the user can
    skip them if they're in a rush.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO workout_sessions (
                user_id, workout_type, gym_location,
                sleep_hours, energy_pre_workout, start_time
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, workout_type, gym_location,
                sleep_hours, energy_pre_workout,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def end_session(session_id: int, notes: Optional[str] = None) -> None:
    """Mark a session as ended by setting end_time and saving notes."""
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE workout_sessions
            SET end_time = ?, notes = ?
            WHERE session_id = ?
            """,
            (datetime.now().isoformat(), notes, session_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_session(session_id: int):
    """Return one session row, or None if not found."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM workout_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    finally:
        conn.close()


def get_sessions_for_user(user_id: int, limit: Optional[int] = None):
    """
    Return all sessions for a user, newest first. Used by the History page.
    Pass limit=10 to get only the 10 most recent.
    """
    sql = """
        SELECT * FROM workout_sessions
        WHERE user_id = ?
        ORDER BY start_time DESC
    """
    params = [user_id]

    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def get_active_session_for_user(user_id: int):
    """
    Return the user's currently-active session (one with no end_time),
    or None if they don't have one. Used at login to detect 'you have
    a workout already in progress'.
    """
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT * FROM workout_sessions
            WHERE user_id = ? AND end_time IS NULL
            ORDER BY start_time DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


# ============================================================
# Exercise executions
# ============================================================

def add_execution(
    session_id: int,
    exercise_id: int,
    equipment_brand: Optional[str] = None,
    equipment_model: Optional[str] = None,
) -> int:
    """
    Add an exercise to a session. Returns the new execution_id.
    execution_order is auto-assigned based on how many exercises
    already exist in this session.
    """
    conn = get_connection()
    try:
        # Compute the next order value for this session
        existing = conn.execute(
            "SELECT COUNT(*) FROM exercise_executions WHERE session_id = ?",
            (session_id,),
        ).fetchone()[0]
        next_order = existing + 1

        cursor = conn.execute(
            """
            INSERT INTO exercise_executions (
                session_id, exercise_id, equipment_brand,
                equipment_model, execution_order
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, exercise_id, equipment_brand, equipment_model, next_order),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_execution_with_exercise(execution_id: int):
    """
    Return execution joined with its exercise details (name, muscle group,
    type). Used by the active workout page to display the current exercise.
    """
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                ex.execution_id,
                ex.session_id,
                ex.exercise_id,
                ex.equipment_brand,
                ex.equipment_model,
                ex.execution_order,
                e.exercise_name,
                e.muscle_group,
                e.exercise_type
            FROM exercise_executions ex
            JOIN exercises e ON ex.exercise_id = e.exercise_id
            WHERE ex.execution_id = ?
            """,
            (execution_id,),
        ).fetchone()
    finally:
        conn.close()


def get_executions_for_session(session_id: int):
    """
    Return all exercises performed in a session, in the order they were
    performed. Each row includes the exercise name. Used by the History
    page when expanding a session.
    """
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                ex.execution_id,
                ex.exercise_id,
                ex.equipment_brand,
                ex.equipment_model,
                ex.execution_order,
                e.exercise_name,
                e.muscle_group,
                e.exercise_type
            FROM exercise_executions ex
            JOIN exercises e ON ex.exercise_id = e.exercise_id
            WHERE ex.session_id = ?
            ORDER BY ex.execution_order
            """,
            (session_id,),
        ).fetchall()
    finally:
        conn.close()