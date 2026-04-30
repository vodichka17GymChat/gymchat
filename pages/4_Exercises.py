"""
Exercise Library page - browse all available exercises with filtering.

Layout:
  - Filter controls (search, muscle group, exercise type)
  - Summary count
  - Exercises grouped by muscle group (or flat list when filtered)
  - Per-exercise: how many sessions the current user has logged it
"""

import streamlit as st

from db import exercises as exercises_db
from db.connection import get_connection


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

_TYPE_LABELS = {
    "compound": "Compound",
    "isolation": "Isolation",
}

_MUSCLE_EMOJI = {
    "back": "🔙",
    "biceps": "💪",
    "calves": "🦵",
    "chest": "🫁",
    "core": "⬜",
    "glutes": "🍑",
    "hamstrings": "🦵",
    "quads": "🦵",
    "shoulders": "🏋️",
    "triceps": "💪",
}


def _user_exercise_counts(user_id: int) -> dict[int, int]:
    """Return a mapping of exercise_id -> number of sessions logged for this user."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT ex.exercise_id, COUNT(DISTINCT ex.session_id) AS session_count
            FROM exercise_executions ex
            JOIN workout_sessions ws ON ex.session_id = ws.session_id
            WHERE ws.user_id = ?
            GROUP BY ex.exercise_id
            """,
            (user_id,),
        ).fetchall()
        return {r["exercise_id"]: r["session_count"] for r in rows}
    finally:
        conn.close()


# ============================================================
# Page
# ============================================================

st.title("📚 Exercise Library")

# --- Filter controls ---
col_search, col_group, col_type = st.columns([2, 1, 1])

with col_search:
    search_query = st.text_input("Search", placeholder="e.g. bench press…", label_visibility="collapsed")

muscle_groups = exercises_db.get_muscle_groups()
with col_group:
    selected_group = st.selectbox(
        "Muscle group",
        ["All"] + [g.title() for g in muscle_groups],
        label_visibility="collapsed",
    )

with col_type:
    selected_type = st.selectbox(
        "Type",
        ["All types", "Compound", "Isolation"],
        label_visibility="collapsed",
    )

# Resolve filter values for the db call
group_filter = None if selected_group == "All" else selected_group.lower()
type_filter = None if selected_type == "All types" else selected_type.lower()

exercises = exercises_db.search_exercises(
    muscle_group=group_filter,
    exercise_type=type_filter,
)

# Apply text search client-side (small dataset, fine to filter in Python)
if search_query.strip():
    q = search_query.strip().lower()
    exercises = [e for e in exercises if q in e["exercise_name"].lower()]

# ============================================================
# Fetch per-exercise user stats
# ============================================================

usage_counts = _user_exercise_counts(USER_ID)

# ============================================================
# Summary bar
# ============================================================

st.caption(f"{len(exercises)} exercise{'s' if len(exercises) != 1 else ''} found")

if not exercises:
    st.info("No exercises match your filters.")
    st.stop()

st.divider()

# ============================================================
# Exercise display
# ============================================================
# Group by muscle group when no specific group is selected;
# otherwise show a flat list under a single header.
# ============================================================

def _render_exercises(rows):
    """Render a list of exercise rows in a 3-column grid."""
    cols = st.columns(3)
    for i, ex in enumerate(rows):
        col = cols[i % 3]
        ex_id = ex["exercise_id"]
        ex_name = ex["exercise_name"]
        ex_type = ex["exercise_type"]
        muscle = ex["muscle_group"]

        type_badge = "🔵 Compound" if ex_type == "compound" else "🟠 Isolation"
        sessions_logged = usage_counts.get(ex_id, 0)
        sessions_text = f"✅ {sessions_logged} session{'s' if sessions_logged != 1 else ''}" if sessions_logged else "Not yet logged"

        with col:
            with st.container(border=True):
                st.markdown(f"**{ex_name}**")
                st.caption(f"{type_badge}  ·  {sessions_text}")


is_filtered = group_filter is not None or type_filter is not None or search_query.strip()

if is_filtered:
    # Flat list — label comes from the active filter
    if group_filter:
        emoji = _MUSCLE_EMOJI.get(group_filter, "")
        st.subheader(f"{emoji} {group_filter.title()}".strip())
    _render_exercises(exercises)
else:
    # Group by muscle group, in the order they appear in the seed data
    groups_seen: list[str] = []
    by_group: dict[str, list] = {}
    for ex in exercises:
        g = ex["muscle_group"]
        if g not in by_group:
            by_group[g] = []
            groups_seen.append(g)
        by_group[g].append(ex)

    for group in groups_seen:
        emoji = _MUSCLE_EMOJI.get(group, "")
        st.subheader(f"{emoji} {group.title()}".strip())
        _render_exercises(by_group[group])
        st.write("")
