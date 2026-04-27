"""
Sets data access. One row per logged set within an exercise execution.
This is the most granular data the app captures and the table that will
grow fastest, so queries here need to stay efficient.
"""

from datetime import datetime
from typing import Optional

from db.connection import get_connection


def add_set(
    execution_id: int,
    set_number: int,
    weight_kg: float,
    reps: int,
    rpe: Optional[int] = None,
    rir: Optional[int] = None,
    rest_seconds: Optional[int] = None,
) -> int:
    """
    Log a single set. Returns the new set_id.

    rest_seconds is the rest taken BEFORE this set (since the previous one).
    Optional - users can skip it if they don't track rest.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO sets (
                execution_id, set_number, timestamp,
                weight_kg, reps, rpe, rir, rest_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                execution_id,
                set_number,
                datetime.now().isoformat(),
                weight_kg,
                reps,
                rpe,
                rir,
                rest_seconds,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_sets_for_execution(execution_id: int):
    """
    Return all sets for one exercise execution, ordered by set number.
    Used by the active workout page to show 'previous sets' and by the
    history page when expanding an exercise.
    """
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                set_id, set_number, timestamp,
                weight_kg, reps, rpe, rir, rest_seconds
            FROM sets
            WHERE execution_id = ?
            ORDER BY set_number
            """,
            (execution_id,),
        ).fetchall()
    finally:
        conn.close()


def count_sets_for_execution(execution_id: int) -> int:
    """
    Return how many sets have been logged for this execution. Used to
    compute the next set_number without loading every set into memory.
    """
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM sets WHERE execution_id = ?",
            (execution_id,),
        ).fetchone()[0]
    finally:
        conn.close()


def delete_set(set_id: int) -> None:
    """
    Delete one set. Used when a user mis-logs a set and wants to remove
    it. The remaining sets keep their original set_number values
    (gap-tolerant) - we don't renumber, since timestamps preserve order.
    """
    conn = get_connection()
    try:
        conn.execute("DELETE FROM sets WHERE set_id = ?", (set_id,))
        conn.commit()
    finally:
        conn.close()


def get_last_set_for_user_and_exercise(user_id: int, exercise_id: int):
    """
    Return the most recent set the user logged for this specific exercise
    (across all sessions). Powers the 'last time you did Bench Press, you
    did 80kg x 8' hint that'll show up on the active workout page.
    Returns None if the user has never done this exercise before.
    """
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                s.set_id, s.set_number, s.timestamp,
                s.weight_kg, s.reps, s.rpe, s.rir, s.rest_seconds,
                ws.start_time AS session_start_time
            FROM sets s
            JOIN exercise_executions ex ON s.execution_id = ex.execution_id
            JOIN workout_sessions ws ON ex.session_id = ws.session_id
            WHERE ws.user_id = ? AND ex.exercise_id = ?
            ORDER BY s.timestamp DESC
            LIMIT 1
            """,
            (user_id, exercise_id),
        ).fetchone()
    finally:
        conn.close()