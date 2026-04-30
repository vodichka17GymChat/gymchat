"""
Exercise card component. Renders one exercise within a workout session.

This is the building block of the new workout view. Instead of the old
'one screen per exercise, modally' flow, the workout page stacks one of
these cards per exercise and the user scrolls between them. They can
expand any past exercise and add a forgotten set without losing context.

Each card contains:
  - Header (exercise name + set count)
  - Equipment line (if recorded)
  - List of logged sets with delete buttons
  - Live rest timer (only between sets within this exercise)
  - Set logger form, pre-filled from the previous set
"""

import streamlit as st

from components import rest_timer
from components.set_logger import render as render_set_logger
from services.workout import (
    WorkoutError,
    get_execution_details,
    get_last_performance,
    get_sets,
    log_set,
    remove_set,
)


def render(execution_id: int, user_id: int, expanded: bool = False) -> None:
    """
    Render one exercise card.

    Args:
        execution_id: which exercise execution this card represents.
        user_id: needed to look up the user's last performance for prefill.
        expanded: whether the card starts open. The currently-active
                  exercise should be expanded; older ones collapsed to
                  save vertical space on long sessions.
    """
    execution = get_execution_details(execution_id)
    if execution is None:
        # Stale execution_id (e.g. database reset during development).
        # Silently skip - the workout page will sort itself out on
        # the next interaction.
        return

    sets_so_far = get_sets(execution_id)
    set_count = len(sets_so_far)

    header = _build_header(execution["exercise_name"], set_count)

    with st.expander(header, expanded=expanded):
        # --- Equipment line (only if user filled it in) ---
        equipment_parts = [
            p for p in (execution["equipment_brand"], execution["equipment_model"])
            if p
        ]
        if equipment_parts:
            st.caption(f"📍 {' '.join(equipment_parts)}")

        # --- Logged sets so far ---
        if sets_so_far:
            for s in sets_so_far:
                _render_set_row(s)
        else:
            st.caption("_No sets yet — log your first one below._")

        # --- Live rest timer (only between sets) ---
        # We hide this before the first set since there's nothing to
        # rest from. Once at least one set exists, the timer shows
        # elapsed time since that set's timestamp.
        if sets_so_far:
            rest_timer.render_live(sets_so_far[-1]["timestamp"])

        # --- Set logger form ---
        defaults = _compute_defaults(sets_so_far, user_id, execution["exercise_id"])
        result = render_set_logger(
            key_prefix=f"logger_ex{execution_id}",
            **defaults,
        )

        if result is not None:
            _handle_log_set(execution_id, result, sets_so_far)


# ============================================================
# Internal helpers
# ============================================================

def _build_header(exercise_name: str, set_count: int) -> str:
    """Header text for the expander. Includes set count for at-a-glance progress."""
    if set_count == 0:
        return f"**{exercise_name}**"
    return f"**{exercise_name}**  ·  {set_count} set{'s' if set_count != 1 else ''}"


def _render_set_row(s) -> None:
    """
    Render one already-logged set as a compact row, with a small
    delete button on the right for undoing mistakes.
    """
    cols = st.columns([1, 4, 1])

    cols[0].markdown(f"**Set {s['set_number']}**")

    detail = f"{s['weight_kg']:.1f} kg × {s['reps']}"
    extras = []
    if s["rpe"] is not None:
        extras.append(f"RPE {s['rpe']}")
    if s["rir"] is not None:
        extras.append(f"RIR {s['rir']}")
    if extras:
        detail += "  ·  " + " · ".join(extras)
    cols[1].write(detail)

    if cols[2].button("🗑", key=f"del_set_{s['set_id']}", help="Delete this set"):
        remove_set(s["set_id"])
        st.rerun()


def _compute_defaults(sets_so_far, user_id: int, exercise_id: int) -> dict:
    """
    Pick sensible defaults to pre-fill the set logger.

    Priority order:
      1. The most recent set in this execution - we're mid-exercise,
         user is likely repeating or making a small adjustment.
      2. The user's last performance of this exercise across all
         sessions - first set of the day, "what did I do last time?".
      3. Empty - fall back to the component's built-in defaults.
    """
    if sets_so_far:
        last = sets_so_far[-1]
        return {
            "default_weight": float(last["weight_kg"]),
            "default_reps": int(last["reps"]),
            "default_rpe": int(last["rpe"]) if last["rpe"] is not None else None,
            "default_rir": int(last["rir"]) if last["rir"] is not None else None,
        }

    last_perf = get_last_performance(user_id, exercise_id)
    if last_perf is not None:
        return {
            "default_weight": float(last_perf["weight_kg"]),
            "default_reps": int(last_perf["reps"]),
            "default_rpe": int(last_perf["rpe"]) if last_perf["rpe"] is not None else None,
            "default_rir": int(last_perf["rir"]) if last_perf["rir"] is not None else None,
        }

    return {}


def _handle_log_set(execution_id: int, result: dict, sets_so_far) -> None:
    """
    Save a set the user just submitted. If they didn't manually override
    the rest time, fill it in from the live timer (seconds since the
    previous set in this execution).
    """
    rest_seconds = result["rest_seconds"]
    if rest_seconds is None and sets_so_far:
        rest_seconds = rest_timer.get_elapsed_seconds(sets_so_far[-1]["timestamp"])

    try:
        log_set(
            execution_id=execution_id,
            weight_kg=result["weight_kg"],
            reps=result["reps"],
            rpe=result["rpe"],
            rir=result["rir"],
            rest_seconds=rest_seconds,
        )
    except WorkoutError as e:
        st.error(str(e))
        return

    # Remember which card the user just acted in - the workout page
    # uses this to keep the same card expanded after the rerun, so
    # repeated set-logging doesn't bounce focus around.
    st.session_state.focused_execution_id = execution_id
    st.rerun()
