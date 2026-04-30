"""
History page - browse past workouts and see progression on key lifts.

Layout:
  - Summary stats (total sessions, total sets, last workout)
  - Recent sessions, each expandable to show exercises and sets
  - Progression chart for any chosen exercise
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from components.theme import inject_theme
from db import exercises as exercises_db
from db.connection import get_connection
from services.workout import (
    get_session_exercises,
    get_sets,
    get_user_sessions,
)
from utils.datetime_helpers import format_datetime, format_duration

inject_theme()


# ============================================================
# Auth gate
# ============================================================

if st.session_state.get("user_id") is None:
    st.warning("Please log in from the home page first.")
    st.stop()

USER_ID = st.session_state.user_id


with st.sidebar:
    st.write(f"Signed in as **{st.session_state.user_email}**")


# ============================================================
# Local helpers
# ============================================================

def _session_volume(session_id: int) -> float:
    """
    Total volume (sum of weight × reps across every set) for a session.
    Cheap aggregate query - much faster than loading every set into
    Python and summing there as the user accumulates years of data.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(s.weight_kg * s.reps), 0) AS volume
            FROM sets s
            JOIN exercise_executions ex ON s.execution_id = ex.execution_id
            WHERE ex.session_id = ?
            """,
            (session_id,),
        ).fetchone()
        return float(row["volume"])
    finally:
        conn.close()


def _exercise_history(user_id: int, exercise_id: int):
    """
    Pull every set the user has ever logged for one exercise, with the
    parent session's start time. Used to draw the progression chart.
    """
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                ws.start_time,
                s.weight_kg,
                s.reps,
                s.rpe,
                s.set_number
            FROM sets s
            JOIN exercise_executions ex ON s.execution_id = ex.execution_id
            JOIN workout_sessions ws ON ex.session_id = ws.session_id
            WHERE ws.user_id = ? AND ex.exercise_id = ?
            ORDER BY ws.start_time, s.set_number
            """,
            (user_id, exercise_id),
        ).fetchall()
    finally:
        conn.close()


def _workout_type_chip(workout_type: str | None) -> str:
    """Return an HTML chip for use inside expander bodies (not the label)."""
    label = workout_type or "Workout"
    return f'<span class="gc-chip gc-chip-blue">{label}</span>'


# ============================================================
# Page
# ============================================================

st.title("📊 History")

sessions = get_user_sessions(USER_ID)

if not sessions:
    st.info(
        "No workouts logged yet. Head to the Workout page to start "
        "your first session."
    )
    st.stop()


# ============================================================
# Summary stats
# ============================================================

st.markdown('<p class="gc-section-label">All time</p>', unsafe_allow_html=True)

total_sessions = len(sessions)

conn = get_connection()
try:
    total_sets = conn.execute(
        """
        SELECT COUNT(s.set_id)
        FROM sets s
        JOIN exercise_executions ex ON s.execution_id = ex.execution_id
        JOIN workout_sessions ws ON ex.session_id = ws.session_id
        WHERE ws.user_id = ?
        """,
        (USER_ID,),
    ).fetchone()[0]
finally:
    conn.close()

last_workout_str = format_datetime(sessions[0]["start_time"])

col1, col2, col3 = st.columns(3)
col1.metric("Total workouts", total_sessions)
col2.metric("Total sets logged", total_sets)
col3.metric("Last workout", last_workout_str)

st.divider()


# ============================================================
# Recent sessions list
# ============================================================

st.markdown('<p class="gc-section-label">Recent workouts</p>', unsafe_allow_html=True)

limit = st.session_state.get("history_limit", 10)
visible_sessions = sessions[:limit]

for session in visible_sessions:
    sid = session["session_id"]
    started_str = format_datetime(session["start_time"])
    duration_str = format_duration(session["start_time"], session["end_time"])
    workout_type = session["workout_type"] or "Workout"
    is_open = session["end_time"] is None

    status_suffix = "  🟢 *active*" if is_open else ""
    header = f"**{workout_type}**  ·  {started_str}  ·  {duration_str}{status_suffix}"

    with st.expander(header):
        # Chip inside the body where HTML renders correctly
        st.markdown(_workout_type_chip(session["workout_type"]), unsafe_allow_html=True)

        meta_cols = st.columns(4)

        location_value = session["gym_location"] or "—"
        meta_cols[0].caption(f"**Location**\n\n{location_value}")

        sleep_value = (
            f"{session['sleep_hours']}h"
            if session["sleep_hours"] is not None
            else "—"
        )
        meta_cols[1].caption(f"**Sleep**\n\n{sleep_value}")

        energy_value = (
            f"{session['energy_pre_workout']}/10"
            if session["energy_pre_workout"] is not None
            else "—"
        )
        meta_cols[2].caption(f"**Energy (pre)**\n\n{energy_value}")

        meta_cols[3].caption(f"**Volume**\n\n{_session_volume(sid):,.0f} kg")

        if session["notes"]:
            st.caption(f"**Notes:** {session['notes']}")

        executions = get_session_exercises(sid)
        if not executions:
            st.write("_No exercises logged in this session._")
            continue

        for ex in executions:
            ex_sets = get_sets(ex["execution_id"])

            equipment_parts = [
                p for p in (ex["equipment_brand"], ex["equipment_model"])
                if p
            ]
            equipment_suffix = (
                f"  ·  _{' '.join(equipment_parts)}_" if equipment_parts else ""
            )
            st.markdown(f"**{ex['exercise_name']}**{equipment_suffix}")

            if not ex_sets:
                st.caption("_No sets logged._")
                continue

            df = pd.DataFrame(
                [
                    {
                        "Set": s["set_number"],
                        "Weight (kg)": s["weight_kg"],
                        "Reps": s["reps"],
                        "RPE": s["rpe"] if s["rpe"] is not None else "—",
                        "RIR": s["rir"] if s["rir"] is not None else "—",
                        "Rest (s)": s["rest_seconds"] if s["rest_seconds"] is not None else "—",
                    }
                    for s in ex_sets
                ]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)


if limit < total_sessions:
    if st.button(f"Load more ({total_sessions - limit} remaining)"):
        st.session_state.history_limit = limit + 10
        st.rerun()


# ============================================================
# Exercise progression chart
# ============================================================

st.divider()

with st.container(border=True):
    st.markdown("### Exercise progression")

    all_exercises = exercises_db.get_all_exercises()
    exercise_options = {row["exercise_name"]: row["exercise_id"] for row in all_exercises}

    chosen_name = st.selectbox(
        "Pick an exercise to see your progression",
        list(exercise_options.keys()),
    )
    chosen_id = exercise_options[chosen_name]

    history = _exercise_history(USER_ID, chosen_id)

    if not history:
        st.info(f"You haven't logged any sets for **{chosen_name}** yet.")
    else:
        df = pd.DataFrame(
            [
                {
                    "date": datetime.fromisoformat(r["start_time"]).date(),
                    "weight_kg": r["weight_kg"],
                    "reps": r["reps"],
                    "rpe": r["rpe"],
                }
                for r in history
            ]
        )

        # Top set per session = max weight on that date.
        is_top_set = df.groupby("date")["weight_kg"].transform("max") == df["weight_kg"]
        top_sets = (
            df[is_top_set]
            .drop_duplicates(subset=["date"])
            .sort_values("date")
        )

        chart_df = top_sets[["date", "weight_kg"]].set_index("date")
        st.line_chart(chart_df, height=300)
        st.caption(
            f"Top set weight per session for {chosen_name}. "
            f"{len(history)} total sets across {len(top_sets)} sessions."
        )

        with st.expander("See all logged sets"):
            st.dataframe(
                df.rename(
                    columns={
                        "date": "Date",
                        "weight_kg": "Weight (kg)",
                        "reps": "Reps",
                        "rpe": "RPE",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
