"""Growth Tracker API routes."""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.growth_tracker_service import GrowthTrackerService

router = APIRouter(tags=["growth"])
_svc: Optional[GrowthTrackerService] = None


def _get() -> GrowthTrackerService:
    global _svc
    if _svc is None:
        _svc = GrowthTrackerService()
    return _svc


@router.post("/snapshot")
async def record_snapshot(body: dict):
    """Record daily metrics snapshot. Body: {followers, engagement_rate, reach, impressions, ...}"""
    if not body.get("followers"):
        raise HTTPException(400, "followers count required")
    result = _get().record_snapshot(body)
    return {"status": "success", **result}


@router.get("/dashboard")
async def get_dashboard():
    return _get().get_dashboard()


@router.get("/trend")
async def get_trend_data(days: int = 30):
    return {"trend": _get().get_trend_data(days)}


@router.get("/report")
async def get_weekly_report():
    result = _get().get_weekly_report()
    return {"report": result}


@router.get("/milestones")
async def get_milestones():
    svc = _get()
    data = svc._load()
    return {"milestones": data.get("milestones", [])}


@router.get("/goals")
async def get_goals():
    svc = _get()
    data = svc._load()
    return {"goals": data.get("goals", {})}


@router.put("/goals")
async def update_goals(body: dict):
    result = _get().update_goals(body)
    return {"goals": result}
