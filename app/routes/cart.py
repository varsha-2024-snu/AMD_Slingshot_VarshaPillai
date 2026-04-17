"""GET + POST /cart — Cart CRUD backed by Firestore, scoped to authenticated user."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import verify_token
from app.models.cart import CartItem, CartResponse
from app.services import firestore as fs

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Cart"])


@router.get("/cart", response_model=CartResponse)
async def get_cart(uid: str = Depends(verify_token)) -> CartResponse:
    """Return all cart items for the authenticated user."""
    items = await fs.get_cart(uid)
    total = sum(item.price * item.qty for item in items)
    return CartResponse(user_id=uid, items=items, total=round(total, 2))


@router.post("/cart", response_model=dict)
async def add_to_cart(item: CartItem, uid: str = Depends(verify_token)) -> dict:
    """Add or update a product in the authenticated user's cart."""
    success = await fs.upsert_cart_item(uid, item)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update cart. Please retry.")
    return {"status": "updated", "product_id": item.product_id}
