# XYZ AI — Multi-Role School Assistant

An AI assistant for a school ERP system that adapts to four user roles — **student, parent, teacher, principal** — each with a distinct persona and strictly enforced permissions. Built with **FastAPI** (backend) and **React** (frontend), powered by **Gemini** for natural-language understanding and function calling.

## Why this project is different

Most chatbot demos let the AI decide what a user is "allowed" to do. Here, the AI never makes that decision. Gemini can *understand* what a user is asking for and *propose* a tool to call — but every tool call closes over the authenticated user from their signed token, and the backend independently re-checks role permissions before anything executes. A student asking the assistant to mark their own attendance gets a `403 Forbidden` from the server, regardless of how the request is phrased. This is the core architectural principle of the project: **the LLM proposes, the backend disposes.**

## Features

- **Role-based access control (RBAC)** — enforced server-side, independent of chat input
- **Persona-specific AI behavior** — each role gets a distinct system prompt and tone
- **Gemini function calling** — the AI can retrieve real data (e.g. attendance) via tools, not guesswork
- **Multi-turn memory** — conversations persist context across messages, isolated per user
- **Escalation workflow** — sensitive actions require explicit confirmation before executing
- **11-language support** — English, Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Punjabi, Kannada, Malayalam, Urdu
- **Voice input/output** — browser-based speech-to-text and text-to-speech
- **Animated AI avatar** — reflects assistant state (idle / thinking / listening / speaking)
- **Security-transparent UI** — the frontend visualizes real backend permission state, it doesn't fake it

## Architecture

```
frontend/          React + Vite + Tailwind
  src/
    App.jsx         Main chat UI, session/voice state
    components/      Avatar, PersonaSwitcher, PermissionPanel

app/                FastAPI backend
  core/
    rbac.py          Role → permission mapping, enforced independently of the LLM
    conversation.py  Per-user, per-language session store
  routers/
    chat.py          /chat endpoint
  services/ai/
    gemini_client.py Gemini integration, function-calling, persona injection
    personas.py      Role-specific system prompts
    tools.py         Tool definitions the LLM can call
```

## Setup

**Backend**
```bash
cd xyz-ai
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env        # add your Gemini API key
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd xyz-ai/frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/auth`, `/chat`, and `/tools` to the backend at `http://localhost:8000`.

## Demo accounts (mock auth)

| Name | Role | Can do |
|---|---|---|
| Rahul Sharma | Student | View own attendance, request escalation |
| Mr. Sharma | Parent | View child's attendance, request escalation |
| Ms. Mehta | Teacher | View + mark attendance, request escalation |
| Dr. Rao | Principal | View attendance, view school-wide analytics, request escalation |

No password needed — select a persona from the sidebar to switch roles.

## Verifying the security model

1. Log in as **Rahul Sharma (student)**
2. Ask the assistant to mark attendance for the class
3. The backend rejects the underlying tool call with `403 Forbidden` — the RBAC panel in the sidebar shows `mark_attendance` as **Blocked** for this role
4. Switch to **Ms. Mehta (teacher)** and repeat — the same action now succeeds, because the backend permission check (not the AI) allows it

## Tech stack

- **Backend:** FastAPI, Pydantic, custom HMAC-signed token auth
- **AI:** Google `google-genai` SDK, Gemini (function calling)
- **Frontend:** React, Vite, Tailwind CSS, `react-markdown`, `lucide-react`
- **Voice:** Browser-native `SpeechRecognition` / `SpeechSynthesis` APIs (no external service required)