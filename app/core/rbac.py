"""
rbac.py — Role-Based Access Control rules.

THE CENTRAL IDEA OF THIS WHOLE PROJECT:
The LLM (Gemini) is allowed to be wrong, tricked, or confused. It might
be prompt-injected into "believing" the user is a teacher. That is fine,
AS LONG AS this file is the actual gatekeeper before any data moves or
any action happens. Every function here answers one yes/no question
using ONLY trusted data (the token-derived user, and our database's
relationships) — never anything the user typed in chat.

Pattern: every check function either returns normally (allowed) or
raises PermissionError with a clear reason (denied). Callers in
services/ catch that and turn it into an HTTP 403.
"""

from app.database import get_user


class PermissionDenied(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def require_role(current_user: dict, allowed_roles: list[str]):
    if current_user["role"] not in allowed_roles:
        raise PermissionDenied(
            f"Role '{current_user['role']}' is not permitted to perform this action. "
            f"Allowed roles: {allowed_roles}."
        )


def can_view_attendance(current_user: dict, student_id: str):
    """
    - Student can view only their OWN attendance.
    - Parent can view only THEIR CHILD's attendance (checked via the
      children_ids link in the database — not via anything the user typed).
    - Teacher can view attendance for students in their class.
    - Principal can view anyone's (school-wide).
    """
    role = current_user["role"]

    if role == "student":
        if current_user["id"] != student_id:
            raise PermissionDenied("Students may only view their own attendance.")
        return

    if role == "parent":
        if student_id not in current_user.get("children_ids", []):
            raise PermissionDenied("Parents may only view their own child's attendance.")
        return

    if role == "teacher":
        target = get_user(student_id)
        if not target or target.get("class_id") not in current_user.get("class_ids", []):
            raise PermissionDenied("Teachers may only view attendance for their own class.")
        return

    if role == "principal":
        return  # full access

    raise PermissionDenied("Unknown role.")


def can_mark_attendance(current_user: dict, student_id: str):
    """
    Only teachers can mark attendance, and only for students in a class
    they teach. Students, parents, and even the principal are NOT allowed
    to directly mark attendance per the required use cases.
    """
    require_role(current_user, ["teacher"])
    target = get_user(student_id)
    if not target or target.get("class_id") not in current_user.get("class_ids", []):
        raise PermissionDenied("Teachers may only mark attendance for their own class.")


def can_view_school_analytics(current_user: dict):
    """Only the principal (school management) gets aggregate analytics."""
    require_role(current_user, ["principal"])


def can_request_escalation(current_user: dict):
    """
    Students and parents are the ones who escalate to a real human
    per the spec. (Teachers/principal ARE the humans being escalated to.)
    """
    require_role(current_user, ["student", "parent"])