"""
Analytics and insights routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_analytics():
    """Get analytics data"""
    return {"message": "Analytics endpoint - coming soon"}


@router.get("/dashboard")
async def get_dashboard_data():
    """Get dashboard analytics"""
    return {"message": "Dashboard data - coming soon"}