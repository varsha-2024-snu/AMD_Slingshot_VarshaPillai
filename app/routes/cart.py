from fastapi import APIRouter, HTTPException
router = APIRouter()

@router.get("/cart")
async def get_cart():
    """GET /cart — implemented in Stage 3."""
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.post("/cart")
async def add_to_cart():
    """POST /cart — implemented in Stage 3."""
    raise HTTPException(status_code=501, detail="Not yet implemented")
