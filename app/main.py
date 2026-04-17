"""
main.py — FastAPI application factory for ShopGenie.

Responsibilities:
- Register all API routes under /api/v1
- Mount frontend static files
- Configure CORS to restrict origins explicitly (security)
- Expose /health for Cloud Run liveness checks
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import FRONTEND_ORIGIN
from app.routes import chat, vision, cart, products

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ShopGenie API",
    description="Multimodal AI shopping assistant powered by Gemini 1.5 Flash.",
    version="1.0.0",
    # Disable Swagger UI in production to reduce attack surface
    docs_url="/docs" if __import__("os").getenv("ENV") != "production" else None,
)

# CORS: explicitly restrict to known origins — not wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "https://shopgenie-hy7jpqxcsa-uc.a.run.app", "https://amd-slingshot-cec69.web.app", "https://amd-slingshot-cec69.firebaseapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register API routes
app.include_router(chat.router, prefix="/api/v1")
app.include_router(vision.router, prefix="/api/v1")
app.include_router(cart.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")

@app.get("/health", tags=["Ops"])
async def health_check() -> dict:
    """Cloud Run liveness probe. Must return 200 within 10 seconds."""
    return {"status": "ok", "service": "shopgenie"}


# Serve Stitch-generated frontend as static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
