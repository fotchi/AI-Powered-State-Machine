from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..auth import create_access_token, get_current_user, verify_password
from ..database import get_user_by_email, log_audit_event
from ..schemas import LoginRequest, LoginResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    user = get_user_by_email(payload.email.strip().lower())
    if user is None or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(401, "Incorrect email or password")

    token = create_access_token(user["email"], user["role"])
    log_audit_event(None, "user_login", f"{user['email']} signed in")
    return LoginResponse(
        access_token=token,
        user=UserResponse(email=user["email"], full_name=user["full_name"], role=user["role"]),
    )


@router.post("/logout")
def logout(user: dict = Depends(get_current_user)):
    # JWTs are stateless -- there is nothing server-side to invalidate here.
    # The frontend discards the token; this endpoint exists mainly to give
    # the sign-out action an auditable server round-trip.
    log_audit_event(None, "user_logout", f"{user['email']} signed out")
    return {"status": "ok"}


@router.get("/me", response_model=UserResponse)
def me(user: dict = Depends(get_current_user)):
    return UserResponse(email=user["email"], full_name=user["full_name"], role=user["role"])
