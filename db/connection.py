"""
Database connection helper. Provides a single get_connection() function
that the rest of the app uses, plus first-run initialization that creates
the schema and seeds the exercises table.
"""

import json
import sqlite3
from pathlib import Path

import config


# Path to the seed data sits next to this file
SEED_EXERCISES_PATH = Path(__file__).parent / "seed_exercises.json"


def get_connection() -> sqlite3.Connection:
    """
    Open a SQLite connection to the GymChat database.

    Returns rows as sqlite3.Row objects so callers can access columns by
    name (row['user_id']) instead of by position (row[0]).
    """
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enforce foreign keys (off by default in SQLite)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """
    Run the schema file and seed the exercises table on first launch.
    Safe to call repeatedly: schema uses CREATE TABLE IF NOT EXISTS,
    and seeding only happens when the exercises table is empty.
    """
    # 1. Create tables
    schema_sql = config.SCHEMA_PATH.read_text(encoding="utf-8")
    conn = get_connection()
    try:
        conn.executescript(schema_sql)
        conn.commit()

        # 2. Seed exercises if table is empty
        count = conn.execute("SELECT COUNT(*) FROM exercises").fetchone()[0]
        if count == 0:
            _seed_exercises(conn)
            conn.commit()
    finally:
        conn.close()


def _seed_exercises(conn: sqlite3.Connection) -> None:
    """Load exercises from JSON and insert them into the exercises table."""
    with open(SEED_EXERCISES_PATH, encoding="utf-8") as f:
        exercises = json.load(f)

    rows = [(e["name"], e["muscle_group"], e["type"]) for e in exercises]
    conn.executemany(
        "INSERT INTO exercises (exercise_name, muscle_group, exercise_type) "
        "VALUES (?, ?, ?)",
        rows,
    )
    print(f"Seeded {len(rows)} exercises.")


# Allow running this file directly to (re)initialize the database from the
# command line: `python -m db.connection`
if __name__ == "__main__":
    init_db()
    print(f"Database ready at: {config.DB_PATH}")