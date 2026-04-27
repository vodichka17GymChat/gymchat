"""
User table data access. Pure SQL only - hashing, validation, and business
rules belong in services/auth.py. Every function here returns either
sqlite3.Row objects (for reads) or primitive values (lastrowid for inserts).
"""

from datetime import datetime
from typing import Optional

from db.connection import get_connection


def create_user(
    email: str,
    password_hash: str,
    password_salt: str,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    training_experience_months: Optional[int] = None,
    fitness_level: Optional[str] = None,
    athlete_type: Optional[str] = None,
    primary_goal: Optional[str] = None,
) -> int:
    """
    Insert a new user. Returns the new user_id.
    Raises sqlite3.IntegrityError if the email is already taken.
    """
    now = datetime.now().isoformat()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO users (
                email, password_hash, password_salt,
                age, gender, height_cm, weight_kg,
                training_experience_months, fitness_level,
                athlete_type, primary_goal,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email, password_hash, password_salt,
                age, gender, height_cm, weight_kg,
                training_experience_months, fitness_level,
                athlete_type, primary_goal,
                now, now,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_by_email(email: str):
    """Return the user row matching this email, or None if not found."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    """Return the user row for this user_id, or None if not found."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


def update_user_profile(
    user_id: int,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    training_experience_months: Optional[int] = None,
    fitness_level: Optional[str] = None,
    athlete_type: Optional[str] = None,
    primary_goal: Optional[str] = None,
) -> None:
    """
    Update profile fields for an existing user. Only fields passed as
    non-None are updated; everything else is left alone. This lets the
    Profile page submit just the fields that changed.
    """
    fields = {
        "age": age,
        "gender": gender,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "training_experience_months": training_experience_months,
        "fitness_level": fitness_level,
        "athlete_type": athlete_type,
        "primary_goal": primary_goal,
    }
    # Drop fields the caller didn't pass
    updates = {k: v for k, v in fields.items() if v is not None}
    if not updates:
        return  # nothing to do

    set_clause = ", ".join(f"{col} = ?" for col in updates.keys())
    values = list(updates.values())
    values.append(datetime.now().isoformat())  # updated_at
    values.append(user_id)

    conn = get_connection()
    try:
        conn.execute(
            f"UPDATE users SET {set_clause}, updated_at = ? WHERE user_id = ?",
            values,
        )
        conn.commit()
    finally:
        conn.close()


def update_password(user_id: int, password_hash: str, password_salt: str) -> None:
    """Update password hash and salt. Used when a user changes their password."""
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE users
            SET password_hash = ?, password_salt = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (password_hash, password_salt, datetime.now().isoformat(), user_id),
        )
        conn.commit()
    finally:
        conn.close()