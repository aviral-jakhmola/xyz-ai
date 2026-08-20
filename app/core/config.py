"""
config.py — centralized environment configuration.

CONCEPT: never hardcode secrets (API keys) directly in your source code.
Load them from environment variables so the actual key never gets
committed to GitHub. python-dotenv reads a local .env file (which is
gitignored) and loads it into os.environ for us during local dev.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Parse comma-separated list or fallback to single key
raw_keys = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY", "")
GEMINI_API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

# Fallback string if needed
GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else None