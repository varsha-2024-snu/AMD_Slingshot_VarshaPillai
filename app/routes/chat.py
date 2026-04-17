from fastapi import APIRouter, HTTPException
router = APIRouter()

@router.post("/chat")
async def chat_endpoint():
    """POST /chat — implemented in Stage 3."""
    raise HTTPException(status_code=501, detail="Not yet implemented")
