"""
Set logger component. Renders the form for logging one set's worth of
data and returns the values when the user submits. Designed to be used
inside an st.form so all inputs submit together.

Used on the Workout page during an active exercise.
"""

import streamlit as st

import config


def render(
    key_prefix: str = "set_logger",
    default_weight: float = 20.0,
    default_reps: int = 10,
    default_rpe: int = 7,
    default_rir: int = 3,
    default_rest_seconds: int = 90,
) -> dict | None:
    """
    Render the set logging form. Returns a dict with the values when the
    user clicks 'Log set', or None on every other rerun.

        {
            "weight_kg": float,
            "reps": int,
            "rpe": int,
            "rir": int,
            "rest_seconds": int,
        }

    Defaults can be passed in - useful for pre-filling with the user's
    last set so they only adjust what changed.
    """
    with st.form(key=f"{key_prefix}_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input(
                "Weight (kg)",
                min_value=config.WEIGHT_INPUT_MIN,
                max_value=config.WEIGHT_INPUT_MAX,
                value=default_weight,
                step=2.5,
                format="%.1f",
                key=f"{key_prefix}_weight",
            )
            rpe = st.number_input(
                "RPE (1-10, how hard)",
                min_value=config.RPE_MIN,
                max_value=config.RPE_MAX,
                value=default_rpe,
                step=1,
                key=f"{key_prefix}_rpe",
                help="Rate of Perceived Exertion. 10 = absolute max effort.",
            )
        with col2:
            reps = st.number_input(
                "Reps",
                min_value=config.REPS_MIN,
                max_value=config.REPS_MAX,
                value=default_reps,
                step=1,
                key=f"{key_prefix}_reps",
            )
            rir = st.number_input(
                "RIR (reps in reserve)",
                min_value=config.RIR_MIN,
                max_value=config.RIR_MAX,
                value=default_rir,
                step=1,
                key=f"{key_prefix}_rir",
                help="How many more reps you could have done. 0 = failure.",
            )

        rest = st.number_input(
            "Rest before this set (seconds)",
            min_value=0,
            max_value=config.REST_SECONDS_MAX,
            value=default_rest_seconds,
            step=15,
            key=f"{key_prefix}_rest",
            help="How long you rested since the previous set.",
        )

        submitted = st.form_submit_button("✅ Log set", use_container_width=True)

        if submitted:
            return {
                "weight_kg": float(weight),
                "reps": int(reps),
                "rpe": int(rpe),
                "rir": int(rir),
                "rest_seconds": int(rest),
            }
        return None