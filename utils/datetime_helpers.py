"""
Datetime formatting helpers. Pure functions used across multiple pages.
No Streamlit, no database - safe to use anywhere and easy to test.
"""

from datetime import datetime


def format_datetime(iso_string: str | None) -> str:
    """Turn an ISO timestamp into a friendly 'Apr 27, 2026 · 18:42'."""
    if not iso_string:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%b %d, %Y · %H:%M")
    except ValueError:
        return iso_string


def format_relative(iso_string: str | None) -> str:
    """
    Turn an ISO timestamp into a friendly 'just now', '5 minutes ago',
    '2 hours ago', etc. Falls back to a date format for anything older
    than a month.
    """
    if not iso_string:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_string)
    except ValueError:
        return iso_string

    delta = datetime.now() - dt
    seconds = int(delta.total_seconds())

    if seconds < 30:
        return "just now"
    if seconds < 60:
        return f"{seconds} seconds ago"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"

    days = hours // 24
    if days < 7:
        return f"{days} day{'s' if days != 1 else ''} ago"

    weeks = days // 7
    if weeks < 4:
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"

    return dt.strftime("%b %d, %Y")


def format_duration(start: str | None, end: str | None) -> str:
    """
    Compute the time between two ISO timestamps as 'Xh Ym' (or just 'Ym'
    for sessions under an hour). Returns '—' if either is missing or
    malformed - common while a workout is still in progress.
    """
    if not start or not end:
        return "—"
    try:
        delta = datetime.fromisoformat(end) - datetime.fromisoformat(start)
    except ValueError:
        return "—"

    total_minutes = int(delta.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"


def format_seconds(seconds: int | None) -> str:
    """
    Format a raw seconds count as 'M:SS' or 'Ss'. Used by the rest timer
    and anywhere we display short durations.
    """
    if seconds is None or seconds < 0:
        return "—"
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}" if m > 0 else f"{s}s"
