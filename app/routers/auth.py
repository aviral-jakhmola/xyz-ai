"""
auth.py — mock login.

In a real school ERP, this would check a password / OTP / SSO. For our
mock system, we let the demo "log in" as any of our seed users by ID —
this is fine for an assessment since the point being demonstrated is
what happens AFTER login (RBAC), not the login mechanism itself.

Mention this simplification honestly in your README.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.security import create_token
from app.database import get_user

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    user_id: str  # e.g. "u_parent_sharma" — in a real system this'd be a username/password


class LoginResponse(BaseModel):
    token: str
    user_id: str
    name: str
    role: str


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    user = get_user(body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Unknown user_id")

    token = create_token(user["id"])
    return LoginResponse(token=token, user_id=user["id"], name=user["name"], role=user["role"])