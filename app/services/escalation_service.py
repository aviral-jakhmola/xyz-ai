"""
escalation_service.py — mock "connect me to a human" service.

IMPORTANT SPEC REQUIREMENT this enforces:
"The system must not claim that a teacher or school management
representative has been contacted unless the call/request is actually
confirmed by the mock service."

So this function returns a real status. Later, when the AI generates a
reply like "Your call request has been submitted", it must be generated
FROM this function's actual return value — never asserted by the LLM
on its own. We'll enforce that in Day 2 when we wire up Gemini
function-calling: the AI is only allowed to say "submitted" if this
dict says status == "submitted".
"""

from app.core.rbac import can_request_escalation
from app import database


def request_escalation(current_user: dict, target_role: str, reason: str) -> dict:
    if target_role not in ("teacher", "principal", "management"):
        raise ValueError("target_role must be 'teacher', 'principal', or 'management'")

    can_request_escalation(current_user)  # raises PermissionDenied if not allowed

    entry = database.log_escalation(
        requested_by=current_user["id"],
        target_role=target_role,
        reason=reason,
    )
    return entry