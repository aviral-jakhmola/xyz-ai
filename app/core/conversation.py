"""
conversation.py — in-memory conversation session store.

CONCEPT: Gemini's ChatSession object holds the conversation history
internally. To support multi-turn conversations ("maintain conversation
context" per the spec), we need to reuse the SAME ChatSession across
multiple HTTP requests — HTTP itself is stateless, so we keep a
server-side dict mapping user_id -> ChatSession.

For a real production app you'd use Redis (with expiry) instead of a
plain Python dict, so it survives server restarts and scales across
multiple server processes. Documented as a known simplification.
"""

from app.services.ai.gemini_client import create_chat_session, send_message

# user_id -> gemini ChatSession object
_SESSIONS: dict = {}


def get_or_create_session(current_user: dict, language: str = "English"):
    key = f"{current_user['id']}:{language}"
    if key not in _SESSIONS:
        _SESSIONS[key] = create_chat_session(current_user, language)
    return _SESSIONS[key]

def reset_session(current_user: dict):
    _SESSIONS.pop(current_user["id"], None)