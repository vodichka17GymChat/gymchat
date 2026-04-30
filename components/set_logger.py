"""
Set logger component. A compact form for logging one set.

Design philosophy:
- The 80% case is "same as last set" or "+2.5kg, same reps". We optimize
  for that: weight and reps are visible, pre-filled, and the form
  doesn't clear on submit so a quick second click repeats the entry.
- RPE and RIR are useful but most users don't track them. They live in
  an expander, gated by per-field checkboxes.
- Rest seconds is NOT asked here by default - the rest timer measures
  it automatically. Manual override lives in the advanced expander
  for the rare case where the user wants to correct it.

Note on Streamlit forms: widgets inside a form don't trigger reruns
on interaction - only the submit button does. That means we can't
dynamically disable inputs based on a checkbox in the same form
(the disabled state only refreshes after submit). So we keep all
inputs editable and treat the checkbox as a "save this?" decision
applied at submit time. Honest, predictable, and it works.
"""

import streamlit as st

import config


def render(
    key_prefix: str = "set_logger",
    default_weight: float = 20.0,
    default_reps: int = 10,
    default_rpe: int | None = None,
    default_rir: int | None = None,
    default_rest_seconds: int | None = None,
) -> dict | None:
    """
    Render the set logging form. Returns a dict on submit, None on every
    other rerun.

    Returned shape:
        {
            "weight_kg": float,
            "reps": int,
            "rpe": int | None,           # None unless user ticked the box
            "rir": int | None,           # None unless user ticked the box
            "rest_seconds": int | None,  # None means "use measured time"
        }

    Defaults pre-fill the inputs - typically from the user's previous
    set. Pass default_rpe=None / default_rir=None to start with those
    fields off.
    """
    advanced_open = default_rpe is not None or default_rir is not None

    st.markdown('<p class="gc-section-label">Log next set</p>', unsafe_allow_html=True)

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
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
        with col2:
            reps = st.number_input(
                "Reps",
                min_value=config.REPS_MIN,
                max_value=config.REPS_MAX,
                value=default_reps,
                step=1,
                key=f"{key_prefix}_reps",
            )

        with st.expander("Advanced (RPE · RIR · rest override)", expanded=advanced_open):
            st.caption(
                "Tick the boxes for the fields you want to record on "
                "this set. Untracked fields are saved as 'not recorded'."
            )

            use_rpe = st.checkbox(
                "Record RPE (rate of perceived exertion, 1-10)",
                value=default_rpe is not None,
                key=f"{key_prefix}_use_rpe",
                help="10 = max effort, couldn't have done another rep.",
            )
            rpe = st.number_input(
                "RPE",
                min_value=config.RPE_MIN,
                max_value=config.RPE_MAX,
                value=default_rpe if default_rpe is not None else 7,
                step=1,
                key=f"{key_prefix}_rpe",
            )

            use_rir = st.checkbox(
                "Record RIR (reps in reserve)",
                value=default_rir is not None,
                key=f"{key_prefix}_use_rir",
                help="How many more reps you could have done. 0 = failure.",
            )
            rir = st.number_input(
                "RIR",
                min_value=config.RIR_MIN,
                max_value=config.RIR_MAX,
                value=default_rir if default_rir is not None else 3,
                step=1,
                key=f"{key_prefix}_rir",
            )

            override_rest = st.checkbox(
                "Override measured rest time",
                value=False,
                key=f"{key_prefix}_override_rest",
                help=(
                    "By default the app measures rest from your last set. "
                    "Tick this to enter it manually instead."
                ),
            )
            rest_input = st.number_input(
                "Rest before this set (seconds)",
                min_value=0,
                max_value=config.REST_SECONDS_MAX,
                value=default_rest_seconds or config.DEFAULT_REST_SECONDS,
                step=15,
                key=f"{key_prefix}_rest",
            )

        submitted = st.form_submit_button(
            "✅ Log set",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            return {
                "weight_kg": float(weight),
                "reps": int(reps),
                "rpe": int(rpe) if use_rpe else None,
                "rir": int(rir) if use_rir else None,
                # None signals "use the measured rest time"
                "rest_seconds": int(rest_input) if override_rest else None,
            }
        return None
