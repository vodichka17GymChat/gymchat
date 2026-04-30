"""
Exercise picker component. Renders filter dropdowns and an exercise
selector, plus optional equipment fields. Returns the user's selection.

Used on the Workout page when adding a new exercise to a session.
"""

import streamlit as st

from db import exercises as exercises_db


def render(key_prefix: str = "picker") -> dict:
    """
    Render the exercise picker UI. Returns a dict with the user's
    current selection:

        {
            "exercise_id": int,
            "exercise_name": str,
            "muscle_group": str,
            "exercise_type": str,
            "equipment_brand": str,   # may be empty
            "equipment_model": str,   # may be empty
        }

    Returns None if no exercises match the current filters (which
    shouldn't happen in normal use but guards against an edge case).

    The key_prefix lets the same component appear multiple times on
    one page without Streamlit widget-key collisions.
    """
    # --- Filters ---
    st.markdown('<p class="gc-section-label">Filters</p>', unsafe_allow_html=True)

    muscle_groups = ["All"] + exercises_db.get_muscle_groups()
    exercise_types = ["All", "compound", "isolation"]

    col1, col2 = st.columns(2)
    with col1:
        muscle_filter = st.selectbox(
            "Muscle group",
            muscle_groups,
            key=f"{key_prefix}_muscle",
        )
    with col2:
        type_filter = st.selectbox(
            "Exercise type",
            exercise_types,
            key=f"{key_prefix}_type",
        )

    # --- Search exercises with the selected filters ---
    filtered = exercises_db.search_exercises(
        muscle_group=None if muscle_filter == "All" else muscle_filter,
        exercise_type=None if type_filter == "All" else type_filter,
    )

    if not filtered:
        st.warning("No exercises match these filters.")
        return None

    # --- Exercise selector ---
    st.markdown('<p class="gc-section-label">Exercise</p>', unsafe_allow_html=True)

    options = {
        f"{row['exercise_name']}  ·  {row['muscle_group']} · {row['exercise_type']}": row
        for row in filtered
    }
    chosen_label = st.selectbox(
        "Exercise",
        list(options.keys()),
        key=f"{key_prefix}_exercise",
    )
    chosen = options[chosen_label]

    # --- Equipment fields ---
    st.markdown('<p class="gc-section-label">Equipment (optional)</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        brand = st.text_input(
            "Equipment brand",
            key=f"{key_prefix}_brand",
        )
    with col2:
        model = st.text_input(
            "Equipment model",
            key=f"{key_prefix}_model",
        )

    return {
        "exercise_id": chosen["exercise_id"],
        "exercise_name": chosen["exercise_name"],
        "muscle_group": chosen["muscle_group"],
        "exercise_type": chosen["exercise_type"],
        "equipment_brand": brand.strip(),
        "equipment_model": model.strip(),
    }
