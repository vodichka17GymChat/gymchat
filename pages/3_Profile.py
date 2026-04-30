"""
Profile page - view and edit your user details.

After the move to two-step signup (just email + password to create an
account), most new users land here with everything blank. We surface
a friendly welcome banner in that case and route the dashboard's
"complete profile" button straight to this page.

The athlete_type field is the most important one for future analytics:
it sets the baseline for what 'normal' rest times, rep ranges, and
intensities look like for this user. We treat it as the canonical
"is this profile complete?" marker (see config.PROFILE_COMPLETE_MARKER).
"""

import streamlit as st

import config
from components.theme import inject_theme
from db.users import get_user_by_id, update_user_profile

inject_theme()


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
    st.error("Could not load your profile. Please log out and back in.")
    st.stop()


# ============================================================
# Helpers
# ============================================================

def _index_or_zero(options: list[str], current: str | None) -> int:
    """
    Return the index of `current` in `options`, or 0 if it's missing
    or no longer a valid choice.
    """
    if current and current in options:
        return options.index(current)
    return 0


# ============================================================
# Header
# ============================================================

st.title("👤 Profile")

profile_is_incomplete = user[config.PROFILE_COMPLETE_MARKER] is None

if profile_is_incomplete:
    with st.container(border=True):
        st.markdown("### 👋 Welcome to GymChat!")
        st.write(
            "Take a moment to fill in your training details below. "
            "It only takes a minute, and it helps the app give you "
            "more useful suggestions over time. "
            "You can update any of these later."
        )

# Account metadata strip — email, created date, last updated
created = user["created_at"][:10] if user["created_at"] else "—"
updated = user["updated_at"][:10] if user["updated_at"] else None
updated_part = f'<span><strong>Updated</strong> {updated}</span>' if updated else ""

st.markdown(
    f"""
    <div class="gc-meta-strip">
        <span><strong>Account</strong> {user['email']}</span>
        <span><strong>Joined</strong> {created}</span>
        {updated_part}
    </div>
    """,
    unsafe_allow_html=True,
)

if not profile_is_incomplete:
    st.caption("Update any field below. Changes save when you click **Save**.")


# ============================================================
# Profile form
# ============================================================

with st.container(border=True):
    with st.form("profile_form"):
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

        submit_label = "Complete setup" if profile_is_incomplete else "💾 Save changes"
        submitted = st.form_submit_button(
            submit_label,
            use_container_width=True,
            type="primary",
        )

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
