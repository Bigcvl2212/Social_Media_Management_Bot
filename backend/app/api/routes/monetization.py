"""
API routes for monetization features including brand collaboration, campaigns, and affiliate marketing
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.monetization_service import MonetizationService
from app.schemas.monetization import (
    Brand, BrandCreate, BrandUpdate,
    Campaign, CampaignCreate, CampaignUpdate,
    Collaboration, CollaborationCreate, CollaborationUpdate,
    AffiliateLink, AffiliateLinkCreate, AffiliateLinkUpdate,
    BrandMarketplaceFilter, CampaignMarketplaceFilter,
    MonetizationDashboard
)

router = APIRouter(prefix="/api/v1/monetization", tags=["monetization"])


def get_monetization_service(db: Session = Depends(get_db)) -> MonetizationService:
    """Dependency to get monetization service"""
    return MonetizationService(db)


# Brand Management Routes
@router.post("/brands", response_model=Brand, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand_data: BrandCreate,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Create a new brand profile"""
    return service.create_brand(brand_data, current_user.id)


@router.get("/brands", response_model=List[Brand])
async def get_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get user's brand profiles"""
    return service.get_brands(user_id=current_user.id, skip=skip, limit=limit)


@router.get("/brands/marketplace", response_model=List[Brand])
async def search_brands_marketplace(
    industry: Optional[List[str]] = Query(None),
    company_size: Optional[List[str]] = Query(None),
    location: Optional[str] = Query(None),
    min_budget: Optional[float] = Query(None, ge=0),
    max_budget: Optional[float] = Query(None, ge=0),
    platforms: Optional[List[str]] = Query(None),
    verified_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Search brands in the collaboration marketplace"""
    filters = BrandMarketplaceFilter(
        industry=industry,
        company_size=company_size,
        location=location,
        min_budget=min_budget,
        max_budget=max_budget,
        platforms=platforms,
        verified_only=verified_only
    )
    return service.search_brands(filters, skip=skip, limit=limit)


@router.get("/brands/{brand_id}", response_model=Brand)
async def get_brand(
    brand_id: int,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get a specific brand profile"""
    brand = service.get_brand(brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    return brand


@router.put("/brands/{brand_id}", response_model=Brand)
async def update_brand(
    brand_id: int,
    brand_data: BrandUpdate,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Update a brand profile"""
    brand = service.update_brand(brand_id, brand_data, current_user.id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found or access denied"
        )
    return brand


@router.delete("/brands/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_id: int,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Delete a brand profile"""
    success = service.delete_brand(brand_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found or access denied"
        )


# Campaign Management Routes
@router.post("/campaigns", response_model=Campaign, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Create a new campaign"""
    # Verify user owns the brand
    brand = service.get_brand(campaign_data.brand_id, current_user.id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this brand"
        )
    
    return service.create_campaign(campaign_data)


@router.get("/campaigns", response_model=List[Campaign])
async def get_campaigns(
    brand_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get campaigns with optional brand filter"""
    if brand_id:
        # Verify user owns the brand
        brand = service.get_brand(brand_id, current_user.id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brand"
            )
    
    return service.get_campaigns(brand_id=brand_id, skip=skip, limit=limit)


@router.get("/campaigns/marketplace", response_model=List[Campaign])
async def search_campaigns_marketplace(
    campaign_type: Optional[List[str]] = Query(None),
    platforms: Optional[List[str]] = Query(None),
    min_budget: Optional[float] = Query(None, ge=0),
    max_budget: Optional[float] = Query(None, ge=0),
    industry: Optional[List[str]] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Search campaigns in the marketplace"""
    filters = CampaignMarketplaceFilter(
        campaign_type=campaign_type,
        platforms=platforms,
        min_budget=min_budget,
        max_budget=max_budget,
        industry=industry
    )
    return service.search_campaigns(filters, skip=skip, limit=limit)


@router.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get a specific campaign"""
    campaign = service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign


@router.put("/campaigns/{campaign_id}", response_model=Campaign)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Update a campaign"""
    campaign = service.update_campaign(campaign_id, campaign_data, current_user.id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found or access denied"
        )
    return campaign


# Collaboration Management Routes
@router.post("/collaborations", response_model=Collaboration, status_code=status.HTTP_201_CREATED)
async def create_collaboration(
    collaboration_data: CollaborationCreate,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Create a new collaboration"""
    # Only brand owners can create collaborations
    brand = service.get_brand(collaboration_data.brand_id, current_user.id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this brand"
        )
    
    return service.create_collaboration(collaboration_data)


@router.get("/collaborations", response_model=List[Collaboration])
async def get_collaborations(
    brand_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get collaborations for current user (as influencer or brand owner)"""
    if brand_id:
        # Verify user owns the brand
        brand = service.get_brand(brand_id, current_user.id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brand"
            )
        return service.get_collaborations(brand_id=brand_id, skip=skip, limit=limit)
    else:
        # Get collaborations where user is the influencer
        return service.get_collaborations(user_id=current_user.id, skip=skip, limit=limit)


@router.get("/collaborations/{collaboration_id}", response_model=Collaboration)
async def get_collaboration(
    collaboration_id: int,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get a specific collaboration"""
    collaboration = service.get_collaboration(collaboration_id)
    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration not found"
        )
    
    # Check if user has access (either influencer or brand owner)
    brand = service.get_brand(collaboration.brand_id, current_user.id)
    if collaboration.influencer_id != current_user.id and not brand:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this collaboration"
        )
    
    return collaboration


@router.put("/collaborations/{collaboration_id}", response_model=Collaboration)
async def update_collaboration(
    collaboration_id: int,
    collaboration_data: CollaborationUpdate,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Update a collaboration"""
    collaboration = service.update_collaboration(collaboration_id, collaboration_data, current_user.id)
    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration not found or access denied"
        )
    return collaboration


@router.post("/collaborations/{collaboration_id}/accept", response_model=Collaboration)
async def accept_collaboration(
    collaboration_id: int,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Accept a collaboration (influencer only)"""
    collaboration = service.accept_collaboration(collaboration_id, current_user.id)
    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration not found or cannot be accepted"
        )
    return collaboration


# Affiliate Link Management Routes
@router.post("/affiliate-links", response_model=AffiliateLink, status_code=status.HTTP_201_CREATED)
async def create_affiliate_link(
    link_data: AffiliateLinkCreate,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Create a new affiliate link"""
    return service.create_affiliate_link(link_data, current_user.id)


@router.get("/affiliate-links", response_model=List[AffiliateLink])
async def get_affiliate_links(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get user's affiliate links"""
    return service.get_affiliate_links(current_user.id, skip=skip, limit=limit)


@router.get("/affiliate-links/{link_id}", response_model=AffiliateLink)
async def get_affiliate_link(
    link_id: int,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get a specific affiliate link"""
    link = service.get_affiliate_link(link_id, current_user.id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Affiliate link not found"
        )
    return link


@router.put("/affiliate-links/{link_id}", response_model=AffiliateLink)
async def update_affiliate_link(
    link_id: int,
    link_data: AffiliateLinkUpdate,
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Update an affiliate link"""
    link = service.update_affiliate_link(link_id, link_data, current_user.id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Affiliate link not found"
        )
    return link


@router.post("/affiliate-links/{affiliate_code}/click")
async def track_affiliate_click(
    affiliate_code: str,
    referrer: Optional[str] = Query(None),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Track a click on an affiliate link (public endpoint)"""
    success = service.track_click(affiliate_code, referrer)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Affiliate link not found or expired"
        )
    return {"message": "Click tracked successfully"}


@router.post("/affiliate-links/{affiliate_code}/conversion")
async def track_affiliate_conversion(
    affiliate_code: str,
    conversion_value: float = Query(0.0, ge=0),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Track a conversion for an affiliate link (public endpoint)"""
    success = service.track_conversion(affiliate_code, conversion_value)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Affiliate link not found"
        )
    return {"message": "Conversion tracked successfully"}


# Analytics and Dashboard Routes
@router.get("/dashboard", response_model=MonetizationDashboard)
async def get_monetization_dashboard(
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get monetization dashboard data"""
    return service.get_monetization_dashboard(current_user.id)


@router.get("/analytics/affiliate-links")
async def get_affiliate_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    service: MonetizationService = Depends(get_monetization_service)
):
    """Get affiliate link analytics"""
    return service.get_affiliate_analytics(current_user.id, days)