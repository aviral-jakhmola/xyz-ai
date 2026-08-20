import os
import time
import re
from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEYS
from app.services.ai.personas import get_persona_prompt
from app.services.ai.tools import build_tools_for_user

MODEL_NAME = "gemini-3.5-flash-lite"

# Set to True while building UI; set to False for final demo/recording with fresh keys
MOCK_AI_MODE = os.getenv("MOCK_AI_MODE", "false").lower() == "true"

_CLIENT_CACHE = {}


def _get_client(api_key: str) -> genai.Client:
    if api_key not in _CLIENT_CACHE:
        _CLIENT_CACHE[api_key] = genai.Client(api_key=api_key)
    return _CLIENT_CACHE[api_key]


class RotatingGeminiChat:
    def __init__(self, current_user: dict, language: str = "English"):
        self.current_user = current_user
        self.language = language
        self.key_index = 0
        self.keys = [k for k in GEMINI_API_KEYS if k]
        self.history = []

        if not MOCK_AI_MODE and not self.keys:
            raise ValueError("No Gemini API keys found in GEMINI_API_KEYS.")

        if not MOCK_AI_MODE:
            self._init_session()

    def _get_current_key(self) -> str:
        return self.keys[self.key_index % len(self.keys)]

    def _init_session(self):
        persona_prompt = get_persona_prompt(self.current_user["role"])
        persona_prompt += f"\nRespond in this language: {self.language}.\n"
        persona_prompt += f"\nThe user's name is {self.current_user['name']}.\n"

        tools = build_tools_for_user(self.current_user)

        config = types.GenerateContentConfig(
            system_instruction=persona_prompt,
            tools=tools if tools else None,
            temperature=0.1,
            max_output_tokens=350,
        )

        client = _get_client(self._get_current_key())
        self.chat = client.chats.create(model=MODEL_NAME, config=config)

    def _rotate_key_and_rebuild(self):
        self.key_index = (self.key_index + 1) % len(self.keys)
        self._init_session()
        for turn in self.history:
            if turn["role"] == "user":
                try:
                    self.chat.send_message(turn["content"])
                except Exception:
                    pass

    def send_message(self, message: str) -> str:
        # Mock mode fallback to bypass quotas during UI development
        if MOCK_AI_MODE:
            role = self.current_user.get("role", "student")
            name = self.current_user.get("name", "User")
            msg = message.lower()

            if "attendance" in msg:
                return (
                    f"Here is the attendance information for **{name}**:\n\n"
                    f"* **Overall Attendance:** 75%\n"
                    f"* **Recent Records:** Aug 10 (Present), Aug 11 (Present), Aug 12 (Absent), Aug 13 (Present)"
                )
            if "analytics" in msg and role == "principal":
                return (
                    "**School-Wide Attendance Overview**:\n\n"
                    "* **Total Students:** 120\n"
                    "* **Average Daily Attendance:** 88.5%\n"
                    "* **Lowest Attendance Class:** Grade 10-A (78%)"
                )
            if "escalat" in msg or "principal" in msg or "teacher" in msg:
                return (
                    f"Hello {name}. Would you like me to formally submit an escalation request "
                    f"to connect you with school staff? Please reply with **yes** to confirm."
                )
            if msg.strip() in ["yes", "confirm", "proceed", "yes, please"]:
                return "I have submitted your escalation request. A staff member will reach out to you shortly."

            return f"Hello {name}! I received your query: *\"{message}\"*. As a {role}, let me know what assistance you need."

        # Live Gemini API generation logic
        attempts = 0
        max_attempts = max(len(self.keys), 1)

        while attempts < max_attempts:
            try:
                response = self.chat.send_message(message)
                self.history.append({"role": "user", "content": message})
                self.history.append({"role": "assistant", "content": response.text})
                return response.text
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    attempts += 1
                    if len(self.keys) > 1 and attempts < max_attempts:
                        self._rotate_key_and_rebuild()
                        continue
                    else:
                        match = re.search(r"retry in (\d+(\.\d+)?)s", err_str)
                        delay = float(match.group(1)) if match else 10.0
                        if delay <= 12:
                            time.sleep(delay + 1)
                            continue
                raise e

        raise RuntimeError("All configured Gemini API keys exceeded quota limits.")


def create_chat_session(current_user: dict, language: str = "English") -> RotatingGeminiChat:
    return RotatingGeminiChat(current_user=current_user, language=language)


def send_message(session: RotatingGeminiChat, message: str) -> str:
    return session.send_message(message)