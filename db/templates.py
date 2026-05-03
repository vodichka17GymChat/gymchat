"""
Workout templates data access.

A template is a named, reusable exercise list. It stores which exercises
to perform (with optional equipment info) but not sets or weights — those
come from the user's last performance when the template is launched.
"""

from datetime import datetime
from typing import Optional

from db.connection import get_connection


def create_template(
    user_id: int,
    name: str,
    workout_type: Optional[str] = None,
) -> int:
    """Insert a new template header. Returns the new template_id."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO workout_templates (user_id, name, workout_type, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, name, workout_type, datetime.now().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def add_template_exercise(
    template_id: int,
    exercise_id: int,
    exercise_order: int,
    equipment_brand: Optional[str] = None,
    equipment_model: Optional[str] = None,
) -> None:
    """Append one exercise to a template."""
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO template_exercises (
                template_id, exercise_id, equipment_brand,
                equipment_model, exercise_order
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (template_id, exercise_id, equipment_brand, equipment_model, exercise_order),
        )
        conn.commit()
    finally:
        conn.close()


def get_templates_for_user(user_id: int):
    """Return all templates owned by the user, newest first."""
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT * FROM workout_templates
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
    finally:
        conn.close()


def get_template(template_id: int):
    """Return a single template row, or None."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM workout_templates WHERE template_id = ?",
            (template_id,),
        ).fetchone()
    finally:
        conn.close()


def get_template_exercises(template_id: int):
    """
    Return all exercises in a template in order, joined with exercise details.
    """
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                te.template_exercise_id,
                te.exercise_order,
                te.equipment_brand,
                te.equipment_model,
                e.exercise_id,
                e.exercise_name,
                e.muscle_group,
                e.exercise_type
            FROM template_exercises te
            JOIN exercises e ON te.exercise_id = e.exercise_id
            WHERE te.template_id = ?
            ORDER BY te.exercise_order
            """,
            (template_id,),
        ).fetchall()
    finally:
        conn.close()


def delete_template(template_id: int) -> None:
    """Delete a template and all its exercises (cascade via app logic)."""
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM template_exercises WHERE template_id = ?",
            (template_id,),
        )
        conn.execute(
            "DELETE FROM workout_templates WHERE template_id = ?",
            (template_id,),
        )
        conn.commit()
    finally:
        conn.close()
