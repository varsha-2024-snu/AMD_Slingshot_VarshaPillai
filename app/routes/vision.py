"""POST /vision — Image-based product search via Gemini 1.5 Flash Vision."""
import base64
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.middleware.auth import verify_token
from app.models.chat import ChatResponse
from app.services import firestore as fs
from app.services import gemini
from app.config import MAX_IMAGE_SIZE_BYTES

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Vision"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


class VisionRequest(BaseModel):
    image_base64: str
    mime_type: str = "image/jpeg"


@router.post("/vision", response_model=ChatResponse)
async def vision_endpoint(
    request: VisionRequest,
    uid: str = Depends(verify_token),
) -> ChatResponse:
    """
    Accept a base64-encoded product image and return visually similar catalog matches.
    Validates MIME type and byte size before passing to Gemini.
    """
    # Validate MIME type
    if request.mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type '{request.mime_type}'. Use JPEG, PNG, or WebP."
        )

    # Decode and validate size — backend safety net on top of client-side validation
    try:
        image_bytes = base64.b64decode(request.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image encoding.")

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Image exceeds 1MB limit ({len(image_bytes)} bytes). Resize before uploading."
        )

    products = await fs.get_products_by_category(category=None)
    category, recommendations = await gemini.get_vision_recommendations(
        image_bytes, request.mime_type, products
    )

    logger.info(f"Vision search by {uid}: identified category '{category}', {len(recommendations)} results")
    return ChatResponse(recommendations=recommendations, follow_up=None)
