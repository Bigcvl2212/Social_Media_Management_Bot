"""
Advanced content management routes with AI-powered features and CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime, timedelta
import math

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.content import ContentType, ContentStatus, ScheduleStatus
from app.models.social_account import SocialPlatform as Platform
from app.services.content_service import ContentService
from app.services.content_search_service import ContentSearchService
from app.services.content_generation_service import ContentGenerationService
from app.services.content_editing_service import ContentEditingService
from app.services.trend_analysis_service import TrendAnalysisService
from app.schemas.content import (
    ContentCreate, ContentUpdate, ContentResponse, ContentListResponse,
    ContentScheduleCreate, ContentScheduleUpdate, ContentScheduleResponse,
    CalendarEventResponse, ContentStatsResponse
)

router = APIRouter()

# Pydantic models for request/response
class ContentSearchRequest(BaseModel):
    platform: Platform
    topic: Optional[str] = None
    region: str = "global"
    timeframe_days: int = 7

class ContentGenerationRequest(BaseModel):
    prompt: str
    platform: Platform
    content_type: str = "post"
    style: str = "engaging"
    target_audience: Optional[str] = None

class ImageGenerationRequest(BaseModel):
    prompt: str
    platform: Platform
    style: str = "modern"
    dimensions: Optional[tuple] = None

class VideoGenerationRequest(BaseModel):
    concept: str
    platform: Platform
    duration: Optional[int] = None
    style: str = "dynamic"

class ContentEditingRequest(BaseModel):
    content_path: str
    platform: Platform
    edit_style: str = "viral"
    target_duration: Optional[int] = None

class TrendAnalysisRequest(BaseModel):
    platform: Platform
    timeframe_days: int = 7

class ViralPredictionRequest(BaseModel):
    content_description: str
    platform: Platform
    content_type: ContentType
    posting_time: Optional[datetime] = None

# Content Search and Ideation Endpoints
@router.get("/search/trending")
async def search_trending_topics(
    platform: Platform,
    region: str = "global",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search for trending topics on specific platforms"""
    try:
        search_service = ContentSearchService(db)
        trends = await search_service.search_trending_topics(platform, region)
        return {"trends": trends, "platform": platform.value, "region": region}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")

@router.post("/search/ideas")
async def generate_content_ideas(
    request: ContentSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI-powered content ideas based on topics and platform"""
    try:
        search_service = ContentSearchService(db)
        ideas = await search_service.generate_content_ideas(
            request.topic or "general content",
            request.platform,
            "General audience"
        )
        return {"ideas": ideas, "platform": request.platform.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ideas: {str(e)}")

@router.get("/search/viral")
async def search_viral_content(
    platform: Platform,
    timeframe: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search for viral content patterns on platforms"""
    try:
        search_service = ContentSearchService(db)
        viral_content = await search_service.search_viral_content(platform, timeframe)
        return {"viral_content": viral_content, "platform": platform.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search viral content: {str(e)}")

@router.post("/search/hashtags")
async def suggest_hashtags(
    content_description: str = Form(...),
    platform: Platform = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """AI-powered hashtag suggestions based on content and platform"""
    try:
        search_service = ContentSearchService(db)
        hashtags = await search_service.suggest_hashtags(content_description, platform)
        return {"hashtags": hashtags, "platform": platform.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suggest hashtags: {str(e)}")

# Content Generation Endpoints
@router.post("/generate/text")
async def generate_text_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI-powered text content optimized for specific platforms"""
    try:
        generation_service = ContentGenerationService(db)
        result = await generation_service.generate_text_content(
            request.prompt,
            request.platform,
            request.content_type,
            request.style,
            request.target_audience
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@router.post("/generate/image")
async def generate_image_content(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI-powered images with platform-specific optimizations"""
    try:
        generation_service = ContentGenerationService(db)
        result = await generation_service.generate_image_content(
            request.prompt,
            request.platform,
            request.style,
            request.dimensions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.post("/generate/video")
async def generate_video_content(
    request: VideoGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI-powered video content with platform optimization"""
    try:
        generation_service = ContentGenerationService(db)
        result = await generation_service.generate_video_content(
            request.concept,
            request.platform,
            request.duration,
            request.style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@router.post("/generate/meme")
async def generate_meme_content(
    text: str = Form(...),
    template: str = Form("auto"),
    platform: Platform = Form(Platform.INSTAGRAM),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate meme content with text overlay"""
    try:
        generation_service = ContentGenerationService(db)
        result = await generation_service.generate_meme_content(text, template, platform)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meme generation failed: {str(e)}")

@router.post("/generate/carousel")
async def generate_carousel_content(
    topic: str = Form(...),
    platform: Platform = Form(Platform.INSTAGRAM),
    slide_count: int = Form(5),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate carousel/slideshow content for educational or storytelling"""
    try:
        generation_service = ContentGenerationService(db)
        result = await generation_service.generate_carousel_content(topic, platform, slide_count)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Carousel generation failed: {str(e)}")

# Content Editing Endpoints
@router.post("/edit/video")
async def edit_video_for_platform(
    file: UploadFile = File(...),
    platform: Platform = Form(...),
    edit_style: str = Form("viral"),
    target_duration: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Edit video with platform-specific optimizations and viral techniques"""
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        editing_service = ContentEditingService(db)
        result = await editing_service.edit_video_for_platform(
            temp_path, platform, edit_style, target_duration
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video editing failed: {str(e)}")

@router.post("/edit/smart-crop")
async def apply_smart_crop(
    file: UploadFile = File(...),
    target_platform: Platform = Form(...),
    crop_style: str = Form("smart"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Apply intelligent cropping with AI-powered focus detection"""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        editing_service = ContentEditingService(db)
        result = await editing_service.apply_smart_crop(temp_path, target_platform, crop_style)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart crop failed: {str(e)}")

@router.post("/edit/captions")
async def add_captions_and_subtitles(
    file: UploadFile = File(...),
    platform: Platform = Form(...),
    style: str = Form("auto"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add AI-generated captions and subtitles optimized for platform"""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        editing_service = ContentEditingService(db)
        result = await editing_service.add_captions_and_subtitles(temp_path, platform, style)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Caption generation failed: {str(e)}")

@router.post("/edit/viral-effects")
async def apply_viral_effects(
    file: UploadFile = File(...),
    content_type: ContentType = Form(...),
    platform: Platform = Form(...),
    effect_style: str = Form("trending"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Apply viral effects and filters based on current trends"""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        editing_service = ContentEditingService(db)
        result = await editing_service.apply_viral_effects(temp_path, content_type, platform, effect_style)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Effect application failed: {str(e)}")

@router.post("/edit/optimize-virality")
async def optimize_for_virality(
    file: UploadFile = File(...),
    content_type: ContentType = Form(...),
    platform: Platform = Form(...),
    target_audience: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Apply AI-powered optimizations to maximize viral potential"""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        editing_service = ContentEditingService(db)
        result = await editing_service.optimize_for_virality(
            temp_path, content_type, platform, target_audience
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virality optimization failed: {str(e)}")

# Trend Analysis Endpoints
@router.post("/trends/analyze")
async def analyze_platform_trends(
    request: TrendAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze current trends on a specific platform"""
    try:
        trend_service = TrendAnalysisService(db)
        analysis = await trend_service.analyze_platform_trends(
            request.platform, request.timeframe_days
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

@router.post("/trends/predict-viral")
async def predict_viral_potential(
    request: ViralPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Predict viral potential of content before creation"""
    try:
        trend_service = TrendAnalysisService(db)
        prediction = await trend_service.predict_viral_potential(
            request.content_description,
            request.platform,
            request.content_type,
            request.posting_time
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Viral prediction failed: {str(e)}")

@router.get("/trends/posting-schedule")
async def get_optimal_posting_schedule(
    platform: Platform,
    target_audience: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate optimal posting schedule based on audience and trends"""
    try:
        trend_service = TrendAnalysisService(db)
        schedule = await trend_service.get_optimal_posting_schedule(
            platform, target_audience
        )
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule optimization failed: {str(e)}")

@router.post("/trends/competitor-analysis")
async def analyze_competitor_strategies(
    competitor_handles: List[str],
    platform: Platform,
    analysis_depth: str = "comprehensive",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze competitor content strategies and identify opportunities"""
    try:
        trend_service = TrendAnalysisService(db)
        analysis = await trend_service.analyze_competitor_strategies(
            competitor_handles, platform, analysis_depth
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Competitor analysis failed: {str(e)}")

@router.get("/trends/emerging")
async def identify_emerging_trends(
    platforms: Optional[List[Platform]] = None,
    categories: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Identify emerging trends before they go mainstream"""
    try:
        trend_service = TrendAnalysisService(db)
        trends = await trend_service.identify_emerging_trends(platforms, categories)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emerging trend identification failed: {str(e)}")

@router.post("/trends/content-calendar")
async def generate_content_calendar(
    platform: Platform,
    duration_weeks: int = 4,
    content_mix: Optional[Dict[str, float]] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI-powered content calendar based on trends and optimization"""
    try:
        trend_service = TrendAnalysisService(db)
        calendar = await trend_service.generate_content_calendar(
            platform, duration_weeks, content_mix
        )
        return calendar
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content calendar generation failed: {str(e)}")

# Legacy endpoints (kept for backward compatibility)
@router.get("/", response_model=ContentListResponse)
async def list_content(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    content_type: Optional[ContentType] = None,
    status: Optional[ContentStatus] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's content with pagination and filters"""
    try:
        content_service = ContentService(db)
        content_list, total = await content_service.list_content(
            user_id=current_user.id,
            page=page,
            size=size,
            content_type=content_type,
            status=status,
            search=search
        )
        
        return ContentListResponse(
            items=[ContentResponse.model_validate(content) for content in content_list],
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content: {str(e)}")


@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new content"""
    try:
        content_service = ContentService(db)
        content = await content_service.create_content(content_data, current_user.id)
        return ContentResponse.model_validate(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create content: {str(e)}")


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific content by ID"""
    try:
        content_service = ContentService(db)
        content = await content_service.get_content_by_id(content_id, current_user.id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return ContentResponse.model_validate(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content: {str(e)}")


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_data: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update content"""
    try:
        content_service = ContentService(db)
        content = await content_service.update_content(content_id, content_data, current_user.id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return ContentResponse.model_validate(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update content: {str(e)}")


@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete content"""
    try:
        content_service = ContentService(db)
        success = await content_service.delete_content(content_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Content not found")
        return {"message": "Content deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete content: {str(e)}")


# Content upload endpoints
@router.post("/upload", response_model=ContentResponse)
async def upload_content(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    content_type: ContentType = Form(...),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    hashtags: Optional[str] = Form(None),  # Comma-separated hashtags
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload content file and create content record"""
    try:
        content_service = ContentService(db)
        
        # Read file content
        file_content = await file.read()
        
        # Save uploaded file
        file_path = await content_service.save_uploaded_file(
            file_content, file.filename or "unknown", current_user.id
        )
        
        # Parse tags and hashtags
        tag_list = [tag.strip() for tag in (tags or "").split(",") if tag.strip()]
        hashtag_list = [tag.strip() for tag in (hashtags or "").split(",") if tag.strip()]
        
        # Create content record
        content_data = ContentCreate(
            title=title,
            description=description,
            content_type=content_type,
            tags=tag_list,
            hashtags=hashtag_list
        )
        
        content = await content_service.create_content(
            content_data, current_user.id, file_path
        )
        
        return ContentResponse.model_validate(content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# Content scheduling endpoints
@router.post("/schedule", response_model=ContentScheduleResponse)
async def schedule_content(
    schedule_data: ContentScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Schedule content for posting"""
    try:
        content_service = ContentService(db)
        schedule = await content_service.schedule_content(schedule_data, current_user.id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Content or social account not found")
        return ContentScheduleResponse.model_validate(schedule)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule content: {str(e)}")


@router.get("/schedule/calendar")
async def get_calendar_events(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get calendar events for scheduled content"""
    try:
        content_service = ContentService(db)
        events = await content_service.get_calendar_events(
            current_user.id, start_date, end_date
        )
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar events: {str(e)}")


@router.put("/schedule/{schedule_id}", response_model=ContentScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ContentScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update content schedule"""
    try:
        content_service = ContentService(db)
        schedule = await content_service.update_schedule(schedule_id, schedule_data, current_user.id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return ContentScheduleResponse.model_validate(schedule)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {str(e)}")


@router.delete("/schedule/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete content schedule"""
    try:
        content_service = ContentService(db)
        success = await content_service.delete_schedule(schedule_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return {"message": "Schedule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete schedule: {str(e)}")


@router.get("/stats", response_model=ContentStatsResponse)
async def get_content_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get content statistics for dashboard"""
    try:
        content_service = ContentService(db)
        stats = await content_service.get_content_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content stats: {str(e)}")