"""
auth.py — Firebase ID Token verification middleware.

Used as a FastAPI dependency on all protected routes.
Raises HTTP 401 if the token is missing, expired, or invalid.
This is the security boundary between the public internet and user data.
"""

import logging
from fastapi import Header, HTTPException, Depends
from firebase_admin import auth

logger = logging.getLogger(__name__)


async def verify_token(authorization: str = Header(None)) -> str:
    """
    Verify Firebase ID Token from the Authorization header.

    Args:
        authorization: 'Bearer <firebase_id_token>' header value.

    Returns:
        The authenticated user's Firebase UID.

    Raises:
        HTTPException 401: If the token is missing, malformed, expired, or invalid.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header must be 'Bearer <token>'")

    token = authorization[len("Bearer "):]

    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token has expired. Please sign in again.")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed.")
