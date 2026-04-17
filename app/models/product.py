"""Product domain model — shared across catalog reads and Gemini responses."""
from pydantic import BaseModel, HttpUrl
from typing import Optional


class Product(BaseModel):
    id: str
    name: str
    description: str
    category: str
    price: float          # INR
    image_url: str
    tags: list[str]
    stock: int


class ProductSummary(BaseModel):
    """Compact product view injected into Gemini prompts to minimise token usage."""
    id: str
    name: str
    description: str
    price: float
    tags: list[str]
