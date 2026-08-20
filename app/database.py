"""
database.py — Mock "database" for XYZ AI.

In a real school ERP this would be Postgres/MySQL. For this assessment we
fake it with plain Python dicts/lists held in memory. This is completely
normal for a mock-API assessment — the important part is that our RBAC
and service layers are written as if this WERE a real database, so
swapping this file for real DB calls later wouldn't change anything else.
"""

from datetime import date

# ---------------------------------------------------------------------
# USERS
# Every user has a role. Roles are the backbone of our RBAC system.
# Note: parents are linked to their children via `children_ids`.
# This link is what lets us enforce "a parent can only see THEIR child's
# attendance" in code, rather than trusting whatever the user/LLM says.
# ---------------------------------------------------------------------
USERS = {
    "u_student_rahul": {
        "id": "u_student_rahul",
        "name": "Rahul Sharma",
        "role": "student",
        "class_id": "c_10a",
    },
    "u_student_anita": {
        "id": "u_student_anita",
        "name": "Anita Verma",
        "role": "student",
        "class_id": "c_10a",
    },
    "u_parent_sharma": {
        "id": "u_parent_sharma",
        "name": "Mr. Sharma",
        "role": "parent",
        "children_ids": ["u_student_rahul"],
    },
    "u_teacher_mehta": {
        "id": "u_teacher_mehta",
        "name": "Ms. Mehta",
        "role": "teacher",
        "class_ids": ["c_10a"],
    },
    "u_principal_rao": {
        "id": "u_principal_rao",
        "name": "Dr. Rao",
        "role": "principal",
    },
}

# ---------------------------------------------------------------------
# ATTENDANCE RECORDS
# Keyed by student_id -> list of {date, status}
# ---------------------------------------------------------------------
ATTENDANCE = {
    "u_student_rahul": [
        {"date": "2026-08-10", "status": "present"},
        {"date": "2026-08-11", "status": "present"},
        {"date": "2026-08-12", "status": "absent"},
        {"date": "2026-08-13", "status": "present"},
    ],
    "u_student_anita": [
        {"date": "2026-08-10", "status": "present"},
        {"date": "2026-08-11", "status": "present"},
        {"date": "2026-08-12", "status": "present"},
        {"date": "2026-08-13", "status": "present"},
    ],
}

# ---------------------------------------------------------------------
# ESCALATION LOG — mock record of "calls" requested to teachers/management
# ---------------------------------------------------------------------
ESCALATIONS = []


def get_user(user_id: str):
    return USERS.get(user_id)


def get_attendance(student_id: str):
    return ATTENDANCE.get(student_id, [])


def mark_attendance(student_id: str, status: str, on_date: str | None = None):
    on_date = on_date or str(date.today())
    records = ATTENDANCE.setdefault(student_id, [])
    records.append({"date": on_date, "status": status})
    return records[-1]


def calculate_attendance_percent(student_id: str) -> float:
    records = ATTENDANCE.get(student_id, [])
    if not records:
        return 0.0
    present = sum(1 for r in records if r["status"] == "present")
    return round((present / len(records)) * 100, 1)


def school_wide_attendance() -> dict:
    """Principal-level analytics across all students."""
    all_students = [u for u in USERS.values() if u["role"] == "student"]
    per_student = {
        s["id"]: calculate_attendance_percent(s["id"]) for s in all_students
    }
    overall = round(sum(per_student.values()) / len(per_student), 1) if per_student else 0.0
    return {"overall_percent": overall, "per_student": per_student}


def log_escalation(requested_by: str, target_role: str, reason: str) -> dict:
    """
    Mock 'call/support request' service. In reality this might hit a
    Twilio API or an internal ticketing system. We simulate success.
    """
    entry = {
        "id": f"esc_{len(ESCALATIONS) + 1}",
        "requested_by": requested_by,
        "target_role": target_role,
        "reason": reason,
        "status": "submitted",  # a real integration might sometimes fail
    }
    ESCALATIONS.append(entry)
    return entry

def find_user_by_name(name: str):
    """
    Fuzzy name lookup so the AI can resolve 'Rahul' -> u_student_rahul
    from natural language, without the chat needing to know internal IDs.
    """
    name_lower = name.strip().lower()
    for user in USERS.values():
        if name_lower in user["name"].lower():
            return user
    return None