"""
File upload routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def upload_file():
    """Upload media files"""
    return {"message": "File upload endpoint - coming soon"}


@router.post("/batch")
async def upload_batch_files():
    """Upload multiple files at once"""
    return {"message": "Batch upload - coming soon"}