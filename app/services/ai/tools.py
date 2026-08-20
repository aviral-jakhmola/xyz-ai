"""
tools.py — builds Gemini "function calling" tools, bound to the real
authenticated user for this request.

CONCEPT: Gemini function calling.
You give the model a list of Python functions. The model can choose to
call them based on the conversation (e.g. user asks about attendance ->
model decides to call view_attendance). The google-generativeai SDK's
"automatic function calling" handles the back-and-forth for you: it
calls your function, gets the result, and feeds it back to the model to
generate a natural-language reply.

THE IMPORTANT PART: each function below is defined INSIDE
build_tools_for_user(current_user), which means it "closes over"
(captures) current_user. Gemini can pass in a student's NAME, but it
can never pass in a fake user/role — that always comes from the real
authenticated session, not from anything Gemini or the chat text says.
"""

from app import database
from app.core.rbac import PermissionDenied
from app.services import attendance_service, escalation_service


def build_tools_for_user(current_user: dict):
    def _resolve_student_id(student_name: str | None) -> tuple[str | None, dict | None]:
        """Returns (student_id, error_dict). Exactly one will be None."""
        role = current_user["role"]

        if role == "student":
            return current_user["id"], None

        if role == "parent":
            children = current_user.get("children_ids", [])
            if not children:
                return None, {"error": "not_found", "message": "No child linked to this account."}
            if student_name:
                for child_id in children:
                    child = database.get_user(child_id)
                    if child and student_name.lower() in child["name"].lower():
                        return child_id, None
                return None, {"error": "not_found", "message": f"No child named '{student_name}' found on this account."}
            return children[0], None  # default to their (only) child

        # teacher / principal must name the student explicitly
        if not student_name:
            return None, {"error": "missing_info", "message": "Please specify which student by name."}
        target = database.find_user_by_name(student_name)
        if not target or target["role"] != "student":
            return None, {"error": "not_found", "message": f"No student named '{student_name}' found."}
        return target["id"], None

    def view_attendance(student_name: str = "") -> dict:
        """
        Get a student's attendance percentage and recent records.
        If the current user is a student asking about themselves, or a
        parent asking about their only child, student_name can be left empty.
        Otherwise (teacher/principal, or a parent with multiple children),
        provide the student's name.
        """
        student_id, error = _resolve_student_id(student_name or None)
        if error:
            return error
        try:
            return attendance_service.view_attendance(current_user, student_id)
        except PermissionDenied as e:
            return {"error": "permission_denied", "reason": e.reason}

    def mark_attendance(student_name: str, status: str) -> dict:
        """
        Mark a student's attendance as 'present' or 'absent'. Only
        teachers can do this, and only for students in their own class.
        student_name is required. status must be exactly 'present' or 'absent'.
        """
        target = database.find_user_by_name(student_name)
        if not target or target["role"] != "student":
            return {"error": "not_found", "message": f"No student named '{student_name}' found."}
        try:
            return attendance_service.mark_attendance(current_user, target["id"], status)
        except PermissionDenied as e:
            return {"error": "permission_denied", "reason": e.reason}
        except ValueError as e:
            return {"error": "invalid_input", "message": str(e)}

    def view_school_analytics() -> dict:
        """
        Get overall school-wide attendance analytics. Principal/school
        management only.
        """
        try:
            return attendance_service.school_analytics(current_user)
        except PermissionDenied as e:
            return {"error": "permission_denied", "reason": e.reason}

    def request_escalation(target_role: str, reason: str) -> dict:
        """
        Submit a real request to connect the user with a human teacher or
        school management. ONLY call this after the user has explicitly
        confirmed they want to escalate (e.g. said "yes" to your offer).
        target_role must be 'teacher', 'principal', or 'management'.
        Returns the REAL status of the request — only tell the user it
        succeeded if this returns status 'submitted'.
        """
        try:
            return escalation_service.request_escalation(current_user, target_role, reason)
        except PermissionDenied as e:
            return {"error": "permission_denied", "reason": e.reason}
        except ValueError as e:
            return {"error": "invalid_input", "message": str(e)}

    # Only expose tools relevant to this role — an extra defense layer.
    # Even though each tool re-checks RBAC internally, we also avoid even
    # showing irrelevant tools to reduce the model's temptation surface.
    role = current_user["role"]
    if role in ("student", "parent"):
        return [view_attendance, request_escalation]
    if role == "teacher":
        return [view_attendance, mark_attendance]
    if role == "principal":
        return [view_school_analytics]
    return []