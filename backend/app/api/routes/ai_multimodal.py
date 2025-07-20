"""
Advanced multi-modal AI content generation API routes
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.social_account import SocialPlatform as Platform
from app.services.ai_voiceover_service import AIVoiceoverService
from app.services.image_to_video_service import ImageToVideoService
from app.services.enhanced_meme_generator_service import EnhancedMemeGeneratorService
from app.services.ai_short_form_video_service import AIShortFormVideoService

router = APIRouter()

# Pydantic models for request/response
class VoiceoverRequest(BaseModel):
    text: str
    voice: str = "alloy"
    language: str = "en"
    platform: Platform = Platform.INSTAGRAM
    speed: float = 1.0

class DubbingRequest(BaseModel):
    target_language: str
    voice: str = "alloy"
    platform: Platform = Platform.INSTAGRAM
    preserve_timing: bool = True

class MultilingualRequest(BaseModel):
    target_languages: List[str]
    voice_preferences: Optional[Dict[str, str]] = None
    platform: Platform = Platform.INSTAGRAM

class PodcastNarrationRequest(BaseModel):
    content: str
    voice: str = "nova"
    style: str = "conversational"
    add_music: bool = True
    platform: Platform = Platform.YOUTUBE

class ImageToVideoRequest(BaseModel):
    motion_prompt: str
    platform: Platform = Platform.INSTAGRAM
    duration: int = 15
    style: str = "cinematic"

class SlideshowRequest(BaseModel):
    transition_style: str = "smooth"
    platform: Platform = Platform.INSTAGRAM
    duration_per_image: float = 3.0
    add_music: bool = True

class TextToImageVideoRequest(BaseModel):
    text_prompt: str
    motion_description: str
    platform: Platform = Platform.INSTAGRAM
    style: str = "realistic"
    duration: int = 15

class ParallaxVideoRequest(BaseModel):
    depth_layers: int = 3
    platform: Platform = Platform.INSTAGRAM
    movement_speed: str = "slow"

class MorphVideoRequest(BaseModel):
    steps: int = 30
    platform: Platform = Platform.INSTAGRAM

class ZoomEffectRequest(BaseModel):
    zoom_type: str = "zoom_in"
    focus_point: tuple = (0.5, 0.5)
    platform: Platform = Platform.INSTAGRAM
    duration: int = 10

class TrendingMemeRequest(BaseModel):
    topic: str
    brand_voice: str = "casual"
    platform: Platform = Platform.INSTAGRAM
    target_audience: str = "general"
    include_brand_elements: bool = True

class BrandMemeRequest(BaseModel):
    brand_info: Dict[str, Any]
    current_trends: List[str]
    platform: Platform = Platform.INSTAGRAM
    count: int = 5

class MemeSeriesRequest(BaseModel):
    theme: str
    series_count: int = 3
    platform: Platform = Platform.INSTAGRAM
    brand_voice: str = "casual"

class ReactiveMemeRequest(BaseModel):
    current_event: str
    brand_perspective: str
    platform: Platform = Platform.TWITTER
    urgency: str = "high"

class ShortFormVideoRequest(BaseModel):
    platform: Platform = Platform.TIKTOK
    style: str = "viral"
    target_duration: int = 15
    add_captions: bool = True
    add_effects: bool = True

class TrendVideoRequest(BaseModel):
    content_theme: str
    trending_audio: Optional[str] = None
    platform: Platform = Platform.TIKTOK
    video_style: str = "trending"

class HookVideoRequest(BaseModel):
    source_content: str
    hook_style: str = "question"
    platform: Platform = Platform.INSTAGRAM
    duration: int = 30

class EducationalVideoRequest(BaseModel):
    topic: str
    complexity_level: str = "beginner"
    platform: Platform = Platform.YOUTUBE
    format_style: str = "explainer"

class ProductVideoRequest(BaseModel):
    product_info: Dict[str, Any]
    showcase_style: str = "lifestyle"
    platform: Platform = Platform.INSTAGRAM
    focus_benefits: Optional[List[str]] = None

# AI Voiceover and Dubbing Endpoints
@router.post("/ai-voiceover/generate")
async def generate_ai_voiceover(
    request: VoiceoverRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI voiceover from text with platform optimization"""
    try:
        voiceover_service = AIVoiceoverService(db)
        result = await voiceover_service.generate_voiceover(
            request.text,
            request.voice,
            request.language,
            request.platform,
            request.speed
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voiceover generation failed: {str(e)}")

@router.post("/ai-voiceover/dub-video")
async def dub_video_with_ai(
    file: UploadFile = File(...),
    request: DubbingRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Dub existing video with AI-generated voiceover in target language"""
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        voiceover_service = AIVoiceoverService(db)
        result = await voiceover_service.dub_video(
            temp_path,
            request.target_language,
            request.voice,
            request.platform,
            request.preserve_timing
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video dubbing failed: {str(e)}")

@router.post("/ai-voiceover/multilingual")
async def create_multilingual_versions(
    file: UploadFile = File(...),
    request: MultilingualRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create multiple language versions of a video"""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        voiceover_service = AIVoiceoverService(db)
        result = await voiceover_service.create_multilingual_versions(
            temp_path,
            request.target_languages,
            request.voice_preferences,
            request.platform
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multilingual video creation failed: {str(e)}")

@router.post("/ai-voiceover/podcast-narration")
async def generate_podcast_narration(
    request: PodcastNarrationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate podcast-style narration for long-form content"""
    try:
        voiceover_service = AIVoiceoverService(db)
        result = await voiceover_service.generate_podcast_narration(
            request.content,
            request.voice,
            request.style,
            request.add_music,
            request.platform
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Podcast narration generation failed: {str(e)}")

@router.post("/ai-voiceover/voice-clone")
async def create_voice_cloning(
    sample_file: UploadFile = File(...),
    text: str = Form(...),
    platform: Platform = Form(Platform.INSTAGRAM),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create voiceover using voice cloning from sample audio"""
    try:
        temp_path = f"/tmp/{sample_file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await sample_file.read()
            buffer.write(content)
        
        voiceover_service = AIVoiceoverService(db)
        result = await voiceover_service.create_voice_cloning(
            temp_path, text, platform
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice cloning failed: {str(e)}")

# Image-to-Video Generation Endpoints
@router.post("/image-to-video/create")
async def create_video_from_image(
    file: UploadFile = File(...),
    request: ImageToVideoRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create video from single image with AI-generated motion"""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        video_service = ImageToVideoService(db)
        result = await video_service.create_video_from_image(
            temp_path,
            request.motion_prompt,
            request.platform,
            request.duration,
            request.style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image-to-video creation failed: {str(e)}")

@router.post("/image-to-video/slideshow")
async def create_slideshow_video(
    files: List[UploadFile] = File(...),
    request: SlideshowRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create slideshow video from multiple images"""
    try:
        image_paths = []
        for i, file in enumerate(files):
            temp_path = f"/tmp/slideshow_{i}_{file.filename}"
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            image_paths.append(temp_path)
        
        video_service = ImageToVideoService(db)
        result = await video_service.create_slideshow_video(
            image_paths,
            request.transition_style,
            request.platform,
            request.duration_per_image,
            request.add_music
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slideshow creation failed: {str(e)}")

@router.post("/image-to-video/text-to-video")
async def create_text_to_image_video(
    request: TextToImageVideoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create video by first generating image from text, then animating it"""
    try:
        video_service = ImageToVideoService(db)
        result = await video_service.create_text_to_image_video(
            request.text_prompt,
            request.motion_description,
            request.platform,
            request.style,
            request.duration
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text-to-image-video creation failed: {str(e)}")

@router.post("/image-to-video/parallax")
async def create_parallax_video(
    file: UploadFile = File(...),
    request: ParallaxVideoRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create parallax motion video effect from single image"""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        video_service = ImageToVideoService(db)
        result = await video_service.create_parallax_video(
            temp_path,
            request.depth_layers,
            request.platform,
            request.movement_speed
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parallax video creation failed: {str(e)}")

@router.post("/image-to-video/morph")
async def create_morph_video(
    start_file: UploadFile = File(...),
    end_file: UploadFile = File(...),
    request: MorphVideoRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create morphing video between two images"""
    try:
        start_path = f"/tmp/start_{start_file.filename}"
        with open(start_path, "wb") as buffer:
            content = await start_file.read()
            buffer.write(content)
        
        end_path = f"/tmp/end_{end_file.filename}"
        with open(end_path, "wb") as buffer:
            content = await end_file.read()
            buffer.write(content)
        
        video_service = ImageToVideoService(db)
        result = await video_service.create_morph_video(
            start_path,
            end_path,
            request.steps,
            request.platform
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Morph video creation failed: {str(e)}")

@router.post("/image-to-video/zoom-effect")
async def create_zoom_effect_video(
    file: UploadFile = File(...),
    request: ZoomEffectRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create zoom effect video from static image"""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        video_service = ImageToVideoService(db)
        result = await video_service.create_zoom_effect_video(
            temp_path,
            request.zoom_type,
            request.focus_point,
            request.platform,
            request.duration
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Zoom effect video creation failed: {str(e)}")

# Enhanced Meme Generator Endpoints
@router.post("/enhanced-memes/trending")
async def generate_trending_meme(
    request: TrendingMemeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate meme using current trending formats and topics"""
    try:
        meme_service = EnhancedMemeGeneratorService(db)
        result = await meme_service.generate_trending_meme(
            request.topic,
            request.brand_voice,
            request.platform,
            request.target_audience,
            request.include_brand_elements
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trending meme generation failed: {str(e)}")

@router.post("/enhanced-memes/brand-relevant")
async def generate_brand_relevant_memes(
    request: BrandMemeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate multiple brand-relevant memes based on current trends"""
    try:
        meme_service = EnhancedMemeGeneratorService(db)
        result = await meme_service.generate_brand_relevant_memes(
            request.brand_info,
            request.current_trends,
            request.platform,
            request.count
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brand meme generation failed: {str(e)}")

@router.post("/enhanced-memes/series")
async def create_meme_series(
    request: MemeSeriesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a series of related memes around a theme"""
    try:
        meme_service = EnhancedMemeGeneratorService(db)
        result = await meme_service.create_meme_series(
            request.theme,
            request.series_count,
            request.platform,
            request.brand_voice
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meme series creation failed: {str(e)}")

@router.post("/enhanced-memes/reactive")
async def generate_reactive_meme(
    request: ReactiveMemeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate reactive meme for current events or trending topics"""
    try:
        meme_service = EnhancedMemeGeneratorService(db)
        result = await meme_service.generate_reactive_meme(
            request.current_event,
            request.brand_perspective,
            request.platform,
            request.urgency
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reactive meme generation failed: {str(e)}")

@router.post("/enhanced-memes/analyze-performance")
async def analyze_meme_performance_potential(
    meme_concept: str = Form(...),
    platform: Platform = Form(Platform.INSTAGRAM),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze potential performance of a meme concept before creation"""
    try:
        meme_service = EnhancedMemeGeneratorService(db)
        result = await meme_service.analyze_meme_performance_potential(
            meme_concept, platform
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meme performance analysis failed: {str(e)}")

# AI Short-Form Video Editing Endpoints
@router.post("/short-form-video/create")
async def create_short_form_video(
    file: UploadFile = File(...),
    request: ShortFormVideoRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create optimized short-form video from longer source video"""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        video_service = AIShortFormVideoService(db)
        result = await video_service.create_short_form_video(
            temp_path,
            request.platform,
            request.style,
            request.target_duration,
            request.add_captions,
            request.add_effects
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Short-form video creation failed: {str(e)}")

@router.post("/short-form-video/trend-based")
async def create_trend_based_video(
    request: TrendVideoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create video based on current trends and viral patterns"""
    try:
        video_service = AIShortFormVideoService(db)
        result = await video_service.create_trend_based_video(
            request.content_theme,
            request.trending_audio,
            request.platform,
            request.video_style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend-based video creation failed: {str(e)}")

@router.post("/short-form-video/hook-optimized")
async def create_hook_optimized_video(
    request: HookVideoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create video with AI-optimized hook for maximum retention"""
    try:
        video_service = AIShortFormVideoService(db)
        result = await video_service.create_hook_optimized_video(
            request.source_content,
            request.hook_style,
            request.platform,
            request.duration
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hook-optimized video creation failed: {str(e)}")

@router.post("/short-form-video/educational")
async def create_educational_short(
    request: EducationalVideoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create educational short-form video with optimal learning structure"""
    try:
        video_service = AIShortFormVideoService(db)
        result = await video_service.create_educational_short(
            request.topic,
            request.complexity_level,
            request.platform,
            request.format_style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Educational short creation failed: {str(e)}")

@router.post("/short-form-video/product-showcase")
async def create_product_showcase_video(
    request: ProductVideoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create product showcase video optimized for conversion"""
    try:
        video_service = AIShortFormVideoService(db)
        result = await video_service.create_product_showcase_video(
            request.product_info,
            request.showcase_style,
            request.platform,
            request.focus_benefits
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product showcase video creation failed: {str(e)}")

# Cross-service integration endpoints
@router.post("/multi-modal/complete-package")
async def create_complete_content_package(
    source_file: UploadFile = File(...),
    content_theme: str = Form(...),
    target_platforms: List[Platform] = Form(...),
    include_voiceover: bool = Form(True),
    include_memes: bool = Form(True),
    brand_voice: str = Form("casual"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create complete content package with video, voiceover, and memes"""
    try:
        temp_path = f"/tmp/{source_file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await source_file.read()
            buffer.write(content)
        
        results = {}
        
        # Create short-form videos for each platform
        video_service = AIShortFormVideoService(db)
        for platform in target_platforms:
            video_result = await video_service.create_short_form_video(
                temp_path, platform, "viral", 15, True, True
            )
            results[f"video_{platform.value}"] = video_result
        
        # Add voiceover if requested
        if include_voiceover:
            voiceover_service = AIVoiceoverService(db)
            voiceover_result = await voiceover_service.generate_voiceover(
                f"Content about {content_theme}", "alloy", "en", target_platforms[0]
            )
            results["voiceover"] = voiceover_result
        
        # Create memes if requested
        if include_memes:
            meme_service = EnhancedMemeGeneratorService(db)
            meme_result = await meme_service.generate_trending_meme(
                content_theme, brand_voice, target_platforms[0]
            )
            results["meme"] = meme_result
        
        return {
            "content_package": results,
            "theme": content_theme,
            "platforms": [p.value for p in target_platforms],
            "package_type": "complete_multi_modal"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete package creation failed: {str(e)}")