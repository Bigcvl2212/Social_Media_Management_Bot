"""
Clip Studio API routes — upload raw footage, AI-analyze, generate viral clips.
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
import json

from app.services.clip_studio_service import ClipStudioService, CLIPS_DIR, THUMBS_DIR, RAW_FOOTAGE_DIR

router = APIRouter(tags=["clip-studio"])

_svc: Optional[ClipStudioService] = None


def _get_svc() -> ClipStudioService:
    global _svc
    if _svc is None:
        _svc = ClipStudioService()
    return _svc


# ── Upload ───────────────────────────────────────────────────────

@router.post("/upload")
async def upload_footage(file: UploadFile = File(...)):
    """Upload raw video footage for processing."""
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    allowed_ext = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".wmv"}
    ext = ("." + file.filename.rsplit(".", 1)[-1].lower()) if "." in file.filename else ""
    if ext not in allowed_ext:
        raise HTTPException(400, f"Unsupported format. Allowed: {', '.join(allowed_ext)}")

    data = await file.read()
    if len(data) > 2 * 1024 * 1024 * 1024:  # 2GB cap
        raise HTTPException(413, "File too large (max 2GB)")

    result = await _get_svc().save_upload(file.filename, data)
    return {"status": "success", "footage": result}


# ── List / Get / Delete footage ──────────────────────────────────

@router.get("/footage")
async def list_footage():
    """List all uploaded raw footage."""
    return {"footage": _get_svc().list_footage()}


@router.get("/footage/{footage_id}")
async def get_footage(footage_id: str):
    """Get full details for one footage item."""
    rec = _get_svc().get_footage(footage_id)
    if not rec:
        raise HTTPException(404, "Footage not found")
    return {"footage": rec}


@router.delete("/footage/{footage_id}")
async def delete_footage(footage_id: str):
    """Delete footage and all its generated clips."""
    ok = _get_svc().delete_footage(footage_id)
    if not ok:
        raise HTTPException(404, "Footage not found")
    return {"status": "deleted"}


# ── Analyze ──────────────────────────────────────────────────────

@router.post("/footage/{footage_id}/analyze")
async def analyze_footage(footage_id: str):
    """Run AI scene analysis on uploaded footage."""
    try:
        analysis = await _get_svc().analyze_footage(footage_id)
        return {"status": "success", "analysis": analysis}
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {e}")


# ── Generate clips ───────────────────────────────────────────────

@router.post("/footage/{footage_id}/generate-clips")
async def generate_clips(footage_id: str, body: dict):
    """Generate clips from selected scenes.

    Body: {
        "clips": [{"scene_index": 0, "start": 0, "end": 15, "title": "..."}],
        "aspect_ratio": "9:16",
        "add_captions": false
    }
    """
    clips_sel = body.get("clips", [])
    if not clips_sel:
        raise HTTPException(400, "No clips selected")

    aspect = body.get("aspect_ratio", "9:16")
    captions = body.get("add_captions", False)

    try:
        generated = await _get_svc().generate_clips(
            footage_id, clips_sel, aspect_ratio=aspect, add_captions=captions
        )
        return {"status": "success", "clips": generated}
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Clip generation failed: {e}")


# ── List / Delete clips ─────────────────────────────────────────

@router.get("/clips")
async def list_clips(footage_id: Optional[str] = Query(None)):
    """List generated clips, optionally filtered by footage_id."""
    return {"clips": _get_svc().list_clips(footage_id)}


@router.delete("/clips/{clip_id}")
async def delete_clip(clip_id: str):
    """Delete a generated clip."""
    ok = _get_svc().delete_clip(clip_id)
    if not ok:
        raise HTTPException(404, "Clip not found")
    return {"status": "deleted"}


# ── Serve files ──────────────────────────────────────────────────

@router.get("/thumbnail/{filename}")
async def serve_thumbnail(filename: str):
    """Serve a thumbnail image."""
    import re
    if not re.match(r'^[a-zA-Z0-9_\-]+\.jpg$', filename):
        raise HTTPException(400, "Invalid filename")
    path = THUMBS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Thumbnail not found")
    return FileResponse(str(path), media_type="image/jpeg")


@router.get("/clip-file/{filename}")
async def serve_clip(filename: str):
    """Serve a generated clip video."""
    import re
    if not re.match(r'^[a-zA-Z0-9_\-]+\.mp4$', filename):
        raise HTTPException(400, "Invalid filename")
    path = CLIPS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Clip not found")
    return FileResponse(str(path), media_type="video/mp4")
