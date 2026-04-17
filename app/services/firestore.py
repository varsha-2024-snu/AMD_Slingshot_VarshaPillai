"""
firestore.py — Firestore service layer for ShopGenie.

All Firestore reads and writes are isolated here.
Routes never import the Firestore client directly — they call these functions.
This makes the data layer independently testable and swappable.
"""

import os
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import DocumentSnapshot

from app.config import FIREBASE_PROJECT_ID
from app.models.product import Product, ProductSummary
from app.models.cart import CartItem

logger = logging.getLogger(__name__)

# Initialise Firebase Admin once at module load.
# In Cloud Run, Application Default Credentials (ADC) are used automatically.
if not firebase_admin._apps:
    cred = None
    if os.path.exists("service-account.json"):
        cred = credentials.Certificate("service-account.json")
    
    firebase_admin.initialize_app(
        credential=cred,
        options={"projectId": FIREBASE_PROJECT_ID}
    )

_db = firestore.client()


async def get_products_by_category(category: Optional[str] = None, limit: int = 20) -> list[ProductSummary]:
    """
    Fetch products from Firestore, optionally filtered by category.
    Returns compact ProductSummary objects to minimise Gemini prompt token usage.
    """
    try:
        ref = _db.collection("products")
        if category:
            ref = ref.where("category", "==", category)
        docs = ref.limit(limit).stream()
        return [
            ProductSummary(
                id=doc.id,
                name=doc.get("name"),
                description=doc.get("description"),
                price=doc.get("price"),
                tags=doc.get("tags", []),
            )
            for doc in docs
        ]
    except Exception as e:
        logger.error(f"Firestore product fetch failed: {e}")
        return []


async def get_all_products(limit: int = 50) -> list[Product]:
    """Fetch full product objects for the catalog browse endpoint."""
    try:
        docs = _db.collection("products").limit(limit).stream()
        return [Product(id=doc.id, **doc.to_dict()) for doc in docs]
    except Exception as e:
        logger.error(f"Firestore full catalog fetch failed: {e}")
        return []


async def get_cart(user_id: str) -> list[CartItem]:
    """Read a user's cart items. Scoped to the authenticated user's UID."""
    try:
        docs = _db.collection("carts").document(user_id).collection("items").stream()
        return [CartItem(**doc.to_dict()) for doc in docs]
    except Exception as e:
        logger.error(f"Firestore cart read failed for user {user_id}: {e}")
        return []


async def upsert_cart_item(user_id: str, item: CartItem) -> bool:
    """
    Write or update a cart item for the authenticated user.
    Validates the CartItem model before writing — no raw dicts to Firestore.
    """
    try:
        ref = (
            _db.collection("carts")
            .document(user_id)
            .collection("items")
            .document(item.product_id)
        )
        ref.set(item.model_dump(), merge=True)
        return True
    except Exception as e:
        logger.error(f"Firestore cart write failed for user {user_id}: {e}")
        return False


async def save_session_message(user_id: str, role: str, content: str) -> None:
    """Append a message to the user's session history for conversational context."""
    try:
        _db.collection("sessions").document(user_id).set(
            {
                "messages": firestore.ArrayUnion(
                    [{"role": role, "content": content}]
                ),
                "last_active": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )
    except Exception as e:
        logger.error(f"Session write failed for user {user_id}: {e}")
