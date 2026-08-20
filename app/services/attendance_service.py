"""
attendance_service.py — the ONLY way anything in this app is allowed to
touch attendance data.

Every function here takes `current_user` (the trusted, token-derived
user from deps.py) FIRST, checks RBAC, and only then touches the
database. This is deliberate: it means it is structurally impossible
to call these functions and skip the permission check, because the
check happens inside the function itself, not in some optional
middleware someone could forget to add.
"""

from app.core.rbac import can_view_attendance, can_mark_attendance, PermissionDenied
from app import database


def view_attendance(current_user: dict, student_id: str) -> dict:
    can_view_attendance(current_user, student_id)  # raises PermissionDenied if not allowed

    records = database.get_attendance(student_id)
    percent = database.calculate_attendance_percent(student_id)
    student = database.get_user(student_id)

    return {
        "student_id": student_id,
        "student_name": student["name"] if student else student_id,
        "attendance_percent": percent,
        "records": records,
    }


def mark_attendance(current_user: dict, student_id: str, status: str, on_date: str | None = None) -> dict:
    if status not in ("present", "absent"):
        raise ValueError("status must be 'present' or 'absent'")

    can_mark_attendance(current_user, student_id)  # raises PermissionDenied if not allowed

    record = database.mark_attendance(student_id, status, on_date)
    return {"student_id": student_id, "marked": record}


def school_analytics(current_user: dict) -> dict:
    from app.core.rbac import can_view_school_analytics
    can_view_school_analytics(current_user)  # raises PermissionDenied if not allowed

    return database.school_wide_attendance()