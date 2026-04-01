"""Competitor Spy API routes."""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.competitor_spy_service import CompetitorSpyService

router = APIRouter(tags=["competitor-spy"])
_svc: Optional[CompetitorSpyService] = None


def _get() -> CompetitorSpyService:
    global _svc
    if _svc is None:
        _svc = CompetitorSpyService()
    return _svc


@router.get("/competitors")
async def list_competitors():
    return {"competitors": _get().list_competitors()}


@router.post("/competitors")
async def add_competitor(body: dict):
    """Add a competitor. Body: {name, platform_url?, notes?}"""
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(400, "name required")
    return {"competitor": _get().add_competitor(body)}


@router.get("/competitors/{competitor_id}")
async def get_competitor(competitor_id: str):
    c = _get().get_competitor(competitor_id)
    if not c:
        raise HTTPException(404, "Competitor not found")
    return {"competitor": c}


@router.put("/competitors/{competitor_id}")
async def update_competitor(competitor_id: str, body: dict):
    c = _get().update_competitor(competitor_id, body)
    if not c:
        raise HTTPException(404, "Competitor not found")
    return {"competitor": c}


@router.delete("/competitors/{competitor_id}")
async def delete_competitor(competitor_id: str):
    if not _get().delete_competitor(competitor_id):
        raise HTTPException(404, "Competitor not found")
    return {"status": "deleted"}


@router.post("/competitors/{competitor_id}/scan")
async def scan_competitor(competitor_id: str, body: dict = None):
    """Scan competitor. Body: {posts: [...]} — their recent posts for AI analysis."""
    posts = (body or {}).get("posts", [])
    if not posts:
        raise HTTPException(400, "posts list required")
    result = await _get().scan_competitor(competitor_id, posts)
    return {"status": "success", **result}


@router.post("/competitors/{competitor_id}/counter-post")
async def generate_counter_post(competitor_id: str, body: dict = None):
    """Generate a counter-post beating their best content. Body: {brand_prompt?}"""
    result = await _get().generate_counter_post(
        competitor_id, (body or {}).get("brand_prompt", "")
    )
    return {"status": "success", **result}


@router.get("/dashboard")
async def get_spy_dashboard():
    return _get().get_dashboard()


@router.get("/insights")
async def get_insights():
    return {"insights": _get().get_insights()}
