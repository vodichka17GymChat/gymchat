"""
Dashboard service. Aggregates the stats shown on the home page.

The page itself just calls get_dashboard_summary() and renders the
result - all the SQL lives here. As the user base grows and these
queries need optimization (caching, materialized views, etc.), this
is the one file that needs to change.
"""

from datetime import datetime, timedelta
from typing import Optional

from db.connection import get_connection


def get_dashboard_summary(user_id: int) -> dict:
    """
    Return everything the home dashboard needs in a single dict.

    Shape:
        {
            "weekly_workouts": int,
            "weekly_sets": int,
            "weekly_volume": float,        # kg lifted (sum of weight × reps)
            "total_workouts": int,
            "last_workout": dict | None,   # see _build_last_workout below
        }

    All numbers are scoped to the given user_id. "Weekly" means the
    last 7 days from now, not the calendar week - that's more useful
    for someone training on a 7-day rolling cycle.
    """
    week_ago_iso = (datetime.now() - timedelta(days=7)).isoformat()

    conn = get_connection()
    try:
        weekly_workouts = conn.execute(
            """
            SELECT COUNT(*) FROM workout_sessions
            WHERE user_id = ? AND start_time >= ?
            """,
            (user_id, week_ago_iso),
        ).fetchone()[0]

        weekly_stats = conn.execute(
            """
            SELECT
                COUNT(s.set_id) AS set_count,
                COALESCE(SUM(s.weight_kg * s.reps), 0) AS volume
            FROM sets s
            JOIN exercise_executions ex ON s.execution_id = ex.execution_id
            JOIN workout_sessions ws ON ex.session_id = ws.session_id
            WHERE ws.user_id = ? AND ws.start_time >= ?
            """,
            (user_id, week_ago_iso),
        ).fetchone()

        total_workouts = conn.execute(
            "SELECT COUNT(*) FROM workout_sessions WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]

        last_workout = _build_last_workout(conn, user_id)

        return {
            "weekly_workouts": weekly_workouts,
            "weekly_sets": weekly_stats["set_count"],
            "weekly_volume": float(weekly_stats["volume"]),
            "total_workouts": total_workouts,
            "last_workout": last_workout,
        }
    finally:
        conn.close()


def _build_last_workout(conn, user_id: int) -> Optional[dict]:
    """
    Return a summary of the user's most recent COMPLETED workout, or
    None if they've never finished one. We deliberately exclude the
    in-progress session here - that's surfaced as a separate "resume"
    banner on the dashboard, with different framing.
    """
    last_session = conn.execute(
        """
        SELECT session_id, workout_type, start_time, end_time
        FROM workout_sessions
        WHERE user_id = ? AND end_time IS NOT NULL
        ORDER BY start_time DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()

    if last_session is None:
        return None

    sid = last_session["session_id"]

    exercise_count = conn.execute(
        "SELECT COUNT(*) FROM exercise_executions WHERE session_id = ?",
        (sid,),
    ).fetchone()[0]

    set_stats = conn.execute(
        """
        SELECT
            COUNT(s.set_id) AS set_count,
            COALESCE(SUM(s.weight_kg * s.reps), 0) AS volume
        FROM sets s
        JOIN exercise_executions ex ON s.execution_id = ex.execution_id
        WHERE ex.session_id = ?
        """,
        (sid,),
    ).fetchone()

    return {
        "session_id": sid,
        "workout_type": last_session["workout_type"],
        "start_time": last_session["start_time"],
        "end_time": last_session["end_time"],
        "exercise_count": exercise_count,
        "set_count": set_stats["set_count"],
        "volume": float(set_stats["volume"]),
    }
