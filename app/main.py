"""
main.py — the FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs for FastAPI's auto-generated
interactive API docs (Swagger UI) — this is one of FastAPI's best
features: you get a free, working test UI for every endpoint,
generated from your Pydantic models and type hints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.routers import auth, tools,chat

app = FastAPI(
    title="XYZ AI - School Assistant Backend",
    description="Role-based AI school assistant backend with enforced RBAC at the tool layer.",
    version="0.1.0",
)

# Allows our React frontend (running on a different port) to call this API.
# In production you'd restrict allow_origins to your real frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tools.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}