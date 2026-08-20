"""
chat.py — the main chat endpoint the frontend calls.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.conversation import get_or_create_session, reset_session
from app.services.ai.gemini_client import send_message

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    language: str = "English"


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest, current_user: dict = Depends(get_current_user)):
    session = get_or_create_session(current_user, body.language)
    try:
        reply = await run_in_threadpool(send_message, session, body.message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")
    return ChatResponse(reply=reply)


@router.post("/reset")
def reset(current_user: dict = Depends(get_current_user)):
    reset_session(current_user)
    return {"status": "reset"}