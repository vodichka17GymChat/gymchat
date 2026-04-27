"""
Lightweight input validators. Each function returns (is_valid, error_message).
Pure functions - no database access, no Streamlit. Easy to test in isolation.
"""

import re

# Basic email shape check. Not RFC-perfect, but rejects obvious garbage.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MIN_PASSWORD_LENGTH = 8


def validate_email(email: str) -> tuple[bool, str]:
    """Check that the email looks well-formed."""
    if not email or not email.strip():
        return False, "Email is required."
    if not _EMAIL_RE.match(email.strip()):
        return False, "Please enter a valid email address."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Check that the password meets minimum strength requirements."""
    if not password:
        return False, "Password is required."
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    return True, ""


def normalize_email(email: str) -> str:
    """
    Standardize email for storage and lookup. Stripped of whitespace
    and lowercased so 'Foo@Bar.com ' and 'foo@bar.com' are treated as
    the same account.
    """
    return email.strip().lower()