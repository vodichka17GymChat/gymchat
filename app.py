"""
GymChat entry point. Initializes the database, renders the login/register
screen, and shows a landing page when the user is logged in.

The Workout, History, and Profile screens live in pages/ - Streamlit picks
them up automatically and shows them in the sidebar once a user is logged in.
"""

import streamlit as st

import config
from db.connection import init_db
from services.auth import AuthError, login, register_user


# ============================================================
# One-time setup
# ============================================================

# Make sure the database exists and the schema is current. Safe to call
# on every page load - it's a no-op after the first run.
init_db()

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="wide",
)


# ============================================================
# Session state defaults
# ============================================================

# Streamlit reruns this whole file on every interaction, so we use
# st.session_state to hold values that persist across reruns. Set
# defaults once - subsequent runs see them already present.
def _init_session_state():
    defaults = {
        "user_id": None,
        "user_email": None,
        # Active workout state, used by the Workout page
        "active_session_id": None,
        "current_execution_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_session_state()


# ============================================================
# Login / register
# ============================================================

def _render_login_form():
    st.subheader("Log in")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", use_container_width=True):
        try:
            user_id = login(email, password)
        except AuthError as e:
            st.error(str(e))
            return

        st.session_state.user_id = user_id
        st.session_state.user_email = email.strip().lower()
        st.success("Logged in.")
        st.rerun()


def _render_register_form():
    st.subheader("Create an account")

    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input(
            "Password",
            type="password",
            key="reg_password",
            help="Minimum 8 characters.",
        )
        age = st.number_input(
            "Age",
            min_value=config.AGE_MIN,
            max_value=config.AGE_MAX,
            value=25,
            step=1,
            key="reg_age",
        )
        gender = st.selectbox("Gender", config.GENDERS, key="reg_gender")
    with col2:
        height_cm = st.number_input(
            "Height (cm)",
            min_value=config.HEIGHT_CM_MIN,
            max_value=config.HEIGHT_CM_MAX,
            value=170,
            step=1,
            key="reg_height",
        )
        weight_kg = st.number_input(
            "Weight (kg)",
            min_value=config.WEIGHT_KG_MIN,
            max_value=config.WEIGHT_KG_MAX,
            value=70.0,
            step=0.5,
            format="%.1f",
            key="reg_weight",
        )
        experience = st.number_input(
            "Training experience (months)",
            min_value=0,
            max_value=config.EXPERIENCE_MONTHS_MAX,
            value=0,
            step=1,
            key="reg_experience",
        )
        fitness_level = st.selectbox(
            "Fitness level",
            config.FITNESS_LEVELS,
            key="reg_fitness",
        )

    athlete_type = st.selectbox(
        "Athlete type",
        config.ATHLETE_TYPES,
        key="reg_athlete_type",
        help="Used to set sensible defaults for what 'normal' looks like for you.",
    )
    primary_goal = st.selectbox(
        "Primary goal",
        config.PRIMARY_GOALS,
        key="reg_goal",
    )

    if st.button("Create account", use_container_width=True):
        try:
            user_id = register_user(
                email=email,
                password=password,
                age=int(age),
                gender=gender,
                height_cm=float(height_cm),
                weight_kg=float(weight_kg),
                training_experience_months=int(experience),
                fitness_level=fitness_level,
                athlete_type=athlete_type,
                primary_goal=primary_goal,
            )
        except AuthError as e:
            st.error(str(e))
            return

        st.session_state.user_id = user_id
        st.session_state.user_email = email.strip().lower()
        st.success("Account created. Welcome!")
        st.rerun()


# ============================================================
# Logged-in landing
# ============================================================

def _render_landing():
    st.subheader(f"Welcome back, {st.session_state.user_email}")
    st.write(
        "Use the sidebar to start a workout, view your history, or update your profile."
    )

    with st.sidebar:
        st.write(f"Signed in as **{st.session_state.user_email}**")
        if st.button("Log out", use_container_width=True):
            for key in ("user_id", "user_email", "active_session_id", "current_execution_id"):
                st.session_state[key] = None
            st.rerun()


# ============================================================
# Page routing
# ============================================================

st.title(f"{config.APP_ICON} {config.APP_NAME}")

if st.session_state.user_id is None:
    tab_login, tab_register = st.tabs(["Log in", "Register"])
    with tab_login:
        _render_login_form()
    with tab_register:
        _render_register_form()
else:
    _render_landing()