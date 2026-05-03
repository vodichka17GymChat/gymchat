"""
Programs data access.

A program is an ordered list of workout templates that a user works
through in sequence, optionally cycling multiple times. Enrollments
track where in the sequence the user currently is.
"""

from datetime import datetime
from typing import Optional

from db.connection import get_connection


# ── Programs ────────────────────────────────────────────────────────────────

def create_program(
    user_id: int,
    name: str,
    description: Optional[str] = None,
    cycles: int = 1,
) -> int:
    """Insert a new program header. Returns the new program_id."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO programs (user_id, name, description, cycles, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, name, description, cycles, datetime.now().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def add_program_session(
    program_id: int,
    template_id: int,
    position: int,
) -> None:
    """Append one template slot to a program at the given position."""
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO program_sessions (program_id, template_id, position)
            VALUES (?, ?, ?)
            """,
            (program_id, template_id, position),
        )
        conn.commit()
    finally:
        conn.close()


def get_program(program_id: int):
    """Return a single program row, or None."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM programs WHERE program_id = ?",
            (program_id,),
        ).fetchone()
    finally:
        conn.close()


def get_programs_for_user(user_id: int):
    """Return all programs owned by the user, newest first."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM programs WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()


def get_program_sessions(program_id: int):
    """
    Return all session slots in a program in order, joined with their
    template name for display.
    """
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                ps.program_session_id,
                ps.position,
                ps.template_id,
                wt.name   AS template_name,
                wt.workout_type
            FROM program_sessions ps
            JOIN workout_templates wt ON ps.template_id = wt.template_id
            WHERE ps.program_id = ?
            ORDER BY ps.position
            """,
            (program_id,),
        ).fetchall()
    finally:
        conn.close()


def delete_program(program_id: int) -> None:
    """Delete a program and all its session slots (and any enrollments)."""
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM program_enrollments WHERE program_id = ?",
            (program_id,),
        )
        conn.execute(
            "DELETE FROM program_sessions WHERE program_id = ?",
            (program_id,),
        )
        conn.execute(
            "DELETE FROM programs WHERE program_id = ?",
            (program_id,),
        )
        conn.commit()
    finally:
        conn.close()


# ── Enrollments ─────────────────────────────────────────────────────────────

def enroll(user_id: int, program_id: int) -> int:
    """Create an active enrollment. Returns the new enrollment_id."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO program_enrollments
                (user_id, program_id, enrolled_at, next_position, current_cycle, status)
            VALUES (?, ?, ?, 1, 1, 'active')
            """,
            (user_id, program_id, datetime.now().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_active_enrollment(user_id: int):
    """Return the user's single active enrollment row, or None."""
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                pe.*,
                p.name      AS program_name,
                p.cycles    AS program_cycles
            FROM program_enrollments pe
            JOIN programs p ON pe.program_id = p.program_id
            WHERE pe.user_id = ? AND pe.status = 'active'
            ORDER BY pe.enrolled_at DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


def get_enrollments_for_user(user_id: int):
    """Return all enrollments for a user (any status), newest first."""
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                pe.*,
                p.name      AS program_name,
                p.cycles    AS program_cycles
            FROM program_enrollments pe
            JOIN programs p ON pe.program_id = p.program_id
            WHERE pe.user_id = ?
            ORDER BY pe.enrolled_at DESC
            """,
            (user_id,),
        ).fetchall()
    finally:
        conn.close()


def advance_enrollment(
    enrollment_id: int,
    next_position: int,
    current_cycle: int,
    status: str,
) -> None:
    """Update position/cycle/status after the user completes a session."""
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE program_enrollments
            SET next_position = ?, current_cycle = ?, status = ?
            WHERE enrollment_id = ?
            """,
            (next_position, current_cycle, status, enrollment_id),
        )
        conn.commit()
    finally:
        conn.close()


def unenroll(enrollment_id: int) -> None:
    """Mark an enrollment as paused (soft-delete keeps history)."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE program_enrollments SET status = 'paused' WHERE enrollment_id = ?",
            (enrollment_id,),
        )
        conn.commit()
    finally:
        conn.close()
