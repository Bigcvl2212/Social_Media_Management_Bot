"""
Pydantic schemas for content management API
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.content import ContentType, ContentStatus, ScheduleStatus
from app.models.social_account import SocialPlatform


class ContentBase(BaseModel):
    """Base content schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: ContentType
    tags: Optional[List[str]] = []
    hashtags: Optional[List[str]] = []
    mentions: Optional[List[str]] = []


class ContentCreate(ContentBase):
    """Schema for creating new content"""
    pass


class ContentUpdate(BaseModel):
    """Schema for updating content"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ContentStatus] = None
    tags: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None


class ContentResponse(ContentBase):
    """Schema for content API responses"""
    id: int
    created_by: int
    status: ContentStatus
    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None
    ai_generated: bool = False
    ai_metadata: Optional[Dict[str, Any]] = None
    platform_variants: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContentListResponse(BaseModel):
    """Schema for paginated content list"""
    items: List[ContentResponse]
    total: int
    page: int
    size: int
    pages: int


class ContentScheduleBase(BaseModel):
    """Base content schedule schema"""
    scheduled_time: datetime
    caption: Optional[str] = None
    platform_specific_data: Optional[Dict[str, Any]] = None


class ContentScheduleCreate(ContentScheduleBase):
    """Schema for creating content schedule"""
    content_id: int
    social_account_id: int


class ContentScheduleUpdate(BaseModel):
    """Schema for updating content schedule"""
    scheduled_time: Optional[datetime] = None
    caption: Optional[str] = None
    platform_specific_data: Optional[Dict[str, Any]] = None
    status: Optional[ScheduleStatus] = None


class ContentScheduleResponse(ContentScheduleBase):
    """Schema for content schedule API responses"""
    id: int
    content_id: int
    social_account_id: int
    status: ScheduleStatus
    posted_at: Optional[datetime] = None
    platform_post_id: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContentScheduleListResponse(BaseModel):
    """Schema for paginated content schedule list"""
    items: List[ContentScheduleResponse]
    total: int
    page: int
    size: int
    pages: int


class CalendarEventResponse(BaseModel):
    """Schema for calendar view of scheduled content"""
    id: int
    title: str
    content_type: ContentType
    scheduled_time: datetime
    status: ScheduleStatus
    platform: SocialPlatform
    content_id: int
    social_account_id: int
    thumbnail_path: Optional[str] = None


class BulkScheduleRequest(BaseModel):
    """Schema for bulk scheduling content"""
    content_ids: List[int]
    social_account_ids: List[int]
    schedules: List[datetime]
    caption_template: Optional[str] = None


class ContentStatsResponse(BaseModel):
    """Schema for content statistics"""
    total_content: int
    by_type: Dict[ContentType, int]
    by_status: Dict[ContentStatus, int]
    recent_uploads: int
    ai_generated_count: int