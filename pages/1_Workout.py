"""
Workout page - the main data-collection screen.

Two states:

  1. No active session - shows a 'Start a new workout' form.

  2. Active session - shows a single scrollable view containing:
       a) Session header card (type, duration, end button)
       b) Stack of exercise cards, one per exercise performed.
          The card the user is actively working in is expanded;
          others collapse to save vertical space.
       c) An 'Add exercise' section at the bottom.

The single-view design lets users scroll back to any earlier exercise
and add a forgotten set without losing context. That's a common gym
workflow that the old modal flow couldn't handle.

Database is the source of truth for what's active. We re-sync on every
page load so a user closing their browser mid-workout and coming back
later still finds their session intact.
"""

from datetime import datetime

import streamlit as st

import config
from components.exercise_card import render as render_exercise_card
from components.exercise_picker import render as render_exercise_picker
from components.theme import inject_theme
from services.workout import (
    WorkoutError,
    add_exercise,
    end_session,
    get_active_session,
    get_session_exercises,
    start_session,
)
from utils.datetime_helpers import format_duration

inject_theme()


# ============================================================
# Auth gate
# ============================================================

if st.session_state.get("user_id") is None:
    st.warning("Please log in from the home page first.")
    st.stop()

USER_ID = st.session_state.user_id


# ============================================================
# Sync session state with database
# ============================================================
# Always trust the database, never session state alone.

active = get_active_session(USER_ID)
st.session_state.active_session_id = active["session_id"] if active else None


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.write(f"Signed in as **{st.session_state.user_email}**")


# ============================================================
# Page header
# ============================================================

st.title("🏋️ Workout")


# ============================================================
# State 1: No active session - start a new workout
# ============================================================

def _render_start_form():
    """The 'begin a new workout' form, shown when no session is active."""
    with st.container(border=True):
        st.subheader("Start a new workout")

        workout_type = st.selectbox("Workout type", config.WORKOUT_TYPES)

        with st.expander("Optional details (location, sleep, energy)"):
            gym_location = st.text_input("Gym location")
            sleep_hours = st.number_input(
                "Sleep last night (hours)",
                min_value=0.0,
                max_value=14.0,
                value=0.0,
                step=0.5,
                help="Leave at 0 to skip.",
            )
            energy = st.slider(
                "Energy level right now",
                min_value=1,
                max_value=10,
                value=7,
                help="1 = exhausted, 10 = ready to go.",
            )

        if st.button("▶️ Begin workout", use_container_width=True, type="primary"):
            try:
                session_id = start_session(
                    user_id=USER_ID,
                    workout_type=workout_type,
                    gym_location=gym_location,
                    sleep_hours=sleep_hours if sleep_hours > 0 else None,
                    energy_pre_workout=energy,
                )
            except WorkoutError as e:
                st.error(str(e))
            else:
                st.session_state.active_session_id = session_id
                st.session_state.focused_execution_id = None
                st.rerun()


# ============================================================
# State 2: Active session - full session view
# ============================================================

def _render_session_header(active_session) -> None:
    """
    The card at the top of an active session: workout type, duration,
    location, and the End button.
    """
    started = datetime.fromisoformat(active_session["start_time"])
    duration_str = format_duration(
        active_session["start_time"],
        datetime.now().isoformat(),
    )

    with st.container(border=True):
        col_info, col_end = st.columns([4, 1])

        with col_info:
            title = active_session["workout_type"] or "Workout"
            details = [f"Started {started.strftime('%H:%M')}", f"{duration_str} elapsed"]
            if active_session["gym_location"]:
                details.append(f"📍 {active_session['gym_location']}")
            meta_str = " · ".join(details)

            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.25rem;">
                    <div class="gc-status-dot"></div>
                    <span style="font-weight:600;font-size:1.05rem;color:#1B2A41;
                                 font-family:'Inter',sans-serif;">{title}</span>
                </div>
                <div style="font-size:0.8rem;color:#6B7A90;font-family:'Inter',sans-serif;">
                    {meta_str}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_end:
            if st.button("End", use_container_width=True, key="end_workout_btn"):
                st.session_state.show_end_form = True
                st.rerun()


def _render_end_workout_form(session_id: int) -> None:
    """
    Confirmation block shown when the user clicks End. Asks for optional
    notes and provides cancel + confirm buttons.
    """
    with st.container(border=True):
        st.markdown("**End this workout?**")
        notes = st.text_area("Session notes (optional)", key="end_notes")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_end_form = False
                st.rerun()
        with col2:
            if st.button("Confirm end", use_container_width=True, type="primary"):
                try:
                    end_session(session_id, notes=notes)
                except WorkoutError as e:
                    st.error(str(e))
                else:
                    st.session_state.show_end_form = False
                    st.session_state.active_session_id = None
                    st.session_state.focused_execution_id = None
                    st.success("Workout ended. Nice work.")
                    st.rerun()


def _resolve_focused_execution(executions) -> int | None:
    """
    Decide which exercise card should be open by default.

    Rule: the card the user last logged a set in stays expanded
    (focused_execution_id is set by exercise_card after a successful
    log). If that's not set or no longer valid, default to the
    most-recently-added exercise.
    """
    if not executions:
        return None

    valid_ids = {ex["execution_id"] for ex in executions}
    focused = st.session_state.get("focused_execution_id")
    if focused in valid_ids:
        return focused

    return executions[-1]["execution_id"]


def _render_exercise_cards(executions, focused_id: int | None) -> None:
    """Render one card per exercise in the session, newest first."""
    st.markdown('<p class="gc-section-label">Exercises</p>', unsafe_allow_html=True)

    for ex in reversed(executions):
        render_exercise_card(
            execution_id=ex["execution_id"],
            user_id=USER_ID,
            expanded=(ex["execution_id"] == focused_id),
        )


def _render_add_exercise_section(session_id: int, has_existing: bool) -> None:
    """
    The 'Add exercise' block at the bottom of the page. Open by default
    when the session has no exercises yet; collapsed otherwise.
    """
    with st.expander("➕ Add exercise", expanded=not has_existing):
        selection = render_exercise_picker(key_prefix="add_ex")

        if selection is None:
            return

        if st.button(
            f"Add {selection['exercise_name']} to workout",
            use_container_width=True,
            type="primary",
        ):
            try:
                new_execution_id = add_exercise(
                    session_id=session_id,
                    exercise_id=selection["exercise_id"],
                    equipment_brand=selection["equipment_brand"],
                    equipment_model=selection["equipment_model"],
                )
            except WorkoutError as e:
                st.error(str(e))
            else:
                st.session_state.focused_execution_id = new_execution_id
                st.rerun()


# ============================================================
# Main
# ============================================================

if active is None:
    _render_start_form()
    st.stop()


session_id = active["session_id"]

_render_session_header(active)

if st.session_state.get("show_end_form"):
    _render_end_workout_form(session_id)

executions = get_session_exercises(session_id)

if executions:
    focused_id = _resolve_focused_execution(executions)
    _render_exercise_cards(executions, focused_id)
else:
    st.info("No exercises yet. Add your first one below.")

st.divider()
_render_add_exercise_section(session_id, has_existing=bool(executions))
