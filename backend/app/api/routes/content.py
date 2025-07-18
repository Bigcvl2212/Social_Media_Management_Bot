"""
Content management routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_content():
    """List user's content"""
    return {"message": "Content endpoint - coming soon"}


@router.post("/")
async def create_content():
    """Create new content"""
    return {"message": "Create content - coming soon"}