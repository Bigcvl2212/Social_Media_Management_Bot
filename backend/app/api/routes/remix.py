"""Content Remix Engine API routes."""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.content_remix_service import ContentRemixService

router = APIRouter(tags=["remix"])
_svc: Optional[ContentRemixService] = None


def _get() -> ContentRemixService:
    global _svc
    if _svc is None:
        _svc = ContentRemixService()
    return _svc


@router.get("/formats")
async def get_formats():
    """Return all available remix formats."""
    return {"formats": _get().REMIX_FORMATS}


@router.get("/originals")
async def list_originals():
    return {"originals": _get().list_originals()}


@router.post("/originals")
async def add_original(body: dict):
    """Add an original post. Body: {post_text, platform?, engagement_score?, media_url?}"""
    text = body.get("post_text", "").strip()
    if not text:
        raise HTTPException(400, "post_text required")
    result = _get().add_original(body)
    return {"original": result}


@router.delete("/originals/{original_id}")
async def delete_original(original_id: str):
    if not _get().delete_original(original_id):
        raise HTTPException(404, "Original not found")
    return {"status": "deleted"}


@router.post("/discover-top")
async def discover_top_posts(body: dict):
    """Discover top posts from analytics. Body: {posts: [...], min_score?: 0.7}"""
    posts = body.get("posts", [])
    if not posts:
        raise HTTPException(400, "No posts provided")
    result = _get().discover_top_posts(posts, body.get("min_score", 0.7))
    return {"status": "success", **result}


@router.post("/remix")
async def remix_post(body: dict):
    """Remix a single post. Body: {original_id, target_format, brand_prompt?}"""
    oid = body.get("original_id")
    fmt = body.get("target_format")
    if not oid or not fmt:
        raise HTTPException(400, "original_id and target_format required")
    result = await _get().remix(oid, fmt, body.get("brand_prompt", ""))
    return {"status": "success", **result}


@router.post("/batch-remix")
async def batch_remix(body: dict):
    """Batch remix top posts. Body: {formats: [...], top_n?: 5, brand_prompt?}"""
    formats = body.get("formats", [])
    if not formats:
        raise HTTPException(400, "formats list required")
    result = await _get().batch_remix(
        formats, body.get("top_n", 5), body.get("brand_prompt", "")
    )
    return {"status": "success", **result}


@router.get("/remixes")
async def list_remixes(original_id: str = None, target_format: str = None):
    return {"remixes": _get().list_remixes(original_id, target_format)}


@router.delete("/remixes/{remix_id}")
async def delete_remix(remix_id: str):
    if not _get().delete_remix(remix_id):
        raise HTTPException(404, "Remix not found")
    return {"status": "deleted"}
