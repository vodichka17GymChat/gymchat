"""
History page - browse past workouts and see progression on key lifts.

Layout:
  - Summary stats (total sessions, total sets, last workout)
  - Recent sessions, each expandable to show the exercises and sets
  - Progress chart for any exercise the user selects
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from db import exercises as exercises_db
from db.connection import get_connection
from services.workout import (
    get_session_exercises,
    get_sets,
    get_user_sessions,
)


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
# Helpers
# ============================================================

def _format_datetime(iso_string: str | None) -> str:
    """Turn an ISO timestamp into a friendly 'Apr 27, 2026 · 18:42'."""
    if not iso_string:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%b %d, %Y · %H:%M")
    except ValueError:
        return iso_string


def _session_duration(start: str | None, end: str | None) -> str:
    """Compute session duration as 'Xh Ym' or '—' if not endable."""
    if not start or not end:
        return "—"
    try:
        delta = datetime.fromisoformat(end) - datetime.fromisoformat(start)
        total_minutes = int(delta.total_seconds() // 60)
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"
    except ValueError:
        return "—"


def _session_volume(session_id: int) -> float:
    """
    Total volume (sum of weight × reps across all sets) for a session.
    A simple but meaningful summary metric.
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
    session start time. Used to draw the progression chart.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
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
        return rows
    finally:
        conn.close()


# ============================================================
# Page
# ============================================================

st.title("📊 History")

sessions = get_user_sessions(USER_ID)

if not sessions:
    st.info("No workouts logged yet. Head to the Workout page to start your first session.")
    st.stop()


# --- Summary stats ---
total_sessions = len(sessions)
completed_sessions = [s for s in sessions if s["end_time"] is not None]

total_sets = 0
for s in sessions:
    for ex in get_session_exercises(s["session_id"]):
        total_sets += len(get_sets(ex["execution_id"]))

last_workout = _format_datetime(sessions[0]["start_time"])

col1, col2, col3 = st.columns(3)
col1.metric("Total workouts", total_sessions)
col2.metric("Total sets logged", total_sets)
col3.metric("Last workout", last_workout)

st.divider()


# ============================================================
# Recent sessions list
# ============================================================

st.subheader("Recent workouts")

# Show 10 by default, with a button to load more
limit = st.session_state.get("history_limit", 10)
visible = sessions[:limit]

for session in visible:
    sid = session["session_id"]
    started = _format_datetime(session["start_time"])
    duration = _session_duration(session["start_time"], session["end_time"])
    workout_type = session["workout_type"] or "—"
    is_open = session["end_time"] is None

    header = f"**{workout_type}** · {started} · {duration}"
    if is_open:
        header += "  🟢 *in progress*"

    with st.expander(header):
        # Session-level metadata
        meta_cols = st.columns(4)
        meta_cols[0].caption(f"**Location**\n\n{session['gym_location'] or '—'}")
        meta_cols[1].caption(
            f"**Sleep**\n\n"
            f"{session['sleep_hours']}h" if session["sleep_hours"] is not None else "**Sleep**\n\n—"
        )
        meta_cols[2].caption(
            f"**Energy (pre)**\n\n"
            f"{session['energy_pre_workout']}/10" if session["energy_pre_workout"] is not None else "**Energy (pre)**\n\n—"
        )
        meta_cols[3].caption(f"**Volume**\n\n{_session_volume(sid):.0f} kg")

        if session["notes"]:
            st.caption(f"**Notes:** {session['notes']}")

        # Exercises performed
        executions = get_session_exercises(sid)
        if not executions:
            st.write("_No exercises logged in this session._")
            continue

        for ex in executions:
            ex_sets = get_sets(ex["execution_id"])
            equipment = ""
            if ex["equipment_brand"] or ex["equipment_model"]:
                parts = [p for p in (ex["equipment_brand"], ex["equipment_model"]) if p]
                equipment = f"  ·  _{' '.join(parts)}_"

            st.markdown(f"**{ex['exercise_name']}**{equipment}")

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


# Load more button
if limit < total_sessions:
    if st.button(f"Load more ({total_sessions - limit} remaining)"):
        st.session_state.history_limit = limit + 10
        st.rerun()


# ============================================================
# Exercise progression chart
# ============================================================

st.divider()
st.subheader("Exercise progression")

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
    # Build a dataframe with one row per logged set. We'll plot the top
    # set (heaviest weight) per session as the progression line.
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

    # Top set per session = max weight on that date
    top_sets = (
        df.groupby("date")
        .apply(lambda g: g.loc[g["weight_kg"].idxmax()])
        .reset_index(drop=True)
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