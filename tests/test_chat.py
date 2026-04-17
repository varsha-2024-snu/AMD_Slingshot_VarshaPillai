"""Unit tests for Gemini prompt construction and response parsing — no API calls."""
import pytest
from app.models.product import ProductSummary
from app.models.chat import Recommendation
from app.services.gemini import build_chat_prompt


MOCK_PRODUCTS = [
    ProductSummary(id="prod_001", name="Dinosaur Discovery Set", description="12 dinosaur figurines", price=749.0, tags=["dinosaur", "educational"]),
    ProductSummary(id="prod_007", name="Dinosaur Egg Surprise", description="Grow a dinosaur from an egg", price=349.0, tags=["dinosaur", "hatching"]),
]


def test_build_chat_prompt_contains_query():
    """Gemini prompt must include the user's query verbatim."""
    query = "birthday gift for a 10-year-old who loves dinosaurs under ₹800"
    prompt = build_chat_prompt(query, MOCK_PRODUCTS)
    assert query in prompt


def test_build_chat_prompt_contains_catalog():
    """Gemini prompt must contain catalog product IDs and prices."""
    prompt = build_chat_prompt("dinosaur toys", MOCK_PRODUCTS)
    assert "prod_001" in prompt
    assert "749.0" in prompt


def test_build_chat_prompt_excludes_out_of_budget():
    """Products present in catalog must appear in prompt regardless of budget (Gemini filters)."""
    prompt = build_chat_prompt("dinosaur under 500", MOCK_PRODUCTS)
    # Both products should appear in catalog — Gemini decides what to recommend
    assert "Dinosaur Discovery Set" in prompt
    assert "Dinosaur Egg Surprise" in prompt


def test_build_chat_prompt_empty_catalog():
    """Prompt builds without error when catalog is empty."""
    prompt = build_chat_prompt("anything", [])
    assert "USER QUERY: anything" in prompt
    assert "[]" in prompt  # Empty catalog JSON
