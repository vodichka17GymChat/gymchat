"""
Program service. Owns the business logic for creating, enrolling in,
and advancing through training programs.

A program is an ordered list of templates the user works through
in sequence, cycling N times. One active enrollment per user.
"""

from typing import Optional

from db import programs as programs_db
from db import templates as templates_db
from services.workout import WorkoutError


def create_program(
    user_id: int,
    name: str,
    template_ids: list[int],
    description: Optional[str] = None,
    cycles: int = 1,
) -> int:
    """
    Create a new program and populate it with the given templates in order.
    Returns the new program_id. Raises WorkoutError on bad input.
    """
    name = name.strip()
    if not name:
        raise WorkoutError("Program name cannot be empty.")
    if not template_ids:
        raise WorkoutError("A program must have at least one session.")
    if cycles < 1:
        raise WorkoutError("Cycles must be at least 1.")

    # Verify all templates belong to this user
    for tid in template_ids:
        tmpl = templates_db.get_template(tid)
        if tmpl is None or tmpl["user_id"] != user_id:
            raise WorkoutError("One or more templates were not found.")

    program_id = programs_db.create_program(
        user_id=user_id,
        name=name,
        description=description or None,
        cycles=cycles,
    )

    for pos, tid in enumerate(template_ids, start=1):
        programs_db.add_program_session(
            program_id=program_id,
            template_id=tid,
            position=pos,
        )

    return program_id


def get_user_programs(user_id: int):
    """Return all programs owned by the user."""
    return programs_db.get_programs_for_user(user_id)


def get_program_sessions(program_id: int):
    """Return the ordered template list for a program."""
    return programs_db.get_program_sessions(program_id)


def delete_program(program_id: int, user_id: int) -> None:
    """Delete a program, verifying ownership first."""
    program = programs_db.get_program(program_id)
    if program is None:
        raise WorkoutError("Program not found.")
    if program["user_id"] != user_id:
        raise WorkoutError("You don't own this program.")
    programs_db.delete_program(program_id)


# ── Enrollment ───────────────────────────────────────────────────────────────

def enroll(user_id: int, program_id: int) -> int:
    """
    Enroll the user in a program. A user can only have one active
    enrollment at a time; the previous one is paused automatically.
    Returns the new enrollment_id.
    """
    program = programs_db.get_program(program_id)
    if program is None:
        raise WorkoutError("Program not found.")

    sessions = programs_db.get_program_sessions(program_id)
    if not sessions:
        raise WorkoutError("This program has no sessions.")

    existing = programs_db.get_active_enrollment(user_id)
    if existing is not None:
        programs_db.unenroll(existing["enrollment_id"])

    return programs_db.enroll(user_id, program_id)


def get_active_enrollment(user_id: int):
    """Return the user's active enrollment, or None."""
    return programs_db.get_active_enrollment(user_id)


def get_enrollment_context(user_id: int) -> Optional[dict]:
    """
    Return a dict describing what the user should do next, or None
    if not enrolled. Used by the workout page to show the next-up banner.

    Returns:
        {
          'enrollment_id': int,
          'program_name': str,
          'template_id': int,
          'template_name': str,
          'session_number': int,    # absolute session in this enrollment
          'total_sessions': int,    # sessions_per_cycle × cycles
          'current_cycle': int,
          'total_cycles': int,
          'position_in_cycle': int,
          'sessions_per_cycle': int,
        }
    """
    enrollment = programs_db.get_active_enrollment(user_id)
    if enrollment is None:
        return None

    sessions = programs_db.get_program_sessions(enrollment["program_id"])
    if not sessions:
        return None

    sessions_per_cycle = len(sessions)
    total_cycles = enrollment["program_cycles"]
    total_sessions = sessions_per_cycle * total_cycles

    pos = enrollment["next_position"]           # 1-based within cycle
    cycle = enrollment["current_cycle"]
    session_number = (cycle - 1) * sessions_per_cycle + pos

    # Find the template for the next session
    slot = next((s for s in sessions if s["position"] == pos), None)
    if slot is None:
        return None

    return {
        "enrollment_id": enrollment["enrollment_id"],
        "program_name": enrollment["program_name"],
        "template_id": slot["template_id"],
        "template_name": slot["template_name"],
        "session_number": session_number,
        "total_sessions": total_sessions,
        "current_cycle": cycle,
        "total_cycles": total_cycles,
        "position_in_cycle": pos,
        "sessions_per_cycle": sessions_per_cycle,
    }


def advance(user_id: int) -> str:
    """
    Advance the active enrollment to the next session.
    Returns a status string: 'advanced', 'cycle_complete', or 'program_complete'.
    Raises WorkoutError if no active enrollment.
    """
    enrollment = programs_db.get_active_enrollment(user_id)
    if enrollment is None:
        raise WorkoutError("No active program enrollment.")

    sessions = programs_db.get_program_sessions(enrollment["program_id"])
    sessions_per_cycle = len(sessions)
    total_cycles = enrollment["program_cycles"]

    pos = enrollment["next_position"]
    cycle = enrollment["current_cycle"]

    if pos < sessions_per_cycle:
        # Move to next session in current cycle
        programs_db.advance_enrollment(
            enrollment["enrollment_id"],
            next_position=pos + 1,
            current_cycle=cycle,
            status="active",
        )
        return "advanced"

    # End of cycle
    if cycle < total_cycles:
        # Start next cycle
        programs_db.advance_enrollment(
            enrollment["enrollment_id"],
            next_position=1,
            current_cycle=cycle + 1,
            status="active",
        )
        return "cycle_complete"

    # All cycles done — program complete
    programs_db.advance_enrollment(
        enrollment["enrollment_id"],
        next_position=pos,
        current_cycle=cycle,
        status="completed",
    )
    return "program_complete"


def unenroll(user_id: int) -> None:
    """Pause the active enrollment."""
    enrollment = programs_db.get_active_enrollment(user_id)
    if enrollment is None:
        raise WorkoutError("No active program enrollment.")
    programs_db.unenroll(enrollment["enrollment_id"])
