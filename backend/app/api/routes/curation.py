"""
API routes for content curation and inspiration board
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.curation import CurationCollectionType, CurationItemType, CurationItemStatus
from app.models.social_account import SocialPlatform as Platform
from app.services.content_curation_service import ContentCurationService
from app.services.realtime_trend_monitoring_service import RealTimeTrendMonitoringService
from app.schemas.curation import (
    CurationCollectionCreate, CurationCollectionUpdate, CurationCollectionResponse,
    CurationItemCreate, CurationItemUpdate, CurationItemResponse,
    TrendWatchCreate, TrendWatchUpdate, TrendWatchResponse,
    TrendAlertResponse, InspirationBoardSummary,
    TrendingContentRequest, TrendingContentResponse,
    QuickSaveRequest, QuickSaveResponse,
    BulkItemOperation, BulkOperationResponse
)

router = APIRouter()


# Collection endpoints
@router.post("/collections", response_model=CurationCollectionResponse)
async def create_collection(
    collection_data: CurationCollectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new curation collection"""
    service = ContentCurationService(db)
    collection = await service.create_collection(collection_data, current_user.id)
    return collection


@router.get("/collections", response_model=List[CurationCollectionResponse])
async def list_collections(
    collection_type: Optional[CurationCollectionType] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's curation collections"""
    service = ContentCurationService(db)
    collections, total = await service.list_collections(current_user.id, collection_type, page, size)
    
    # Add items count to response
    collection_responses = []
    for collection in collections:
        collection_dict = collection.__dict__.copy()
        collection_dict["items_count"] = len(collection.items) if collection.items else 0
        collection_responses.append(CurationCollectionResponse(**collection_dict))
    
    return collection_responses


@router.get("/collections/{collection_id}", response_model=CurationCollectionResponse)
async def get_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get collection by ID"""
    service = ContentCurationService(db)
    collection = await service.get_collection_by_id(collection_id, current_user.id)
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    collection_dict = collection.__dict__.copy()
    collection_dict["items_count"] = len(collection.items) if collection.items else 0
    return CurationCollectionResponse(**collection_dict)


@router.put("/collections/{collection_id}", response_model=CurationCollectionResponse)
async def update_collection(
    collection_id: int,
    collection_data: CurationCollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a collection"""
    service = ContentCurationService(db)
    collection = await service.update_collection(collection_id, collection_data, current_user.id)
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    collection_dict = collection.__dict__.copy()
    collection_dict["items_count"] = len(collection.items) if collection.items else 0
    return CurationCollectionResponse(**collection_dict)


@router.delete("/collections/{collection_id}")
async def delete_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a collection"""
    service = ContentCurationService(db)
    success = await service.delete_collection(collection_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    return {"message": "Collection deleted successfully"}


# Item endpoints
@router.post("/items", response_model=CurationItemResponse)
async def add_item_to_collection(
    item_data: CurationItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add an item to a collection"""
    service = ContentCurationService(db)
    item = await service.add_item_to_collection(item_data, current_user.id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    return item


@router.get("/collections/{collection_id}/items", response_model=List[CurationItemResponse])
async def list_collection_items(
    collection_id: int,
    item_type: Optional[CurationItemType] = Query(None),
    status: Optional[CurationItemStatus] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List items in a collection"""
    service = ContentCurationService(db)
    items, total = await service.list_collection_items(
        collection_id, current_user.id, item_type, status, search, page, size
    )
    return items


@router.put("/items/{item_id}", response_model=CurationItemResponse)
async def update_item(
    item_id: int,
    item_data: CurationItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a curation item"""
    service = ContentCurationService(db)
    item = await service.update_item(item_id, item_data, current_user.id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a curation item"""
    service = ContentCurationService(db)
    success = await service.delete_item(item_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item deleted successfully"}


@router.post("/items/{item_id}/mark-used", response_model=CurationItemResponse)
async def mark_item_as_used(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark an item as used"""
    service = ContentCurationService(db)
    item = await service.mark_item_as_used(item_id, current_user.id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


# Trend monitoring endpoints
@router.post("/trend-watches", response_model=TrendWatchResponse)
async def create_trend_watch(
    watch_data: TrendWatchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new trend watch"""
    service = ContentCurationService(db)
    trend_watch = await service.create_trend_watch(watch_data, current_user.id)
    return trend_watch


@router.get("/trend-watches", response_model=List[TrendWatchResponse])
async def list_trend_watches(
    active_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's trend watches"""
    service = ContentCurationService(db)
    trend_watches = await service.list_trend_watches(current_user.id, active_only)
    return trend_watches


@router.get("/trend-alerts", response_model=List[TrendAlertResponse])
async def get_trend_alerts(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get trend alerts for user"""
    service = ContentCurationService(db)
    alerts, total = await service.get_trend_alerts(current_user.id, unread_only, page, size)
    return alerts


@router.post("/trend-alerts/{alert_id}/mark-read")
async def mark_alert_as_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a trend alert as read"""
    service = ContentCurationService(db)
    success = await service.mark_alert_as_read(alert_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert marked as read"}


# Real-time trend monitoring endpoints
@router.get("/realtime/hashtags")
async def get_realtime_hashtags(
    platforms: List[str] = Query(..., description="List of platforms to monitor"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time trending hashtags across platforms"""
    try:
        platform_enums = [Platform(p) for p in platforms]
        service = RealTimeTrendMonitoringService(db)
        hashtag_data = await service.monitor_trending_hashtags_realtime(platform_enums)
        return hashtag_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {str(e)}")


@router.get("/realtime/sounds")
async def get_realtime_sounds(
    platforms: List[str] = Query(..., description="List of platforms to monitor (TikTok, Instagram)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time trending sounds for TikTok and Instagram"""
    try:
        platform_enums = [Platform(p) for p in platforms]
        service = RealTimeTrendMonitoringService(db)
        sound_data = await service.monitor_trending_sounds_realtime(platform_enums)
        return sound_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {str(e)}")


@router.get("/realtime/viral-spikes")
async def detect_viral_spikes(
    platform: str = Query(..., description="Platform to monitor for viral spikes"),
    threshold: float = Query(2.0, description="Spike detection threshold multiplier"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect viral content spikes on a platform"""
    try:
        platform_enum = Platform(platform)
        service = RealTimeTrendMonitoringService(db)
        viral_spikes = await service.detect_viral_content_spikes(platform_enum, threshold)
        return {"platform": platform, "viral_spikes": viral_spikes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {str(e)}")


@router.get("/realtime/platform-insights")
async def get_platform_insights(
    platform: str = Query(..., description="Platform to get insights for"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive real-time insights for a platform"""
    try:
        platform_enum = Platform(platform)
        service = RealTimeTrendMonitoringService(db)
        insights = await service.get_real_time_platform_insights(platform_enum)
        return insights
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {str(e)}")


@router.post("/realtime/smart-alerts")
async def create_smart_alerts(
    keywords: List[str] = Query(..., description="Keywords to monitor"),
    platforms: List[str] = Query(..., description="Platforms to monitor"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create smart trend alerts based on keywords and platforms"""
    try:
        platform_enums = [Platform(p) for p in platforms]
        service = RealTimeTrendMonitoringService(db)
        alerts = await service.create_smart_trend_alerts(current_user.id, keywords, platform_enums)
        return {"alerts": alerts, "keywords_monitored": len(keywords), "platforms_monitored": len(platforms)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {str(e)}")


# Content discovery endpoints
@router.post("/discover-trending", response_model=List[TrendingContentResponse])
async def discover_trending_content(
    request: TrendingContentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Discover trending content across platforms"""
    service = ContentCurationService(db)
    trending_content = await service.discover_trending_content(request)
    return trending_content


@router.post("/quick-save", response_model=QuickSaveResponse)
async def quick_save_content(
    request: QuickSaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Quick save content from URL to collection"""
    service = ContentCurationService(db)
    result = await service.quick_save_content(request, current_user.id)
    return QuickSaveResponse(**result)


# Dashboard and summary endpoints
@router.get("/inspiration-board/summary", response_model=InspirationBoardSummary)
async def get_inspiration_board_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get inspiration board summary for dashboard"""
    service = ContentCurationService(db)
    summary = await service.get_inspiration_board_summary(current_user.id)
    return summary


# Bulk operations
@router.post("/items/bulk-operation", response_model=BulkOperationResponse)
async def bulk_operation_items(
    operation: BulkItemOperation,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform bulk operations on curation items"""
    service = ContentCurationService(db)
    result = await service.bulk_operation_items(operation, current_user.id)
    return BulkOperationResponse(**result)