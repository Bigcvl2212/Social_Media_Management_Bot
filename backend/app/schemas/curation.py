"""
Pydantic schemas for content curation and inspiration board
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.curation import (
    CurationCollectionType, CurationItemType, CurationItemStatus
)


# Collection Schemas
class CurationCollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    collection_type: CurationCollectionType
    is_public: bool = False
    color_theme: Optional[str] = None
    tags: Optional[List[str]] = None
    auto_curate_trends: bool = False
    auto_curate_keywords: Optional[List[str]] = None


class CurationCollectionCreate(CurationCollectionBase):
    pass


class CurationCollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    color_theme: Optional[str] = None
    tags: Optional[List[str]] = None
    auto_curate_trends: Optional[bool] = None
    auto_curate_keywords: Optional[List[str]] = None


class CurationCollectionResponse(CurationCollectionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Item Schemas
class CurationItemBase(BaseModel):
    item_type: CurationItemType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: CurationItemStatus = CurationItemStatus.SAVED
    source_url: Optional[str] = None
    source_platform: Optional[str] = None
    thumbnail_url: Optional[str] = None
    item_data: Optional[Dict[str, Any]] = None
    user_notes: Optional[str] = None
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_tags: Optional[List[str]] = None


class CurationItemCreate(CurationItemBase):
    collection_id: int


class CurationItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[CurationItemStatus] = None
    source_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    item_data: Optional[Dict[str, Any]] = None
    user_notes: Optional[str] = None
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_tags: Optional[List[str]] = None


class CurationItemResponse(CurationItemBase):
    id: int
    collection_id: int
    ai_insights: Optional[Dict[str, Any]] = None
    viral_potential_score: Optional[int] = None
    times_used: int = 0
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Trend Watch Schemas
class TrendWatchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    keywords: List[str] = Field(..., min_items=1)
    platforms: List[str] = Field(..., min_items=1)
    regions: Optional[List[str]] = None
    is_active: bool = True
    alert_threshold: int = Field(1000, ge=1)
    notification_frequency: str = Field("daily", regex="^(hourly|daily|weekly)$")
    auto_save_to_collection_id: Optional[int] = None
    auto_save_threshold: int = Field(5000, ge=1)


class TrendWatchCreate(TrendWatchBase):
    pass


class TrendWatchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    keywords: Optional[List[str]] = Field(None, min_items=1)
    platforms: Optional[List[str]] = Field(None, min_items=1)
    regions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    alert_threshold: Optional[int] = Field(None, ge=1)
    notification_frequency: Optional[str] = Field(None, regex="^(hourly|daily|weekly)$")
    auto_save_to_collection_id: Optional[int] = None
    auto_save_threshold: Optional[int] = Field(None, ge=1)


class TrendWatchResponse(TrendWatchBase):
    id: int
    user_id: int
    last_check_at: Optional[datetime] = None
    total_alerts_sent: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Trend Alert Schemas
class TrendAlertResponse(BaseModel):
    id: int
    trend_watch_id: int
    trend_name: str
    platform: str
    alert_type: str
    current_volume: Optional[int] = None
    growth_rate: Optional[str] = None
    trend_data: Optional[Dict[str, Any]] = None
    is_read: bool = False
    is_dismissed: bool = False
    auto_saved_to_collection: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Content Discovery Schemas
class TrendingContentRequest(BaseModel):
    platforms: List[str] = Field(..., min_items=1)
    keywords: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    region: str = "global"
    time_range: str = Field("24h", regex="^(1h|6h|24h|7d|30d)$")


class TrendingContentResponse(BaseModel):
    platform: str
    trends: List[Dict[str, Any]]
    hashtags: List[Dict[str, Any]]
    audio_tracks: Optional[List[Dict[str, Any]]] = None
    viral_content: List[Dict[str, Any]]
    generated_at: datetime


# Quick Save Schemas
class QuickSaveRequest(BaseModel):
    url: str
    collection_id: int
    title: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class QuickSaveResponse(BaseModel):
    success: bool
    item_id: Optional[int] = None
    message: str
    auto_extracted_data: Optional[Dict[str, Any]] = None


# Inspiration Board Summary
class InspirationBoardSummary(BaseModel):
    total_collections: int
    total_items: int
    trending_items: List[CurationItemResponse]
    recent_additions: List[CurationItemResponse]
    active_trend_watches: int
    unread_alerts: int
    collections_by_type: Dict[str, int]


# Bulk Operations
class BulkItemOperation(BaseModel):
    item_ids: List[int] = Field(..., min_items=1)
    operation: str = Field(..., regex="^(move|delete|update_status|tag)$")
    target_collection_id: Optional[int] = None
    new_status: Optional[CurationItemStatus] = None
    tags_to_add: Optional[List[str]] = None
    tags_to_remove: Optional[List[str]] = None


class BulkOperationResponse(BaseModel):
    success: bool
    processed_items: int
    failed_items: int
    errors: Optional[List[str]] = None