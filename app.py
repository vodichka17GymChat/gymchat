"""
GymChat entry point.

When signed out: shows login / register tabs.
When signed in: shows a dashboard - the user's home base.

The Workout, History, and Profile pages live in pages/ and Streamlit
auto-discovers them. They're hidden from the sidebar until login by
the auth gate at the top of each page.

Design notes:
- Layout is 'centered', not 'wide'. Most users will be on a phone in
  the gym, and centered (~730px max) reads beautifully there while
  still looking fine on desktop.
- Registration is intentionally minimal: email + password. Body
  metrics, training experience, etc. live on the Profile page where
  the user can fill them in when they have time. We surface a
  "complete your profile" prompt on the dashboard for the new user.
"""

import streamlit as st

import config
from components.theme import inject_theme
from db.connection import init_db
from db.users import get_user_by_id
from services.auth import AuthError, login, register_user
from services.dashboard import get_dashboard_summary
from services.workout import get_active_session
from utils.datetime_helpers import format_datetime, format_relative
from utils.validators import MIN_PASSWORD_LENGTH


# ============================================================
# One-time setup
# ============================================================

init_db()

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="centered",
    initial_sidebar_state="auto",
)

inject_theme()


# ============================================================
# Session state defaults
# ============================================================

def _init_session_state():
    """
    Streamlit reruns this whole file on every interaction. Session
    state holds values that need to survive reruns. Setting defaults
    once (only if not already present) means we don't clobber values
    set later in the lifecycle.
    """
    defaults = {
        "user_id": None,
        "user_email": None,
        "active_session_id": None,
        "focused_execution_id": None,
        "show_end_form": False,
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

    if st.button("Log in", use_container_width=True, type="primary"):
        try:
            user_id = login(email, password)
        except AuthError as e:
            st.error(str(e))
            return

        st.session_state.user_id = user_id
        st.session_state.user_email = email.strip().lower()
        st.rerun()


def _render_register_form():
    """
    Minimal sign-up. Just email + password + confirm. Profile details
    are deferred to the Profile page so first-time users hit the gym
    floor instead of a wall of forms.
    """
    st.subheader("Create an account")
    st.caption(
        "Just an email and password to get started. "
        "You can add your training details after."
    )

    email = st.text_input("Email", key="reg_email")
    password = st.text_input(
        "Password",
        type="password",
        key="reg_password",
        help=f"At least {MIN_PASSWORD_LENGTH} characters.",
    )
    confirm = st.text_input(
        "Confirm password",
        type="password",
        key="reg_confirm",
    )

    if st.button("Create account", use_container_width=True, type="primary"):
        if password != confirm:
            st.error("Passwords don't match.")
            return

        try:
            user_id = register_user(email=email, password=password)
        except AuthError as e:
            st.error(str(e))
            return

        st.session_state.user_id = user_id
        st.session_state.user_email = email.strip().lower()
        st.success("Welcome to GymChat 💪")
        st.rerun()


# ============================================================
# Logged-in dashboard
# ============================================================

def _render_sidebar():
    with st.sidebar:
        st.write(f"Signed in as **{st.session_state.user_email}**")
        if st.button("Log out", use_container_width=True):
            _logout()


def _logout():
    """Clear user-specific session state and rerun."""
    keys_to_clear = (
        "user_id", "user_email",
        "active_session_id", "focused_execution_id",
        "show_end_form",
    )
    for key in keys_to_clear:
        st.session_state[key] = None if key.endswith("_id") or key.endswith("_email") else False
    st.rerun()


def _render_active_workout_banner(active_session) -> None:
    """Top-of-page status strip when a workout is in progress."""
    started_str = format_relative(active_session["start_time"])
    workout_label = active_session["workout_type"] or "Workout"

    st.markdown(
        f"""
        <div class="gc-status-strip">
            <div class="gc-status-dot"></div>
            <span class="gc-status-label">{workout_label} in progress</span>
            <span class="gc-status-meta">Started {started_str}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("→ Resume workout", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Workout.py")


def _render_profile_prompt() -> None:
    """Prompt for users who haven't filled in their profile yet."""
    with st.container(border=True):
        st.markdown("### 👋 Quick setup")
        st.write(
            "Tell GymChat a bit about yourself — your training type, "
            "experience, and goals. It only takes a minute and helps "
            "us tailor the app to you."
        )
        if st.button("Complete profile", use_container_width=True):
            st.switch_page("pages/3_Profile.py")


def _render_quick_actions() -> None:
    """Three navigation cards linking to the main pages."""
    st.markdown('<p class="gc-section-label">Navigate</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/1_Workout.py", label="🏋️ Workout", use_container_width=True)
    with col2:
        st.page_link("pages/2_History.py", label="📊 History", use_container_width=True)
    with col3:
        st.page_link("pages/3_Profile.py", label="👤 Profile", use_container_width=True)


def _render_weekly_stats(summary: dict) -> None:
    """Three-up metric row for this week's training."""
    st.markdown('<p class="gc-section-label">This week</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Workouts", summary["weekly_workouts"])
    col2.metric("Sets", summary["weekly_sets"])
    col3.metric("Volume", f"{summary['weekly_volume']:,.0f} kg")


def _render_last_workout(last: dict) -> None:
    """Compact summary card for the user's most recent completed session."""
    st.markdown('<p class="gc-section-label">Last workout</p>', unsafe_allow_html=True)
    with st.container(border=True):
        title = last["workout_type"] or "Workout"
        st.markdown(f"**{title}**  ·  {format_datetime(last['start_time'])}")
        st.caption(
            f"{last['exercise_count']} exercise"
            f"{'s' if last['exercise_count'] != 1 else ''} · "
            f"{last['set_count']} set"
            f"{'s' if last['set_count'] != 1 else ''} · "
            f"{last['volume']:,.0f} kg total volume"
        )


def _render_dashboard():
    user_id = st.session_state.user_id

    _render_sidebar()

    user = get_user_by_id(user_id)
    if user is None:
        st.error("Could not load your account. Please log out and back in.")
        return

    name_hint = st.session_state.user_email.split("@")[0]
    st.markdown(f"### Welcome back, **{name_hint}** 👋")

    # 1. Active workout banner
    active = get_active_session(user_id)
    if active is not None:
        _render_active_workout_banner(active)

    # 2. Profile completion prompt for new users
    if user[config.PROFILE_COMPLETE_MARKER] is None:
        _render_profile_prompt()

    # 3. Quick-action navigation row
    _render_quick_actions()

    # 4. Weekly stats
    summary = get_dashboard_summary(user_id)
    _render_weekly_stats(summary)

    # 5. Last completed workout
    if summary["last_workout"] is not None:
        _render_last_workout(summary["last_workout"])
    elif active is None and summary["total_workouts"] == 0:
        st.info(
            "No workouts logged yet. Hit **Start a workout** below to "
            "log your first session."
        )

    # 6. Primary CTA — only when there's no active workout
    if active is None:
        st.divider()
        if st.button("▶️ Start a workout", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Workout.py")


# ============================================================
# Page routing
# ============================================================

if st.session_state.user_id is None:
    st.markdown(
        f"""
        <div class="gc-hero">
            <div class="gc-hero-icon">{config.APP_ICON}</div>
            <div class="gc-hero-title">{config.APP_NAME}</div>
            <div class="gc-hero-sub">Track your training. Own your progress.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tab_login, tab_register = st.tabs(["Log in", "Register"])
    with tab_login:
        _render_login_form()
    with tab_register:
        _render_register_form()
else:
    _render_dashboard()
