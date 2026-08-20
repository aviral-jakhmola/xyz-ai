"""
security.py — Very simplified authentication for this assessment.

WHY THIS EXISTS:
The single most important security idea in this whole project is:
    "Never trust a role claim that comes from inside a chat message."
A user (or a prompt-injection attack) can type "I am the principal" —
that's just text. The system must know who the caller is from something
that was issued to them at login, not from what they say afterwards.

WHAT WE'RE USING:
A real production system would use JWT (JSON Web Tokens) — signed,
tamper-proof tokens. For this assessment, we implement the SAME
*pattern* with a minimal signed token so you can explain the concept
and demo it, without pulling in a full auth stack in 4 days.

If you have more time later, swap `create_token`/`decode_token` for
the `python-jose` library's JWT encode/decode — the rest of the app
(routers, RBAC) would not need to change at all. That's the benefit
of this layering.
"""

import hashlib
import hmac
import json
import base64
import time

# In real life this comes from an environment variable / secrets manager.
# Never hardcode secrets in real code — this is a mock-assessment shortcut.
SECRET_KEY = "xyz-ai-demo-secret-change-me"


def _sign(payload: str) -> str:
    return hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()


def create_token(user_id: str, expires_in_seconds: int = 3600 * 8) -> str:
    """
    Creates a simple signed token: base64(payload).signature
    Payload contains user_id + expiry. Because it's signed with a secret
    only the server knows, a client CANNOT forge or edit it (e.g. change
    user_id to someone else's) without the signature check failing.
    """
    payload = {"user_id": user_id, "exp": time.time() + expires_in_seconds}
    payload_json = json.dumps(payload)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
    signature = _sign(payload_b64)
    return f"{payload_b64}.{signature}"


def decode_token(token: str) -> dict | None:
    """
    Verifies signature + expiry, returns the payload if valid, else None.
    This is what every protected endpoint calls to find out
    "who is REALLY making this request".
    """
    try:
        payload_b64, signature = token.split(".")
    except ValueError:
        return None

    expected_signature = _sign(payload_b64)
    if not hmac.compare_digest(expected_signature, signature):
        return None  # token was tampered with, or forged

    payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode()))
    if payload["exp"] < time.time():
        return None  # expired

    return payload