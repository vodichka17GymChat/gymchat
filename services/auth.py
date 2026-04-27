"""
Authentication service. Handles signup and login by sitting on top of
db/users.py. Owns password hashing, input validation, and the rules
about what makes a valid registration.

The UI calls this module - never db/users.py directly.
"""

import hashlib
import secrets
import sqlite3
from typing import Optional

from db import users as users_db
from utils.validators import (
    normalize_email,
    validate_email,
    validate_password,
)


# scrypt parameters. These are the OWASP-recommended values for
# interactive logins - secure but fast enough not to feel sluggish.
_SCRYPT_N = 2 ** 14   # CPU/memory cost
_SCRYPT_R = 8         # block size
_SCRYPT_P = 1         # parallelization
_SCRYPT_DKLEN = 64    # derived key length in bytes
_SALT_BYTES = 16      # 128 bits of salt per user


# ============================================================
# Custom exception for clean error messaging
# ============================================================

class AuthError(Exception):
    """Raised when authentication or registration fails for a known reason."""
    pass


# ============================================================
# Password hashing
# ============================================================

def _hash_password(password: str, salt: str) -> str:
    """
    Hash a password with scrypt using the given salt. Returns the hash
    as a hex string. Same password + same salt always produces the same
    hash, which is how we verify logins.
    """
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt),
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_DKLEN,
    )
    return derived.hex()


def _generate_salt() -> str:
    """Generate a fresh random salt as a hex string. One per user."""
    return secrets.token_hex(_SALT_BYTES)


# ============================================================
# Public API: register and login
# ============================================================

def register_user(
    email: str,
    password: str,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    training_experience_months: Optional[int] = None,
    fitness_level: Optional[str] = None,
    athlete_type: Optional[str] = None,
    primary_goal: Optional[str] = None,
) -> int:
    """
    Register a new user. Returns the new user_id on success.
    Raises AuthError with a user-friendly message on failure.
    """
    # 1. Validate inputs
    email_ok, email_err = validate_email(email)
    if not email_ok:
        raise AuthError(email_err)

    pw_ok, pw_err = validate_password(password)
    if not pw_ok:
        raise AuthError(pw_err)

    # 2. Normalize and check for duplicates
    email_norm = normalize_email(email)
    if users_db.get_user_by_email(email_norm) is not None:
        raise AuthError("An account with this email already exists.")

    # 3. Hash the password with a fresh salt
    salt = _generate_salt()
    password_hash = _hash_password(password, salt)

    # 4. Insert. The IntegrityError catch is a backstop in case two
    #    signups race - get_user_by_email above already covers the
    #    common case.
    try:
        return users_db.create_user(
            email=email_norm,
            password_hash=password_hash,
            password_salt=salt,
            age=age,
            gender=gender,
            height_cm=height_cm,
            weight_kg=weight_kg,
            training_experience_months=training_experience_months,
            fitness_level=fitness_level,
            athlete_type=athlete_type,
            primary_goal=primary_goal,
        )
    except sqlite3.IntegrityError:
        raise AuthError("An account with this email already exists.")


def login(email: str, password: str) -> int:
    """
    Verify credentials. Returns the user_id on success.
    Raises AuthError on failure - same message regardless of whether
    the email exists, so attackers can't enumerate valid accounts.
    """
    if not email or not password:
        raise AuthError("Invalid email or password.")

    email_norm = normalize_email(email)
    user = users_db.get_user_by_email(email_norm)

    if user is None:
        raise AuthError("Invalid email or password.")

    expected_hash = _hash_password(password, user["password_salt"])

    # Constant-time comparison to defeat timing attacks
    if not secrets.compare_digest(expected_hash, user["password_hash"]):
        raise AuthError("Invalid email or password.")

    return user["user_id"]