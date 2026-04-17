"""Chat request/response models with strict validation."""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    user_id: str = Field(..., min_length=1)


class Recommendation(BaseModel):
    id: str
    name: str
    price: float
    reason: str           # Gemini's explanation — shown to user


class ChatResponse(BaseModel):
    recommendations: list[Recommendation]
    follow_up: Optional[str] = None   # Clarifying question if query was ambiguous
