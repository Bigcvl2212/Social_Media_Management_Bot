"""
Facebook Page management routes — posting, comments, insights.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.facebook_service import FacebookService
from app.services.gemini_ai_service import GeminiAIService
from app.services.credential_resolver import get_facebook_credentials
from app.services.content_autopilot_service import sanitize_post_text

router = APIRouter()
logger = logging.getLogger(__name__)


def _is_quota_or_billing_error(message: str) -> bool:
    text = (message or "").lower()
    return (
        "resource_exhausted" in text
        or "spending cap" in text
        or "quota" in text
        or "billing" in text
        or "429" in text
    )


def _raise_generation_exception(exc: Exception) -> None:
    msg = str(exc)
    if _is_quota_or_billing_error(msg):
        raise HTTPException(
            status_code=429,
            detail=(
                "Video generation is currently unavailable because the Gemini project "
                "hit quota/billing limits (RESOURCE_EXHAUSTED). "
                "Increase project spending cap or quota and retry."
            ),
        )
    raise HTTPException(status_code=500, detail=f"Generation failed: {msg}")


async def _fb(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FacebookService:
    creds = await get_facebook_credentials(db, user_id=current_user.id)
    return FacebookService(page_id=creds.page_id, page_token=creds.page_token)


# ── Request models ───────────────────────────────────────

class TextPostRequest(BaseModel):
    message: str

class PhotoPostRequest(BaseModel):
    image_url: str
    caption: str = ""

class VideoPostRequest(BaseModel):
    video_url: str
    description: str = ""

class SchedulePostRequest(BaseModel):
    message: str
    scheduled_time: datetime
    image_url: Optional[str] = None

class ReplyRequest(BaseModel):
    message: str

class EditPostRequest(BaseModel):
    message: str

class GeneratePostRequest(BaseModel):
    topic: str = "motivation"
    tone: str = "casual"
    platform: str = "facebook"
    content_type: str = "text"  # text | image | video


# ── AI Generation ────────────────────────────────────────

@router.post("/generate-post")
async def generate_post(
    req: GeneratePostRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate a social media post via Gemini AI.
    content_type: text = text only, image = text + AI image, video = text + AI video.
    """
    try:
        gemini = GeminiAIService()
        result = await gemini.generate_post_text(
            topic=req.topic, style=req.tone, platform=req.platform,
        )

        raw_text = result.get("emoji_enhanced") or result.get("main_text", "")
        clean_text = sanitize_post_text(raw_text)
        clean_main = sanitize_post_text(result.get("main_text", ""))

        response = {
            "text": clean_text,
            "main_text": clean_main,
            "hashtags": result.get("hashtags", []),
            "call_to_action": result.get("call_to_action", ""),
            "variations": result.get("variations", []),
            "posting_tips": result.get("posting_tips", ""),
            "content_type": req.content_type,
            "media_url": None,
            "media_path": None,
        }

        if req.content_type == "image":
            headline = result.get("headline", req.topic[:60])
            img_prompt = f"{req.topic} - professional gym / fitness marketing graphic"
            img_result = await gemini.generate_image(
                prompt=img_prompt, aspect_ratio="1:1",
                headline_overlay=headline,
            )
            if img_result.get("status") == "success":
                response["media_url"] = f"/uploads/generated/{img_result['filename']}"
                response["media_path"] = img_result["filepath"]
            else:
                response["media_error"] = img_result.get("error", "Image generation failed")

        elif req.content_type == "video":
            headline = result.get("headline", req.topic[:60])
            vid_prompt = f"{headline} - energetic gym / fitness promotional video for Anytime Fitness Fond Du Lac"
            vid_result = await gemini.generate_extended_video(
                prompt=vid_prompt,
                target_duration=30,
                aspect_ratio="16:9",
            )
            if vid_result.get("status") == "success":
                response["media_url"] = f"/uploads/generated/{vid_result['filename']}"
                response["media_path"] = vid_result["filepath"]
                response["video_duration"] = vid_result.get("duration_seconds")
                response["video_segments"] = vid_result.get("segments")
            else:
                media_error = vid_result.get("error", "Video generation failed")
                if _is_quota_or_billing_error(media_error):
                    raise HTTPException(
                        status_code=429,
                        detail=(
                            "Video generation is currently unavailable because the Gemini project "
                            "hit quota/billing limits (RESOURCE_EXHAUSTED). "
                            "Increase project spending cap or quota and retry."
                        ),
                    )
                response["media_error"] = media_error

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("/facebook/generate-post failed")
        _raise_generation_exception(e)


# ── Posts ────────────────────────────────────────────────

class PublishPostRequest(BaseModel):
    message: str
    content_type: str = "text"  # text | image | video
    media_path: Optional[str] = None  # local file path from generate-post

@router.post("/posts/publish")
async def publish_post(req: PublishPostRequest, fb: FacebookService = Depends(_fb)):
    """Unified publish: text, photo, or video based on content_type."""
    clean_msg = sanitize_post_text(req.message)
    if req.content_type == "image" and req.media_path:
        return await fb.post_photo(req.media_path, clean_msg)
    elif req.content_type == "video" and req.media_path:
        return await fb.post_video(req.media_path, clean_msg)
    else:
        return await fb.post_text(clean_msg)

@router.post("/posts/text")
async def create_text_post(req: TextPostRequest, fb: FacebookService = Depends(_fb)):
    return await fb.post_text(sanitize_post_text(req.message))

@router.post("/posts/photo")
async def create_photo_post(req: PhotoPostRequest, fb: FacebookService = Depends(_fb)):
    return await fb.post_photo(req.image_url, sanitize_post_text(req.caption))

@router.post("/posts/video")
async def create_video_post(req: VideoPostRequest, fb: FacebookService = Depends(_fb)):
    return await fb.post_video(req.video_url, sanitize_post_text(req.description))

@router.post("/posts/schedule")
async def schedule_post(req: SchedulePostRequest, fb: FacebookService = Depends(_fb)):
    return await fb.schedule_post(
        message=sanitize_post_text(req.message),
        scheduled_time=req.scheduled_time,
        image_url=req.image_url,
    )

@router.get("/posts")
async def list_posts(fb: FacebookService = Depends(_fb), limit: int = Query(25, ge=1, le=100)):
    return await fb.get_page_posts(limit=limit)

@router.put("/posts/{post_id}")
async def edit_post(post_id: str, req: EditPostRequest, fb: FacebookService = Depends(_fb)):
    return await fb.edit_post(post_id, req.message)

@router.delete("/posts/{post_id}")
async def delete_post(post_id: str, fb: FacebookService = Depends(_fb)):
    return await fb.delete_post(post_id)


# ── Comments ─────────────────────────────────────────────

@router.get("/posts/{post_id}/comments")
async def list_comments(post_id: str, fb: FacebookService = Depends(_fb), limit: int = Query(50, ge=1, le=200)):
    return await fb.get_post_comments(post_id, limit=limit)

@router.post("/comments/{comment_id}/reply")
async def reply_to_comment(comment_id: str, req: ReplyRequest, fb: FacebookService = Depends(_fb)):
    return await fb.reply_to_comment(comment_id, req.message)

@router.post("/comments/{comment_id}/hide")
async def hide_comment(comment_id: str, fb: FacebookService = Depends(_fb)):
    return await fb.hide_comment(comment_id)


# ── Insights ─────────────────────────────────────────────

@router.get("/insights/page")
async def page_insights(fb: FacebookService = Depends(_fb), period: str = Query("day", pattern="^(day|week|days_28)$")):
    return await fb.get_page_insights(period=period)

@router.get("/insights/post/{post_id}")
async def post_insights(post_id: str, fb: FacebookService = Depends(_fb)):
    return await fb.get_post_insights(post_id)

@router.get("/info")
async def page_info(fb: FacebookService = Depends(_fb)):
    return await fb.get_page_info()
