"""
deps.py — FastAPI "dependencies".

CONCEPT: FastAPI's dependency injection.
Instead of every endpoint manually parsing headers and checking tokens,
you write a function once (get_current_user) and FastAPI runs it
automatically before your endpoint code, injecting the result as an
argument. If it raises an HTTPException, the endpoint never even runs.

This is what makes routes "protected": you add
    current_user: dict = Depends(get_current_user)
to any endpoint's signature, and authentication is enforced for free,
consistently, everywhere — instead of everyone remembering to check.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.security import decode_token
from app.database import get_user

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Reads the Authorization: Bearer <token> header,
    validates it, and returns the corresponding user.
    """

    token = credentials.credentials

    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = get_user(payload["user_id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user