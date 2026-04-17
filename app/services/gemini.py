"""
gemini.py — Gemini 1.5 Flash integration for ShopGenie.

All Gemini API calls are isolated here.
The service layer takes typed inputs and returns typed outputs.
Routes never import the Gemini SDK directly.
"""

import json
import logging
from typing import Optional
import google.generativeai as genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_CATALOG_PRODUCTS
from app.models.product import ProductSummary
from app.models.chat import Recommendation

logger = logging.getLogger(__name__)

# Configure the Gemini SDK once at module load
genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel(GEMINI_MODEL)

# System prompt template — injected with catalog at request time
_CHAT_SYSTEM_PROMPT = """You are ShopGenie, an AI shopping assistant.
Your job is to help users find the perfect product from the CATALOG provided below.

STRICT RULES:
1. Only recommend products that exist in the CATALOG. Never invent products or prices.
2. Always explain specifically WHY each product matches the user's request.
3. If the query is ambiguous or underspecified, ask exactly ONE clarifying question and return an empty recommendations list.
4. Return ONLY a JSON object matching this schema — no markdown, no preamble:
   {{"recommendations": [{{"id": "string", "name": "string", "price": number, "reason": "string"}}], "follow_up": "string or null"}}
5. Recommend 1–3 products maximum. Quality over quantity.

CATALOG (product options available to recommend):
{catalog_json}"""

_VISION_SYSTEM_PROMPT = """You are ShopGenie's visual search engine.
Analyse the uploaded product image and identify its category, key visual attributes (colour, style, size estimate), and likely use case.
Then find the 3 most visually and functionally similar items from the CATALOG below.

Return ONLY a JSON object — no markdown, no preamble:
{{"identified_category": "string", "attributes": ["string"], "recommendations": [{{"id": "string", "name": "string", "price": number, "reason": "string"}}]}}

CATALOG:
{catalog_json}"""


def _catalog_to_json(products: list[ProductSummary]) -> str:
    """Serialise product summaries to a compact JSON string for prompt injection."""
    return json.dumps(
        [{"id": p.id, "name": p.name, "description": p.description, "price": p.price, "tags": p.tags}
         for p in products[:MAX_CATALOG_PRODUCTS]],
        ensure_ascii=False,
        indent=None,  # Compact — minimise tokens
    )


def build_chat_prompt(query: str, products: list[ProductSummary]) -> str:
    """
    Build the full Gemini chat prompt by injecting catalog into the system template.
    Exposed as a pure function for unit testing without API calls.
    """
    catalog_json = _catalog_to_json(products)
    return _CHAT_SYSTEM_PROMPT.format(catalog_json=catalog_json) + f"\n\nUSER QUERY: {query}"


async def get_chat_recommendations(
    query: str,
    products: list[ProductSummary],
) -> tuple[list[Recommendation], Optional[str]]:
    """
    Call Gemini 1.5 Flash with a text shopping query and grounded catalog context.

    Returns:
        (recommendations, follow_up_question)
        follow_up is non-None when Gemini needs clarification before recommending.
    """
    prompt = build_chat_prompt(query, products)
    try:
        response = await _model.generate_content_async(prompt)
        raw = response.text.strip()
        # Strip markdown code fences if Gemini ignores the no-markdown instruction
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        recommendations = [Recommendation(**r) for r in data.get("recommendations", [])]
        follow_up = data.get("follow_up")
        return recommendations, follow_up
    except json.JSONDecodeError as e:
        logger.error(f"Gemini returned non-JSON for query '{query}': {e} | raw: {response.text[:200]}")
        return [], "I had trouble understanding that. Could you rephrase your query?"
    except Exception as e:
        logger.error(f"Gemini chat call failed: {e}")
        return [], "ShopGenie is temporarily unavailable. Please try again."


async def get_vision_recommendations(
    image_bytes: bytes,
    mime_type: str,
    products: list[ProductSummary],
) -> tuple[str, list[Recommendation]]:
    """
    Call Gemini 1.5 Flash Vision with an uploaded product image and catalog context.

    Args:
        image_bytes: Raw image bytes validated and size-capped before this call.
        mime_type: 'image/jpeg' or 'image/png' — validated at the route layer.

    Returns:
        (identified_category, recommendations)
    """
    catalog_json = _catalog_to_json(products)
    prompt = _VISION_SYSTEM_PROMPT.format(catalog_json=catalog_json)
    image_part = {"mime_type": mime_type, "data": image_bytes}
    try:
        # Note: Depending on SDK version, generate_content_async might need different list structure
        response = await _model.generate_content_async([prompt, image_part])
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        recommendations = [Recommendation(**r) for r in data.get("recommendations", [])]
        return data.get("identified_category", "unknown"), recommendations
    except Exception as e:
        logger.error(f"Gemini vision call failed: {e}")
        return "unknown", []
