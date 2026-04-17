"""
config.py — Centralised environment configuration for ShopGenie.

All environment variable reads happen here and nowhere else.
This makes secret rotation, testing, and auditing trivial.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()  # No-op in Cloud Run; values already in env via --set-secrets

logger = logging.getLogger(__name__)


def _require_env(key: str) -> str:
    """Read a required environment variable, raising clearly if missing."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"See .env.example for the full list of required variables."
        )
    return value


# --- Google AI ---
GEMINI_API_KEY: str = _require_env("GEMINI_API_KEY")
GEMINI_MODEL: str = "gemini-1.5-flash"  # Free tier, fastest, multimodal

# --- Firebase / Firestore ---
FIREBASE_PROJECT_ID: str = _require_env("FIREBASE_PROJECT_ID")

# --- Cloud Storage ---
GCS_BUCKET_NAME: str = _require_env("GCS_BUCKET_NAME")

# --- CORS ---
FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5500")

# --- Gemini constraints ---
MAX_CATALOG_PRODUCTS: int = 20   # Max products injected into a single Gemini prompt
MAX_IMAGE_SIZE_BYTES: int = 1 * 1024 * 1024  # 1MB — enforced backend-side as a safety net
