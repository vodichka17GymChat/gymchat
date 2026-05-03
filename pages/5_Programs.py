"""
Programs page — build and manage multi-session training programs.

A program is an ordered list of workout templates the user works through
in sequence, cycling N times. This page covers:
  - Viewing existing programs and enrollment status
  - Creating a new program from saved templates
  - Enrolling / unenrolling
  - Advancing to the next session after a workout
  - Deleting programs
"""

import streamlit as st

from components.theme import inject_theme
from services.programs import (
    advance,
    create_program,
    delete_program,
    enroll,
    get_active_enrollment,
    get_enrollment_context,
    get_program_sessions,
    get_user_programs,
    unenroll,
)
from services.templates import get_user_templates
from services.workout import WorkoutError

inject_theme()


# ── Auth gate ────────────────────────────────────────────────────────────────

if st.session_state.get("user_id") is None:
    st.warning("Please log in from the home page first.")
    st.stop()

USER_ID = st.session_state.user_id


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.write(f"Signed in as **{st.session_state.user_email}**")


# ── Page header ──────────────────────────────────────────────────────────────

st.title("📋 Programs")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _session_label(pos: int, total: int, cycle: int, total_cycles: int) -> str:
    if total_cycles > 1:
        return f"Session {pos}/{total} · Cycle {cycle}/{total_cycles}"
    return f"Session {pos}/{total}"


# ── Active enrollment banner ─────────────────────────────────────────────────

ctx = get_enrollment_context(USER_ID)

if ctx:
    with st.container(border=True):
        st.markdown(
            f"**Active program: {ctx['program_name']}**  \n"
            f"{_session_label(ctx['session_number'], ctx['total_sessions'], ctx['current_cycle'], ctx['total_cycles'])}"
            f" — Next up: **{ctx['template_name']}**"
        )

        col_advance, col_unenroll = st.columns([3, 1])
        with col_advance:
            if st.button(
                "✓ Mark session done & advance",
                use_container_width=True,
                type="primary",
                key="advance_btn",
            ):
                try:
                    result = advance(USER_ID)
                except WorkoutError as e:
                    st.error(str(e))
                else:
                    if result == "program_complete":
                        st.success(f"🏆 You've completed **{ctx['program_name']}**!")
                    elif result == "cycle_complete":
                        st.success("Cycle complete — starting the next one.")
                    else:
                        st.success("Advanced to the next session.")
                    st.rerun()
        with col_unenroll:
            if st.button("Leave program", use_container_width=True, key="unenroll_btn"):
                try:
                    unenroll(USER_ID)
                except WorkoutError as e:
                    st.error(str(e))
                else:
                    st.rerun()

    st.divider()


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_mine, tab_create = st.tabs(["My Programs", "Create Program"])


# ── Tab 1: My Programs ───────────────────────────────────────────────────────

with tab_mine:
    programs = get_user_programs(USER_ID)

    if not programs:
        st.info("No programs yet. Use the **Create Program** tab to build one.")
    else:
        active_enrollment = get_active_enrollment(USER_ID)
        active_program_id = (
            active_enrollment["program_id"] if active_enrollment else None
        )

        for prog in programs:
            pid = prog["program_id"]
            sessions = get_program_sessions(pid)
            total = len(sessions) * prog["cycles"]
            is_active = pid == active_program_id

            with st.expander(
                f"{'🟢 ' if is_active else ''}{prog['name']}  ·  {total} session{'s' if total != 1 else ''}",
                expanded=is_active,
            ):
                if prog["description"]:
                    st.caption(prog["description"])

                cycle_label = (
                    f"{prog['cycles']}× cycle" if prog["cycles"] > 1
                    else "1 run-through"
                )
                st.caption(
                    f"{len(sessions)} template{'s' if len(sessions) != 1 else ''} · {cycle_label}"
                )

                # Session list
                for s in sessions:
                    st.markdown(f"- {s['position']}. **{s['template_name']}**")

                col_enroll, col_del = st.columns([3, 1])
                with col_enroll:
                    if is_active:
                        st.success("Currently enrolled")
                    else:
                        if st.button(
                            "Enroll",
                            use_container_width=True,
                            key=f"enroll_{pid}",
                        ):
                            try:
                                enroll(USER_ID, pid)
                            except WorkoutError as e:
                                st.error(str(e))
                            else:
                                st.rerun()
                with col_del:
                    if st.button(
                        "Delete",
                        use_container_width=True,
                        key=f"del_prog_{pid}",
                        help="Permanently delete this program",
                    ):
                        try:
                            delete_program(pid, USER_ID)
                        except WorkoutError as e:
                            st.error(str(e))
                        else:
                            st.rerun()


# ── Tab 2: Create Program ────────────────────────────────────────────────────

with tab_create:
    templates = get_user_templates(USER_ID)

    if not templates:
        st.info(
            "You need at least one saved template to build a program.  \n"
            "End a workout and check **Save as template** to create one."
        )
        st.stop()

    with st.form("create_program_form"):
        st.subheader("New program")

        name = st.text_input("Program name", placeholder="e.g. 12-Week Strength Block")
        description = st.text_area(
            "Description (optional)",
            placeholder="What's this program for?",
        )
        cycles = st.number_input(
            "Cycles (how many times to run through the sequence)",
            min_value=1,
            max_value=52,
            value=1,
            step=1,
            help="Set to 4 to repeat your weekly template 4 times = 4 weeks.",
        )

        st.markdown("**Sessions** — select templates in the order you want to perform them:")

        template_options = {t["name"]: t["template_id"] for t in templates}
        template_names = list(template_options.keys())

        # Let the user pick up to 14 slots (2 weeks of daily training)
        selected_slots: list[int] = []
        for i in range(1, 15):
            choice = st.selectbox(
                f"Session {i}",
                ["— (end here) —"] + template_names,
                key=f"prog_slot_{i}",
            )
            if choice == "— (end here) —":
                break
            selected_slots.append(template_options[choice])

        submitted = st.form_submit_button("Create program", type="primary")

    if submitted:
        try:
            pid = create_program(
                user_id=USER_ID,
                name=name,
                template_ids=selected_slots,
                description=description or None,
                cycles=int(cycles),
            )
        except WorkoutError as e:
            st.error(str(e))
        else:
            st.success(
                f"Program **{name}** created with {len(selected_slots)} sessions "
                f"× {int(cycles)} cycle(s) = {len(selected_slots) * int(cycles)} total sessions."
            )
            st.rerun()
