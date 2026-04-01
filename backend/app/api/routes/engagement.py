"""Engagement Autopilot API routes."""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.engagement_autopilot_service import EngagementAutopilotService

router = APIRouter(tags=["engagement"])
_svc: Optional[EngagementAutopilotService] = None


def _get() -> EngagementAutopilotService:
    global _svc
    if _svc is None:
        _svc = EngagementAutopilotService()
    return _svc


@router.get("/config")
async def get_config():
    return {"config": _get().get_config()}


@router.put("/config")
async def update_config(body: dict):
    return {"config": _get().update_config(body)}


@router.get("/rules")
async def get_rules():
    return {"rules": _get().get_rules()}


@router.post("/rules")
async def add_rule(body: dict):
    return {"rule": _get().add_rule(body)}


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    if not _get().delete_rule(rule_id):
        raise HTTPException(404, "Rule not found")
    return {"status": "deleted"}


@router.post("/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str):
    r = _get().toggle_rule(rule_id)
    if not r:
        raise HTTPException(404, "Rule not found")
    return {"rule": r}


@router.post("/process-comments")
async def process_comments(body: dict):
    """Process comments batch. Body: {comments: [...], brand_prompt?: "..."}"""
    comments = body.get("comments", [])
    if not comments:
        raise HTTPException(400, "No comments provided")
    brand_prompt = body.get("brand_prompt", "")
    result = await _get().process_comments(comments, brand_prompt)
    return {"status": "success", **result}


@router.post("/welcome-dm")
async def generate_welcome_dm(body: dict):
    """Generate welcome DM. Body: {follower_name: "...", brand_prompt?: "..."}"""
    name = body.get("follower_name", "").strip()
    if not name:
        raise HTTPException(400, "follower_name required")
    result = await _get().generate_welcome_dm(name, body.get("brand_prompt", ""))
    return {"status": "success", **result}


@router.get("/stats")
async def get_stats():
    return {"stats": _get().get_stats()}


@router.get("/history")
async def get_history(limit: int = 50):
    return {"history": _get().get_history(limit)}


@router.get("/flagged")
async def get_flagged(limit: int = 50):
    return {"flagged": _get().get_flagged(limit)}


@router.delete("/flagged/{comment_id}")
async def dismiss_flagged(comment_id: str):
    if not _get().dismiss_flagged(comment_id):
        raise HTTPException(404, "Not found")
    return {"status": "dismissed"}
