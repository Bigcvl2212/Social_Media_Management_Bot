"""
Pydantic schemas for monetization features
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.monetization import BrandType, CampaignType, CampaignStatus, CollaborationStatus, PaymentStatus


# Brand schemas
class BrandBase(BaseModel):
    """Base brand schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    website: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    industry: BrandType
    company_size: Optional[str] = Field(None, regex="^(startup|small|medium|large|enterprise)$")
    location: Optional[str] = Field(None, max_length=100)
    contact_email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    contact_phone: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=100)
    social_media_handles: Optional[Dict[str, str]] = None
    collaboration_budget: Optional[float] = Field(None, ge=0)
    preferred_platforms: Optional[List[str]] = None
    target_demographics: Optional[Dict[str, Any]] = None


class BrandCreate(BrandBase):
    """Schema for creating a brand"""
    pass


class BrandUpdate(BaseModel):
    """Schema for updating a brand"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    website: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    industry: Optional[BrandType] = None
    company_size: Optional[str] = Field(None, regex="^(startup|small|medium|large|enterprise)$")
    location: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[str] = Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$')
    contact_phone: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=100)
    social_media_handles: Optional[Dict[str, str]] = None
    collaboration_budget: Optional[float] = Field(None, ge=0)
    preferred_platforms: Optional[List[str]] = None
    target_demographics: Optional[Dict[str, Any]] = None


class Brand(BrandBase):
    """Full brand schema"""
    id: int
    user_id: int
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Campaign schemas
class CampaignBase(BaseModel):
    """Base campaign schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    campaign_type: CampaignType
    budget: float = Field(..., gt=0)
    target_platforms: List[str] = Field(..., min_items=1)
    target_audience: Optional[Dict[str, Any]] = None
    content_requirements: Optional[Dict[str, Any]] = None
    deliverables: Optional[Dict[str, Any]] = None
    start_date: datetime
    end_date: datetime
    application_deadline: Optional[datetime] = None
    target_metrics: Optional[Dict[str, Any]] = None
    payment_amount: Optional[float] = Field(None, ge=0)

    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    @validator('application_deadline')
    def application_deadline_before_start_date(cls, v, values):
        if v and 'start_date' in values and v >= values['start_date']:
            raise ValueError('application_deadline must be before start_date')
        return v


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign"""
    brand_id: int


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    campaign_type: Optional[CampaignType] = None
    status: Optional[CampaignStatus] = None
    budget: Optional[float] = Field(None, gt=0)
    target_platforms: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None
    content_requirements: Optional[Dict[str, Any]] = None
    deliverables: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    target_metrics: Optional[Dict[str, Any]] = None
    actual_metrics: Optional[Dict[str, Any]] = None
    payment_amount: Optional[float] = Field(None, ge=0)
    payment_status: Optional[PaymentStatus] = None
    payment_date: Optional[datetime] = None


class Campaign(CampaignBase):
    """Full campaign schema"""
    id: int
    brand_id: int
    status: CampaignStatus
    actual_metrics: Optional[Dict[str, Any]]
    payment_status: PaymentStatus
    payment_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Collaboration schemas
class CollaborationBase(BaseModel):
    """Base collaboration schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    deliverables: Dict[str, Any]
    compensation: Optional[float] = Field(None, ge=0)
    compensation_type: Optional[str] = Field(None, regex="^(fixed|per_post|revenue_share)$")
    content_requirements: Optional[Dict[str, Any]] = None
    platforms: List[str] = Field(..., min_items=1)
    start_date: datetime
    end_date: datetime

    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class CollaborationCreate(CollaborationBase):
    """Schema for creating a collaboration"""
    influencer_id: int
    brand_id: int
    campaign_id: Optional[int] = None


class CollaborationUpdate(BaseModel):
    """Schema for updating a collaboration"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[CollaborationStatus] = None
    deliverables: Optional[Dict[str, Any]] = None
    compensation: Optional[float] = Field(None, ge=0)
    compensation_type: Optional[str] = Field(None, regex="^(fixed|per_post|revenue_share)$")
    content_requirements: Optional[Dict[str, Any]] = None
    platforms: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    content_ids: Optional[List[int]] = None
    approval_status: Optional[str] = Field(None, regex="^(pending|approved|rejected)$")
    performance_metrics: Optional[Dict[str, Any]] = None
    terms_accepted: Optional[bool] = None


class Collaboration(CollaborationBase):
    """Full collaboration schema"""
    id: int
    influencer_id: int
    brand_id: int
    campaign_id: Optional[int]
    status: CollaborationStatus
    content_ids: Optional[List[int]]
    approval_status: str
    performance_metrics: Optional[Dict[str, Any]]
    contract_url: Optional[str]
    terms_accepted: bool
    terms_accepted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Affiliate Link schemas
class AffiliateLinkBase(BaseModel):
    """Base affiliate link schema"""
    name: str = Field(..., min_length=1, max_length=200)
    original_url: HttpUrl
    product_name: Optional[str] = Field(None, max_length=200)
    product_description: Optional[str] = Field(None, max_length=1000)
    product_image_url: Optional[HttpUrl] = None
    commission_rate: float = Field(..., ge=0, le=100)
    commission_type: str = Field(default="percentage", regex="^(percentage|fixed|tiered)$")
    commission_settings: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class AffiliateLinkCreate(AffiliateLinkBase):
    """Schema for creating an affiliate link"""
    brand_id: Optional[int] = None
    campaign_id: Optional[int] = None


class AffiliateLinkUpdate(BaseModel):
    """Schema for updating an affiliate link"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    original_url: Optional[HttpUrl] = None
    product_name: Optional[str] = Field(None, max_length=200)
    product_description: Optional[str] = Field(None, max_length=1000)
    product_image_url: Optional[HttpUrl] = None
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    commission_type: Optional[str] = Field(None, regex="^(percentage|fixed|tiered)$")
    commission_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class AffiliateLink(AffiliateLinkBase):
    """Full affiliate link schema"""
    id: int
    user_id: int
    brand_id: Optional[int]
    campaign_id: Optional[int]
    affiliate_code: str
    short_url: Optional[str]
    click_count: int
    conversion_count: int
    total_earnings: float
    last_clicked: Optional[datetime]
    is_active: bool
    analytics_data: Optional[Dict[str, Any]]
    conversion_rate: float
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Marketplace and reporting schemas
class BrandMarketplaceFilter(BaseModel):
    """Schema for filtering brands in marketplace"""
    industry: Optional[List[BrandType]] = None
    company_size: Optional[List[str]] = None
    location: Optional[str] = None
    min_budget: Optional[float] = Field(None, ge=0)
    max_budget: Optional[float] = Field(None, ge=0)
    platforms: Optional[List[str]] = None
    verified_only: bool = False


class CampaignMarketplaceFilter(BaseModel):
    """Schema for filtering campaigns in marketplace"""
    campaign_type: Optional[List[CampaignType]] = None
    status: Optional[List[CampaignStatus]] = None
    platforms: Optional[List[str]] = None
    min_budget: Optional[float] = Field(None, ge=0)
    max_budget: Optional[float] = Field(None, ge=0)
    industry: Optional[List[BrandType]] = None


class AffiliateLinkAnalytics(BaseModel):
    """Schema for affiliate link analytics"""
    link_id: int
    date_range: str
    total_clicks: int
    total_conversions: int
    total_earnings: float
    conversion_rate: float
    daily_stats: List[Dict[str, Any]]
    top_referrers: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class CollaborationAnalytics(BaseModel):
    """Schema for collaboration analytics"""
    collaboration_id: int
    total_reach: Optional[int]
    total_engagement: Optional[int]
    engagement_rate: Optional[float]
    click_through_rate: Optional[float]
    conversion_rate: Optional[float]
    platform_breakdown: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class MonetizationDashboard(BaseModel):
    """Schema for monetization dashboard data"""
    total_earnings: float
    active_collaborations: int
    pending_collaborations: int
    active_affiliate_links: int
    total_clicks: int
    total_conversions: int
    recent_activities: List[Dict[str, Any]]
    top_performing_links: List[Dict[str, Any]]
    upcoming_deadlines: List[Dict[str, Any]]