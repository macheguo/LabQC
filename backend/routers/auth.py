"""Auth router — login, logout, session check, user management (admin)."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.auth import (
    User,
    hash_password,
    verify_password,
    create_token,
    validate_token,
    revoke_token,
    seed_default_admin,
)
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Pydantic models ─────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    username: str
    display_name: str
    is_admin: bool

class MeResponse(BaseModel):
    username: str
    display_name: str
    is_admin: bool

class UserInfo(BaseModel):
    username: str
    display_name: str
    is_admin: bool
    is_active: bool
    created_at: str | None = None
    last_login: str | None = None

class CreateUserRequest(BaseModel):
    username: str
    password: str
    display_name: str = ""
    is_admin: bool = False

class UpdateUserRequest(BaseModel):
    display_name: str | None = None
    is_admin: bool | None = None
    is_active: bool | None = None

class ResetPasswordRequest(BaseModel):
    new_password: str


# ── Helpers ─────────────────────────────────────────────────────────────

def _get_current_user(token: str, db: Session) -> User:
    """Validate token and return user, or raise 401."""
    username = validate_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user = db.query(User).filter_by(username=username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user

def _get_admin(token: str, db: Session) -> User:
    """Like _get_current_user but also requires admin flag."""
    user = _get_current_user(token, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="仅管理员可执行此操作")
    return user

def _serialize_user(u: User) -> dict:
    return {
        "username": u.username,
        "display_name": u.display_name or "",
        "is_admin": u.is_admin,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "last_login": u.last_login.isoformat() if u.last_login else None,
    }


# ── Public endpoints ────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return a session token."""
    if db.query(User).count() == 0:
        seed_default_admin()
    user = db.query(User).filter_by(username=body.username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(body.password, user.salt, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    token = create_token(user.username)
    return LoginResponse(
        token=token,
        username=user.username,
        display_name=user.display_name or user.username,
        is_admin=user.is_admin,
    )

@router.post("/logout")
def logout(token: str):
    """Revoke a session token."""
    revoke_token(token)
    return {"ok": True}

@router.get("/me", response_model=MeResponse)
def me(token: str, db: Session = Depends(get_db)):
    """Return current user info from token."""
    user = _get_current_user(token, db)
    return MeResponse(
        username=user.username,
        display_name=user.display_name or user.username,
        is_admin=user.is_admin,
    )


# ── Admin-only user management ──────────────────────────────────────────

@router.get("/users")
def list_users(token: str, db: Session = Depends(get_db)):
    """List all users (admin only)."""
    _get_admin(token, db)
    users = db.query(User).order_by(User.created_at).all()
    return [_serialize_user(u) for u in users]

@router.post("/users")
def create_user(body: CreateUserRequest, token: str, db: Session = Depends(get_db)):
    """Create a new user (admin only)."""
    _get_admin(token, db)
    if db.query(User).filter_by(username=body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    h, salt = hash_password(body.password)
    user = User(
        username=body.username,
        password_hash=h,
        salt=salt,
        display_name=body.display_name or body.username,
        is_admin=body.is_admin,
    )
    db.add(user)
    db.commit()
    return _serialize_user(user)

@router.put("/users/{username}")
def update_user(username: str, body: UpdateUserRequest, token: str, db: Session = Depends(get_db)):
    """Update user fields (admin only)."""
    _get_admin(token, db)
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.is_admin is not None:
        user.is_admin = body.is_admin
    if body.is_active is not None:
        user.is_active = body.is_active
    db.commit()
    return _serialize_user(user)

@router.delete("/users/{username}")
def delete_user(username: str, token: str, db: Session = Depends(get_db)):
    """Delete a user (admin only). Cannot delete self."""
    admin = _get_admin(token, db)
    if username == admin.username:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    # Revoke any active tokens for deleted user
    to_revoke = [t for t, e in list(_get_active_tokens_dict().items()) if e["username"] == username]
    for t in to_revoke:
        revoke_token(t)
    return {"ok": True}

@router.post("/users/{username}/reset-password")
def reset_password(username: str, body: ResetPasswordRequest, token: str, db: Session = Depends(get_db)):
    """Reset a user's password (admin only)."""
    _get_admin(token, db)
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    h, salt = hash_password(body.new_password)
    user.password_hash = h
    user.salt = salt
    db.commit()
    # Revoke all tokens for this user so old sessions are invalid
    to_revoke = [t for t, e in list(_get_active_tokens_dict().items()) if e["username"] == username]
    for t in to_revoke:
        revoke_token(t)
    return {"ok": True}


# ── Internal accessor for delete/reset to access active tokens ──────────

def _get_active_tokens_dict() -> dict:
    """Return reference to the in-memory token store."""
    import backend.auth as auth_mod
    return auth_mod._active_tokens
