"""
Social accounts management routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_social_accounts():
    """List user's social media accounts"""
    return {"message": "Social accounts endpoint - coming soon"}


@router.post("/connect/{platform}")
async def connect_social_account(platform: str):
    """Connect a social media account"""
    return {"message": f"Connect {platform} account - coming soon"}