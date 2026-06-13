"""User authentication — models, password hashing, token management."""

import hashlib
import secrets
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Boolean
from backend.db.database import Base

TOKEN_EXPIRY_HOURS = 24


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True)
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    display_name = Column(String, default="")
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Hash password with salt. Returns (hash_hex, salt_hex)."""
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200000)
    return h.hex(), salt


def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    h, _ = hash_password(password, salt)
    return h == stored_hash


# In-memory token store
_active_tokens: dict = {}


def create_token(username: str) -> str:
    """Create a session token for a user."""
    token = secrets.token_hex(32)
    _active_tokens[token] = {
        "username": username,
        "issued": datetime.now(timezone.utc),
    }
    return token


def validate_token(token: str) -> str | None:
    """Validate a token and return username if valid, None otherwise."""
    entry = _active_tokens.get(token)
    if not entry:
        return None
    age = (datetime.now(timezone.utc) - entry["issued"]).total_seconds()
    if age > TOKEN_EXPIRY_HOURS * 3600:
        del _active_tokens[token]
        return None
    return entry["username"]


def revoke_token(token: str):
    """Revoke a session token."""
    _active_tokens.pop(token, None)


def seed_default_admin():
    """Create default admin user if no users exist."""
    from backend.db.database import SessionLocal
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        salt = secrets.token_hex(16)
        h, _ = hash_password("admin123", salt)
        db.add(User(
            username="admin",
            password_hash=h,
            salt=salt,
            display_name="系统管理员",
            is_admin=True,
        ))
        db.commit()
    finally:
        db.close()
