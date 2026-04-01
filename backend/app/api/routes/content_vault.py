"""Content Vault API routes."""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional
import re
from pathlib import Path
from app.services.content_vault_service import ContentVaultService, _THUMBS_DIR, _VAULT_DIR

router = APIRouter(tags=["content-vault"])
_svc: Optional[ContentVaultService] = None


def _get() -> ContentVaultService:
    global _svc
    if _svc is None:
        _svc = ContentVaultService()
    return _svc


@router.post("/upload")
async def upload_asset(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No filename")
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".heic"}
    ext = ("." + file.filename.rsplit(".", 1)[-1].lower()) if "." in file.filename else ""
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported format. Allowed: {', '.join(allowed)}")
    data = await file.read()
    if len(data) > 500 * 1024 * 1024:
        raise HTTPException(413, "Max 500MB")
    result = await _get().upload_asset(file.filename, data)
    return {"status": "success", "asset": result}


@router.get("/assets")
async def list_assets(category: Optional[str] = None, tag: Optional[str] = None,
                      media_type: Optional[str] = None, limit: int = 50):
    return {"assets": _get().list_assets(category, tag, media_type, limit)}


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str):
    a = _get().get_asset(asset_id)
    if not a:
        raise HTTPException(404, "Asset not found")
    return {"asset": a}


@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str):
    if not _get().delete_asset(asset_id):
        raise HTTPException(404, "Asset not found")
    return {"status": "deleted"}


@router.put("/assets/{asset_id}")
async def update_asset(asset_id: str, body: dict):
    a = _get().update_asset(asset_id, body)
    if not a:
        raise HTTPException(404, "Asset not found")
    return {"asset": a}


@router.post("/assets/{asset_id}/favorite")
async def toggle_favorite(asset_id: str):
    a = _get().toggle_favorite(asset_id)
    if not a:
        raise HTTPException(404, "Asset not found")
    return {"asset": a}


@router.post("/assets/{asset_id}/retag")
async def retag_asset(asset_id: str):
    try:
        a = await _get().auto_tag(asset_id)
        return {"status": "success", "asset": a}
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/search")
async def search_assets(q: str = Query(..., min_length=1)):
    return {"assets": _get().search_assets(q)}


@router.get("/stats")
async def inventory_stats():
    return _get().get_inventory_stats()


@router.get("/thumbnail/{filename}")
async def serve_thumbnail(filename: str):
    if not re.match(r'^[a-zA-Z0-9_\-]+\.jpg$', filename):
        raise HTTPException(400, "Invalid filename")
    path = _THUMBS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Not found")
    return FileResponse(str(path), media_type="image/jpeg")
