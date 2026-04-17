"""Cart item models for Firestore persistence."""
from pydantic import BaseModel, Field
from datetime import datetime


class CartItem(BaseModel):
    product_id: str
    name: str
    price: float
    qty: int = Field(..., ge=1, le=99)
    added_at: datetime = Field(default_factory=datetime.utcnow)


class CartResponse(BaseModel):
    user_id: str
    items: list[CartItem]
    total: float
