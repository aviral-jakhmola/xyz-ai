"""
tools.py — HTTP endpoints exposing the same functions the AI will later
call as "tools" via Gemini function-calling.

WHY THIS FILE MATTERS FOR DAY 1:
Today's goal is to prove the RBAC system actually works end-to-end
BEFORE we introduce an LLM into the picture at all. If these endpoints
correctly allow/deny based on role using nothing but the token, then on
Day 2 we just point Gemini's function-calling at these same service
functions — we are NOT rebuilding security logic for the AI, we're
reusing it. This is exactly what "authorization at the application/tool
layer" means in the spec.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.rbac import PermissionDenied
from app.services import attendance_service, escalation_service

router = APIRouter(prefix="/tools", tags=["tools"])


def _handle_permission(fn, *args, **kwargs):
    """Small helper: turn PermissionDenied into a proper HTTP 403."""
    try:
        return fn(*args, **kwargs)
    except PermissionDenied as e:
        raise HTTPException(status_code=403, detail=e.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/attendance/{student_id}")
def get_attendance(student_id: str, current_user: dict = Depends(get_current_user)):
    """Use case: Student views own attendance / Parent views child's attendance."""
    return _handle_permission(attendance_service.view_attendance, current_user, student_id)


class MarkAttendanceRequest(BaseModel):
    student_id: str
    status: str  # "present" | "absent"
    date: str | None = None


@router.post("/attendance/mark")
def mark_attendance(body: MarkAttendanceRequest, current_user: dict = Depends(get_current_user)):
    """Use case: Teacher marks attendance."""
    return _handle_permission(
        attendance_service.mark_attendance, current_user, body.student_id, body.status, body.date
    )


@router.get("/analytics/attendance")
def school_analytics(current_user: dict = Depends(get_current_user)):
    """Use case: Principal views overall school attendance analytics."""
    return _handle_permission(attendance_service.school_analytics, current_user)


class EscalationRequest(BaseModel):
    target_role: str  # "teacher" | "principal" | "management"
    reason: str


@router.post("/escalation/request")
def request_escalation(body: EscalationRequest, current_user: dict = Depends(get_current_user)):
    """Use case: Student/Parent escalates to a real teacher or management."""
    return _handle_permission(
        escalation_service.request_escalation, current_user, body.target_role, body.reason
    )