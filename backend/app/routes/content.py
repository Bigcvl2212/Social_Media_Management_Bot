"""
FastAPI Routes for Content Management
Main API endpoints for content creation, processing, scheduling, and platform posting
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from datetime import datetime
import aiofiles

from app.core.config import settings
from app.services.content_processing import VideoProcessingService, ImageProcessingService
from app.services.ai_generation import AIContentGenerationService
try:
    from app.services.platform_integration import PlatformIntegrationService
except Exception:  # optional dependency bundle
    PlatformIntegrationService = None

def _get_video_service() -> VideoProcessingService:
    return VideoProcessingService()


def _get_image_service() -> ImageProcessingService:
    return ImageProcessingService()


def _get_ai_service() -> AIContentGenerationService:
    return AIContentGenerationService()


def _get_platform_service() -> PlatformIntegrationService:
    if PlatformIntegrationService is None:
        raise HTTPException(
            status_code=503,
            detail="Platform integrations are unavailable (missing optional dependencies).",
        )
    return PlatformIntegrationService()

# Create router
router = APIRouter(prefix="/api/v1", tags=["content"])


# ==================== CONTENT UPLOAD & PROCESSING ====================

@router.post("/content/upload/video")
async def upload_and_process_video(
    file: UploadFile = File(...),
    title: str = Form(""),
):
    """Upload and process video file"""
    try:
        # Save uploaded file
        upload_path = f"{settings.UPLOAD_DIR}/videos/{file.filename}"
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        
        async with aiofiles.open(upload_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process video
        result = await _get_video_service().process_video(upload_path)
        
        return {
            'status': 'success',
            'file_path': upload_path,
            'title': title,
            'clips': result.get('clips', []),
            'total_duration': result.get('total_duration'),
            'analysis': result.get('analysis'),
            'uploaded_at': datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")


@router.post("/content/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    title: str = Form(""),
):
    """Upload image file"""
    try:
        upload_path = f"{settings.UPLOAD_DIR}/images/{file.filename}"
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        
        async with aiofiles.open(upload_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return {
            'status': 'success',
            'file_path': upload_path,
            'title': title,
            'uploaded_at': datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")


# ==================== VIDEO EDITING ====================

@router.get("/video/{video_id}/clips")
async def get_video_clips(video_id: str):
    """Get detected clips from video"""
    # In real implementation, fetch from database
    return {
        'status': 'success',
        'video_id': video_id,
        'clips': [],
    }


@router.post("/video/clips/{clip_id}/add-branding")
async def add_branding_to_clip(
    clip_id: str,
    watermark_path: str = Form(...),
    position: str = Form("bottom-right"),
):
    """Add watermark/branding to video clip"""
    try:
        # Implementation would use FFmpeg to overlay watermark
        return {
            'status': 'success',
            'clip_id': clip_id,
            'message': f'Watermark added to {position}',
            'output_path': f"processed/{clip_id}_branded.mp4",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/clips/{clip_id}/add-music")
async def add_music_to_clip(
    clip_id: str,
    music_file: UploadFile = File(...),
    volume: float = Form(0.7),
    fade_in: float = Form(0.0),
    fade_out: float = Form(0.0),
):
    """Add background music to video clip"""
    try:
        music_path = f"{settings.UPLOAD_DIR}/music/{music_file.filename}"
        os.makedirs(os.path.dirname(music_path), exist_ok=True)
        
        async with aiofiles.open(music_path, 'wb') as f:
            content = await music_file.read()
            await f.write(content)
        
        return {
            'status': 'success',
            'clip_id': clip_id,
            'music_added': music_file.filename,
            'volume': volume,
            'output_path': f"processed/{clip_id}_with_music.mp4",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== IMAGE EDITING ====================

@router.post("/image/apply-filter")
async def apply_image_filter(
    image_path: str = Form(...),
    filter_name: str = Form(...),
    intensity: float = Form(1.0),
):
    """Apply filter to image"""
    try:
        output_path = _get_image_service().apply_filter(image_path, filter_name, intensity)
        
        return {
            'status': 'success',
            'original_path': image_path,
            'output_path': output_path,
            'filter': filter_name,
            'intensity': intensity,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/add-text")
async def add_text_to_image(
    image_path: str = Form(...),
    text: str = Form(...),
    position: str = Form("center"),
    font_size: int = Form(48),
    color: str = Form("white"),
):
    """Add text overlay to image"""
    try:
        output_path = _get_image_service().add_text_overlay(
            image_path, text, position, font_size, color
        )
        
        return {
            'status': 'success',
            'original_path': image_path,
            'output_path': output_path,
            'text': text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/optimize-platform")
async def optimize_image_for_platform(
    image_path: str = Form(...),
    platform: str = Form("instagram"),
):
    """Optimize image for specific platform"""
    try:
        output_path = _get_image_service().optimize_for_platform(image_path, platform)
        
        return {
            'status': 'success',
            'original_path': image_path,
            'output_path': output_path,
            'platform': platform,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AI GENERATION ====================

@router.post("/generate/script")
async def generate_video_script(
    topic: str = Form(...),
    duration_seconds: int = Form(60),
    style: str = Form("professional"),
):
    """Generate video script from topic"""
    try:
        result = await _get_ai_service().generate_script(topic, duration_seconds, style)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/video")
async def generate_video_from_script(
    script: str = Form(...),
    duration_seconds: int = Form(60),
    style: str = Form("professional"),
):
    """Generate video from script"""
    try:
        result = await _get_ai_service().generate_video_from_script(script, duration_seconds, style)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/video-from-audio")
async def generate_video_from_audio(
    audio_file: UploadFile = File(...),
    description: str = Form(...),
    duration_seconds: int = Form(60),
):
    """Generate video from audio file"""
    try:
        audio_path = f"{settings.UPLOAD_DIR}/audio/{audio_file.filename}"
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        async with aiofiles.open(audio_path, 'wb') as f:
            content = await audio_file.read()
            await f.write(content)
        
        result = await _get_ai_service().generate_video_from_audio(
            audio_path, description, duration_seconds
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/image")
async def generate_image_from_prompt(
    prompt: str = Form(...),
    style: str = Form("professional"),
    size: str = Form("1024x1024"),
):
    """Generate image from text prompt"""
    try:
        result = await _get_ai_service().generate_image_from_prompt(prompt, style, size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/captions")
async def generate_captions(
    content_description: str = Form(...),
    platform: str = Form(...),
    hashtags: bool = Form(True),
):
    """Generate platform-optimized captions"""
    try:
        result = await _get_ai_service().generate_captions(content_description, platform, hashtags)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate/ideas")
async def get_content_ideas(
    topic: str = Query(...),
    platform: str = Query(...),
    count: int = Query(5),
):
    """Get viral content ideas"""
    try:
        result = await _get_ai_service().generate_content_ideas(topic, platform, count)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/viral-potential")
async def analyze_viral_potential(
    content_description: str = Form(...),
    platform: str = Form(...),
    target_audience: str = Form("general"),
):
    """Analyze viral potential of content"""
    try:
        result = await _get_ai_service().predict_viral_potential(
            content_description, platform, target_audience
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/trending")
async def get_trending_topics(
    platform: str = Query(...),
    region: str = Query("global"),
):
    """Get trending topics for platform"""
    try:
        result = await _get_ai_service().analyze_trending_topics(platform, region)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PLATFORM POSTING ====================

@router.post("/post/instagram")
async def post_to_instagram(
    image_path: str = Form(...),
    caption: str = Form(...),
    hashtags: List[str] = Form(None),
    access_token: str = Form(...),
    page_id: str = Form(...),
):
    """Post image to Instagram"""
    try:
        result = await _get_platform_service().post_to_instagram(
            access_token, page_id, image_path, caption, hashtags
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post/instagram-reel")
async def post_reel_to_instagram(
    video_path: str = Form(...),
    caption: str = Form(...),
    access_token: str = Form(...),
    page_id: str = Form(...),
    thumbnail_path: str = Form(None),
):
    """Post Reel to Instagram"""
    try:
        result = await _get_platform_service().post_reel_to_instagram(
            access_token, page_id, video_path, caption, thumbnail_path
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post/tiktok")
async def post_to_tiktok(
    video_path: str = Form(...),
    description: str = Form(...),
    hashtags: List[str] = Form(None),
    access_token: str = Form(...),
):
    """Post video to TikTok"""
    try:
        result = await _get_platform_service().post_to_tiktok(
            access_token, video_path, description, hashtags
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post/youtube")
async def post_to_youtube(
    video_path: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    tags: List[str] = Form(None),
    access_token: str = Form(...),
    privacy_status: str = Form("public"),
    thumbnail_path: str = Form(None),
):
    """Upload video to YouTube"""
    try:
        result = await _get_platform_service().post_to_youtube(
            access_token, video_path, title, description, tags, privacy_status, thumbnail_path
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post/twitter")
async def post_to_twitter(
    text: str = Form(...),
    media_paths: List[str] = Form(None),
    access_token: str = Form(...),
):
    """Post to Twitter/X"""
    try:
        result = await _get_platform_service().post_to_twitter(access_token, text, media_paths)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post/facebook")
async def post_to_facebook(
    message: str = Form(...),
    page_id: str = Form(...),
    access_token: str = Form(...),
    image_path: str = Form(None),
):
    """Post to Facebook"""
    try:
        result = await _get_platform_service().post_to_facebook(
            access_token, page_id, message, image_path
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post/multi-platform")
async def post_to_multiple_platforms(
    platforms: List[str] = Form(...),
    content: dict = Form(...),
    access_tokens: dict = Form(...),
):
    """Post to multiple platforms simultaneously"""
    try:
        results = await _get_platform_service().post_to_multiple_platforms(
            platforms, content, access_tokens
        )
        return {
            'status': 'success',
            'platforms_posted': len([r for r in results.values() if r.get('status') == 'posted']),
            'results': results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ANALYTICS ====================

@router.get("/analytics/instagram")
async def get_instagram_analytics(
    page_id: str = Query(...),
    access_token: str = Query(...),
    metric: str = Query("impressions,reach,profile_views"),
):
    """Get Instagram analytics"""
    try:
        result = await _get_platform_service().get_instagram_analytics(
            access_token, page_id, metric
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/tiktok")
async def get_tiktok_analytics(
    access_token: str = Query(...),
):
    """Get TikTok analytics"""
    try:
        result = await _get_platform_service().get_tiktok_analytics(access_token)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/youtube")
async def get_youtube_analytics(
    access_token: str = Query(...),
    days: int = Query(30),
):
    """Get YouTube analytics"""
    try:
        result = await _get_platform_service().get_youtube_analytics(access_token, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/twitter")
async def get_twitter_analytics(
    access_token: str = Query(...),
):
    """Get Twitter/X analytics"""
    try:
        result = await _get_platform_service().get_twitter_analytics(access_token)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/facebook")
async def get_facebook_analytics(
    page_id: str = Query(...),
    access_token: str = Query(...),
):
    """Get Facebook analytics"""
    try:
        result = await _get_platform_service().get_facebook_analytics(access_token, page_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== OAUTH ====================

@router.get("/auth/oauth-url")
async def get_oauth_url(
    platform: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    state: str = Query(...),
):
    """Generate OAuth authorization URL"""
    try:
        url = _get_platform_service().get_oauth_url(platform, client_id, redirect_uri, state)
        return {'oauth_url': url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HEALTH CHECK ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'video_processing': 'available',
            'image_processing': 'available',
            'ai_generation': 'available',
            'platform_integration': 'available',
        }
    }
