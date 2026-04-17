from fastapi import APIRouter, HTTPException
router = APIRouter()

@router.post("/vision")
async def vision_endpoint():
    """POST /vision — implemented in Stage 3."""
    raise HTTPException(status_code=501, detail="Not yet implemented")
