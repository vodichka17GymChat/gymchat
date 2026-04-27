"""
Profile page - view and edit your user details. The athlete_type field
is the most important one for future analytics: it sets the baseline
for what 'normal' rest times, rep ranges, and intensities look like
for this user.
"""

import streamlit as st

import config
from db.users import get_user_by_id, update_user_profile


# ============================================================
# Auth gate
# ============================================================

if st.session_state.get("user_id") is None:
    st.warning("Please log in from the home page first.")
    st.stop()

USER_ID = st.session_state.user_id


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.write(f"Signed in as **{st.session_state.user_email}**")


# ============================================================
# Load current user data
# ============================================================

user = get_user_by_id(USER_ID)
if user is None:
    # Shouldn't happen unless the user was deleted while logged in,
    # but guard against the crash.
    st.error("Could not load your profile. Please log out and back in.")
    st.stop()


# ============================================================
# Helpers for safe dropdown defaults
# ============================================================

def _index_or_zero(options: list[str], current: str | None) -> int:
    """
    Return the index of `current` in `options`, or 0 if it's missing
    or the value is no longer a valid choice (e.g. we removed an
    athlete type from config but a user still has it on their record).
    """
    if current and current in options:
        return options.index(current)
    return 0


# ============================================================
# Profile form
# ============================================================

st.title("👤 Profile")
st.caption("Update any field below. Changes are saved when you click Save.")

with st.form("profile_form"):
    st.write(f"**Email:** {user['email']}")
    st.caption("Email cannot be changed.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Age",
            min_value=config.AGE_MIN,
            max_value=config.AGE_MAX,
            value=int(user["age"]) if user["age"] is not None else 25,
            step=1,
        )
        gender = st.selectbox(
            "Gender",
            config.GENDERS,
            index=_index_or_zero(config.GENDERS, user["gender"]),
        )
        height_cm = st.number_input(
            "Height (cm)",
            min_value=config.HEIGHT_CM_MIN,
            max_value=config.HEIGHT_CM_MAX,
            value=int(user["height_cm"]) if user["height_cm"] is not None else 170,
            step=1,
        )
        weight_kg = st.number_input(
            "Weight (kg)",
            min_value=config.WEIGHT_KG_MIN,
            max_value=config.WEIGHT_KG_MAX,
            value=float(user["weight_kg"]) if user["weight_kg"] is not None else 70.0,
            step=0.5,
            format="%.1f",
        )

    with col2:
        experience = st.number_input(
            "Training experience (months)",
            min_value=0,
            max_value=config.EXPERIENCE_MONTHS_MAX,
            value=int(user["training_experience_months"]) if user["training_experience_months"] is not None else 0,
            step=1,
        )
        fitness_level = st.selectbox(
            "Fitness level",
            config.FITNESS_LEVELS,
            index=_index_or_zero(config.FITNESS_LEVELS, user["fitness_level"]),
        )
        athlete_type = st.selectbox(
            "Athlete type",
            config.ATHLETE_TYPES,
            index=_index_or_zero(config.ATHLETE_TYPES, user["athlete_type"]),
            help="Used to set sensible defaults for what 'normal' looks like for you.",
        )
        primary_goal = st.selectbox(
            "Primary goal",
            config.PRIMARY_GOALS,
            index=_index_or_zero(config.PRIMARY_GOALS, user["primary_goal"]),
        )

    submitted = st.form_submit_button("💾 Save changes", use_container_width=True)

    if submitted:
        update_user_profile(
            user_id=USER_ID,
            age=int(age),
            gender=gender,
            height_cm=float(height_cm),
            weight_kg=float(weight_kg),
            training_experience_months=int(experience),
            fitness_level=fitness_level,
            athlete_type=athlete_type,
            primary_goal=primary_goal,
        )
        st.success("Profile saved.")
        st.rerun()


# ============================================================
# Account summary footer
# ============================================================

st.divider()
st.caption(
    f"Account created: {user['created_at'][:10]}"
    + (f" · Last updated: {user['updated_at'][:10]}" if user["updated_at"] else "")
)