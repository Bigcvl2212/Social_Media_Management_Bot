"""
Autopilot API — control the autonomous content posting engine.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()


class AutopilotToggle(BaseModel):
    enabled: bool

class AutopilotTrigger(BaseModel):
    topic: Optional[str] = None

class AutopilotConfigUpdate(BaseModel):
    """Partial config update — only include the fields you want to change."""
    posts_per_day: Optional[int] = None
    posting_windows: Optional[List[Dict[str, Any]]] = None
    daily_themes: Optional[Dict[str, List[str]]] = None
    styles: Optional[List[str]] = None
    format_weights: Optional[Dict[str, float]] = None
    enabled: Optional[bool] = None


def _get_autopilot():
    """Get the running autopilot instance from main.py."""
    from app.main import _content_autopilot
    if not _content_autopilot:
        raise HTTPException(status_code=503, detail="Autopilot service not running")
    return _content_autopilot


@router.get("/status")
async def autopilot_status(current_user: User = Depends(get_current_user)):
    """Get the current autopilot status."""
    ap = _get_autopilot()
    return ap.get_status()


@router.post("/toggle")
async def toggle_autopilot(
    body: AutopilotToggle,
    current_user: User = Depends(get_current_user),
):
    """Enable or disable the autopilot."""
    ap = _get_autopilot()
    ap.enabled = body.enabled
    return {"enabled": ap.enabled}


@router.post("/trigger")
async def trigger_post(
    body: AutopilotTrigger,
    current_user: User = Depends(get_current_user),
):
    """Manually trigger an immediate autopilot post."""
    ap = _get_autopilot()
    result = await ap.trigger_now(topic=body.topic)
    return result


@router.get("/config")
async def get_config(current_user: User = Depends(get_current_user)):
    """Get the full autopilot configuration (themes, schedule, weights, etc.)."""
    ap = _get_autopilot()
    return ap.get_full_config()


@router.put("/config")
async def update_config(
    body: AutopilotConfigUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update autopilot configuration. Only include fields you want to change.
    
    Examples:
    - Change to 4 posts/day: {"posting_windows": [{"hour": 7, "minute": 0, "label": "morning"}, ...]}
    - Change format weights: {"format_weights": {"image": 0.5, "text": 0.3, "video": 0.2}}
    - Update Monday themes: {"daily_themes": {"0": ["theme1", "theme2", ...]}}
    - Change styles: {"styles": ["promotional", "educational", "community-story"]}
    """
    ap = _get_autopilot()
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    
    # Validate format_weights sum to ~1.0 if provided
    if "format_weights" in updates:
        fw = updates["format_weights"]
        total = sum(fw.values())
        if abs(total - 1.0) > 0.05:
            raise HTTPException(
                status_code=400,
                detail=f"format_weights must sum to ~1.0 (got {total:.2f})"
            )
    
    # Validate posting_windows have required fields
    if "posting_windows" in updates:
        for w in updates["posting_windows"]:
            if "hour" not in w or "minute" not in w:
                raise HTTPException(
                    status_code=400,
                    detail="Each posting_window must have 'hour' and 'minute'"
                )
            if not (0 <= w["hour"] <= 23) or not (0 <= w["minute"] <= 59):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid time: {w['hour']:02d}:{w['minute']:02d}"
                )

    result = ap.update_config(updates)
    return {"status": "updated", "config": result}


@router.get("/history")
async def get_history(
    limit: int = 20,
    date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Get autopilot publish history. Optional ?date=YYYY-MM-DD filter."""
    ap = _get_autopilot()
    return ap.get_history(limit=limit, date=date)


@router.post("/generate-day")
async def generate_day_queue(
    current_user: User = Depends(get_current_user),
):
    """Generate all posts for today up front. AI-generates text + media for each
    posting window. Posts stay queued until their scheduled time, at which point
    the autopilot publishes them automatically."""
    ap = _get_autopilot()
    result = await ap.generate_day_queue()
    return result


@router.get("/day-queue")
async def get_day_queue(
    current_user: User = Depends(get_current_user),
):
    """Get the current pre-generated day queue with full post content."""
    ap = _get_autopilot()
    return ap.get_day_queue()
