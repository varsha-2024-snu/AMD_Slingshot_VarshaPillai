"""POST /chat — Text-based product search via Gemini 1.5 Flash."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import verify_token
from app.models.chat import ChatRequest, ChatResponse
from app.services import firestore as fs
from app.services import gemini

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    uid: str = Depends(verify_token),
) -> ChatResponse:
    """
    Process a natural language shopping query and return AI-grounded recommendations.
    Fetches relevant products from Firestore before calling Gemini — no hallucinated SKUs.
    """
    # Simple category hint extraction — keeps Firestore reads targeted
    category_hints = {
        "toy": "toys", "game": "toys", "dinosaur": "toys",
        "book": "books", "read": "books",
        "phone": "electronics", "laptop": "electronics", "charger": "electronics",
        "shirt": "clothing", "jacket": "clothing", "clothes": "clothing",
        "kitchen": "home", "home": "home", "cook": "home",
    }
    query_lower = request.query.lower()
    category = next((v for k, v in category_hints.items() if k in query_lower), None)

    products = await fs.get_products_by_category(category=category)
    if not products:
        # Fallback: fetch across all categories if targeted fetch returns empty
        products = await fs.get_products_by_category(category=None)

    recommendations, follow_up = await gemini.get_chat_recommendations(request.query, products)

    # Persist the exchange to session history for conversational context
    await fs.save_session_message(uid, "user", request.query)
    if recommendations:
        summary = f"Recommended: {', '.join(r.name for r in recommendations)}"
        await fs.save_session_message(uid, "model", summary)

    return ChatResponse(recommendations=recommendations, follow_up=follow_up)
