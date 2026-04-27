"""
Workout page - the main data-collection screen.

Three states based on session state:
  1. No active session         -> show 'Start workout' form
  2. Active session, no exercise -> show exercise picker
  3. Active exercise            -> show previous sets + set logger

The 'End workout' flow lives in the sidebar and is available during
states 2 and 3.
"""

import pandas as pd
import streamlit as st

import config
from components.exercise_picker import render as render_exercise_picker
from components.set_logger import render as render_set_logger
from services.workout import (
    WorkoutError,
    add_exercise,
    end_session,
    get_active_session,
    get_execution_details,
    get_last_performance,
    get_sets,
    log_set,
    start_session,
)


# ============================================================
# Auth gate
# ============================================================

if st.session_state.get("user_id") is None:
    st.warning("Please log in from the home page first.")
    st.stop()

USER_ID = st.session_state.user_id


# ============================================================
# Sync session state with database on every load
# ============================================================
# A user might log in, start a workout, close the browser, and come back
# the next day. We detect that by always asking the database what the
# truth is, rather than trusting session state alone.

active = get_active_session(USER_ID)
if active is not None:
    st.session_state.active_session_id = active["session_id"]
else:
    st.session_state.active_session_id = None
    st.session_state.current_execution_id = None  # can't have an exercise without a session


# ============================================================
# Sidebar - end workout
# ============================================================

with st.sidebar:
    st.write(f"Signed in as **{st.session_state.user_email}**")

    if st.session_state.active_session_id is not None:
        st.divider()
        st.write(f"Active workout: **#{st.session_state.active_session_id}**")

        with st.expander("End workout"):
            notes = st.text_area("Notes (optional)", key="end_notes")
            if st.button("Confirm end workout", use_container_width=True):
                try:
                    end_session(st.session_state.active_session_id, notes=notes)
                except WorkoutError as e:
                    st.error(str(e))
                else:
                    st.session_state.active_session_id = None
                    st.session_state.current_execution_id = None
                    st.success("Workout ended.")
                    st.rerun()


# ============================================================
# Page header
# ============================================================

st.title("🏋️ Workout")


# ============================================================
# State 1: No active session - start a new workout
# ============================================================

if st.session_state.active_session_id is None:
    st.subheader("Start a new workout")

    col1, col2 = st.columns(2)
    with col1:
        workout_type = st.selectbox("Workout type", config.WORKOUT_TYPES)
        gym_location = st.text_input("Gym location (optional)")
    with col2:
        sleep_hours = st.number_input(
            "Sleep last night (hours)",
            min_value=0.0,
            max_value=14.0,
            value=7.5,
            step=0.5,
            help="Optional - leave at 0 to skip.",
        )
        energy = st.slider(
            "Energy level right now",
            min_value=1,
            max_value=10,
            value=7,
            help="1 = exhausted, 10 = ready to crush it.",
        )

    if st.button("▶️ Begin workout", use_container_width=True):
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
            st.success(f"Workout #{session_id} started.")
            st.rerun()


# ============================================================
# State 2: Active session, no exercise selected - pick one
# ============================================================

elif st.session_state.current_execution_id is None:
    st.subheader("Add exercise")

    selection = render_exercise_picker(key_prefix="add_ex")

    if selection is not None:
        # Show the user how they last performed this exercise, if ever
        last = get_last_performance(USER_ID, selection["exercise_id"])
        if last is not None:
            st.caption(
                f"Last time: {last['weight_kg']:.1f}kg × {last['reps']} reps"
                + (f" @ RPE {last['rpe']}" if last["rpe"] else "")
            )

        if st.button("➕ Add this exercise", use_container_width=True):
            try:
                execution_id = add_exercise(
                    session_id=st.session_state.active_session_id,
                    exercise_id=selection["exercise_id"],
                    equipment_brand=selection["equipment_brand"],
                    equipment_model=selection["equipment_model"],
                )
            except WorkoutError as e:
                st.error(str(e))
            else:
                st.session_state.current_execution_id = execution_id
                st.rerun()


# ============================================================
# State 3: Active exercise - log sets
# ============================================================

else:
    execution_id = st.session_state.current_execution_id
    execution = get_execution_details(execution_id)

    # Defensive: if the execution id in session state points at something
    # invalid (e.g. database was reset mid-session during development),
    # clear it and rerun.
    if execution is None:
        st.session_state.current_execution_id = None
        st.rerun()

    st.subheader(f"🏋️ {execution['exercise_name']}")
    st.caption(f"{execution['muscle_group']} · {execution['exercise_type']}")

    # --- Show sets logged so far ---
    sets_so_far = get_sets(execution_id)
    if sets_so_far:
        st.write("### Sets logged")
        df = pd.DataFrame(
            [
                {
                    "Set": s["set_number"],
                    "Weight (kg)": s["weight_kg"],
                    "Reps": s["reps"],
                    "RPE": s["rpe"] if s["rpe"] is not None else "-",
                    "RIR": s["rir"] if s["rir"] is not None else "-",
                    "Rest (s)": s["rest_seconds"] if s["rest_seconds"] is not None else "-",
                }
                for s in sets_so_far
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- Pre-fill the logger with the last set's values when possible ---
    if sets_so_far:
        last_set = sets_so_far[-1]
        defaults = {
            "default_weight": float(last_set["weight_kg"]),
            "default_reps": int(last_set["reps"]),
            "default_rpe": int(last_set["rpe"]) if last_set["rpe"] is not None else 7,
            "default_rir": int(last_set["rir"]) if last_set["rir"] is not None else 3,
            "default_rest_seconds": int(last_set["rest_seconds"]) if last_set["rest_seconds"] is not None else 90,
        }
    else:
        # First set of this exercise - use the user's last performance if any
        last_perf = get_last_performance(USER_ID, execution["exercise_id"])
        if last_perf is not None:
            defaults = {
                "default_weight": float(last_perf["weight_kg"]),
                "default_reps": int(last_perf["reps"]),
                "default_rpe": int(last_perf["rpe"]) if last_perf["rpe"] is not None else 7,
                "default_rir": int(last_perf["rir"]) if last_perf["rir"] is not None else 3,
                "default_rest_seconds": 90,
            }
            st.caption(
                f"Pre-filled from your last session: "
                f"{last_perf['weight_kg']:.1f}kg × {last_perf['reps']}"
            )
        else:
            defaults = {}  # use the component's built-in defaults

    # --- Set logger form ---
    st.write("### Log next set")
    result = render_set_logger(key_prefix=f"logger_ex{execution_id}", **defaults)
    if result is not None:
        log_set(
            execution_id=execution_id,
            weight_kg=result["weight_kg"],
            reps=result["reps"],
            rpe=result["rpe"],
            rir=result["rir"],
            rest_seconds=result["rest_seconds"],
        )
        st.success(f"Set #{len(sets_so_far) + 1} logged.")
        st.rerun()

    # --- Finish exercise button ---
    st.divider()
    if st.button("✔️ Finish this exercise", use_container_width=True):
        st.session_state.current_execution_id = None
        st.rerun()