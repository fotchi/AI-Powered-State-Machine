"""
Token-based authentication (JWT) + role-based access control -- per the
Technical Design Document, section 9 ("Security and Technical Best
Practices"): "token-based authentication (e.g., OAuth2 / JWT) at the API
gateway; role-based access control for QA vs. administrative actions."

Two roles: "qa_engineer" (default -- everyday scenario/script/coverage
workflow) and "administrator" (also gets the audit log, see routers/audit.py).
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import get_user_by_email

# In production this MUST be set via env var -- the dev fallback is only
# for zero-config local runs and is logged loudly so it's never mistaken
# for a real secret.
SECRET_KEY = os.environ.get("JWT_SECRET")
if not SECRET_KEY:
    SECRET_KEY = "dev-only-insecure-secret-change-me"
    print("[auth] WARNING: JWT_SECRET not set -- using an insecure development "
          "default. Set the JWT_SECRET environment variable before deploying.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 12 * 60

_bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(email: str, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "role": role, "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token has expired") from None
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid authentication token") from None


def user_from_token(token: str) -> dict[str, Any]:
    payload = decode_access_token(token)
    user = get_user_by_email(payload.get("sub", ""))
    if user is None:
        raise HTTPException(401, "User no longer exists")
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(401, "Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    return user_from_token(credentials.credentials)


def require_admin(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if user["role"] != "administrator":
        raise HTTPException(403, "Administrator role required")
    return user


def user_from_websocket_token(token: str | None) -> dict[str, Any]:
    """WebSockets can't set an Authorization header from browser JS, so the
    stream endpoint takes the token as a query param instead (?token=...)."""
    if not token:
        raise HTTPException(401, "Missing token")
    return user_from_token(token)
