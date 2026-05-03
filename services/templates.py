"""
Template service. Owns the business logic for saving and launching
workout templates.

Two operations:
  save_session_as_template  — snapshot a completed session's exercises
                               into a named, reusable template.
  launch_template           — start a new workout session pre-populated
                               with a template's exercises.
"""

from typing import Optional

from db import templates as templates_db
from db import workouts as workouts_db
from services.workout import WorkoutError, start_session


def save_session_as_template(
    session_id: int,
    user_id: int,
    name: str,
) -> int:
    """
    Snapshot the exercises from a completed session into a new template.
    Returns the new template_id.

    Only the exercise list (with equipment) is saved — not sets or weights.
    Those come from the user's last performance when the template is launched.
    """
    name = name.strip()
    if not name:
        raise WorkoutError("Template name cannot be empty.")

    session = workouts_db.get_session(session_id)
    if session is None:
        raise WorkoutError("Session not found.")

    executions = workouts_db.get_executions_for_session(session_id)
    if not executions:
        raise WorkoutError("Cannot save a template from a session with no exercises.")

    template_id = templates_db.create_template(
        user_id=user_id,
        name=name,
        workout_type=session["workout_type"],
    )

    for ex in executions:
        templates_db.add_template_exercise(
            template_id=template_id,
            exercise_id=ex["exercise_id"],
            exercise_order=ex["execution_order"],
            equipment_brand=ex["equipment_brand"],
            equipment_model=ex["equipment_model"],
        )

    return template_id


def launch_template(
    template_id: int,
    user_id: int,
    gym_location: Optional[str] = None,
    sleep_hours: Optional[float] = None,
    energy_pre_workout: Optional[int] = None,
) -> int:
    """
    Start a new workout session pre-populated with all exercises from the
    template. Returns the new session_id.

    The template's workout_type is used for the session. Set weights are
    not pre-filled here — the exercise_card component already pulls the
    user's last performance for each exercise automatically.
    """
    template = templates_db.get_template(template_id)
    if template is None:
        raise WorkoutError("Template not found.")

    exercises = templates_db.get_template_exercises(template_id)
    if not exercises:
        raise WorkoutError("This template has no exercises.")

    session_id = start_session(
        user_id=user_id,
        workout_type=template["workout_type"] or "Other",
        gym_location=gym_location,
        sleep_hours=sleep_hours,
        energy_pre_workout=energy_pre_workout,
    )

    for ex in exercises:
        workouts_db.add_execution(
            session_id=session_id,
            exercise_id=ex["exercise_id"],
            equipment_brand=ex["equipment_brand"],
            equipment_model=ex["equipment_model"],
        )

    return session_id


def get_user_templates(user_id: int):
    """Return all templates for a user, newest first."""
    return templates_db.get_templates_for_user(user_id)


def get_template_exercises(template_id: int):
    """Return the exercise list for a template, in order."""
    return templates_db.get_template_exercises(template_id)


def delete_template(template_id: int, user_id: int) -> None:
    """
    Delete a template. Verifies ownership before deleting to prevent
    one user from deleting another's template.
    """
    template = templates_db.get_template(template_id)
    if template is None:
        raise WorkoutError("Template not found.")
    if template["user_id"] != user_id:
        raise WorkoutError("You don't own this template.")
    templates_db.delete_template(template_id)
