"""Brand DNA API routes."""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.brand_dna_service import BrandDNAService

router = APIRouter(tags=["brand-dna"])
_svc: Optional[BrandDNAService] = None


def _get() -> BrandDNAService:
    global _svc
    if _svc is None:
        _svc = BrandDNAService()
    return _svc


@router.get("/profile")
async def get_profile():
    return {"profile": _get().get_profile()}


@router.put("/brief")
async def update_brief(body: dict):
    return {"profile": _get().update_brief(body)}


@router.put("/style")
async def update_style(body: dict):
    return {"profile": _get().update_style(body)}


@router.post("/analyze")
async def analyze_posts(body: dict):
    """Analyze page posts. Body: {posts: [...]}"""
    posts = body.get("posts", [])
    if not posts:
        raise HTTPException(400, "No posts provided")
    result = await _get().analyze_posts(posts)
    return {"status": "success", **result}


@router.post("/chat")
async def brand_chat(body: dict):
    """Natural language brand direction. Body: {message: "..."}"""
    msg = body.get("message", "").strip()
    if not msg:
        raise HTTPException(400, "Message required")
    result = await _get().chat(msg)
    return {"status": "success", **result}


@router.get("/style-prompt")
async def get_style_prompt():
    """Get the style instruction block for other services."""
    return {"prompt": _get().get_style_prompt()}


@router.post("/reset")
async def reset_profile():
    return {"profile": _get().reset_profile()}
