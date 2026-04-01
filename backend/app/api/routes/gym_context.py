"""
Gym Context API — exposes current gym data for debugging and frontend use.
"""

from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.models.user import User
from app.services.gym_context_provider import GymContextProvider

router = APIRouter()


@router.get("/")
async def get_gym_context(current_user: User = Depends(get_current_user)):
    """Return the current gym context used for AI content generation."""
    return GymContextProvider.get_context()


@router.get("/prompt-block")
async def get_prompt_block(current_user: User = Depends(get_current_user)):
    """Return the formatted prompt block injected into AI prompts."""
    return {"prompt_block": GymContextProvider.get_prompt_block()}


@router.post("/refresh")
async def refresh_context(current_user: User = Depends(get_current_user)):
    """Force-refresh the cached gym context."""
    GymContextProvider.invalidate()
    ctx = GymContextProvider.get_context()
    return {"status": "refreshed", "keys": list(ctx.keys())}
