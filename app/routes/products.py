"""GET /products — Full catalog browse endpoint."""
import logging
from fastapi import APIRouter, Depends
from app.middleware.auth import verify_token
from app.models.product import Product
from app.services import firestore as fs

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Products"])


@router.get("/products", response_model=list[Product])
async def list_products(uid: str = Depends(verify_token)) -> list[Product]:
    """Return the full product catalog for authenticated users."""
    return await fs.get_all_products()
