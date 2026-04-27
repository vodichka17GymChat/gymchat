"""
Exercise table data access. The exercises table is seeded once from
seed_exercises.json and is read-only from the app's perspective.
"""

from typing import Optional

from db.connection import get_connection


def get_all_exercises():
    """Return every exercise, sorted by name. Used by the exercise picker."""
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT exercise_id, exercise_name, muscle_group, exercise_type
            FROM exercises
            ORDER BY exercise_name
            """
        ).fetchall()
    finally:
        conn.close()


def get_exercise_by_id(exercise_id: int):
    """Return one exercise row, or None if not found."""
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT exercise_id, exercise_name, muscle_group, exercise_type
            FROM exercises
            WHERE exercise_id = ?
            """,
            (exercise_id,),
        ).fetchone()
    finally:
        conn.close()


def get_muscle_groups() -> list[str]:
    """
    Return distinct muscle groups present in the exercises table.
    Used to populate the muscle-group filter in the exercise picker
    so the dropdown stays in sync with the seed data automatically.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT muscle_group FROM exercises ORDER BY muscle_group"
        ).fetchall()
        return [r["muscle_group"] for r in rows]
    finally:
        conn.close()


def search_exercises(
    muscle_group: Optional[str] = None,
    exercise_type: Optional[str] = None,
):
    """
    Return exercises matching the given filters. Pass None for either
    filter to skip it. Used by the exercise picker when the user selects
    a muscle group or exercise type from the dropdowns.
    """
    sql = """
        SELECT exercise_id, exercise_name, muscle_group, exercise_type
        FROM exercises
        WHERE 1=1
    """
    params = []

    if muscle_group:
        sql += " AND muscle_group = ?"
        params.append(muscle_group)

    if exercise_type:
        sql += " AND exercise_type = ?"
        params.append(exercise_type)

    sql += " ORDER BY exercise_name"

    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()