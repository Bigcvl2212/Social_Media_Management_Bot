"""
Facebook Ads management routes — campaigns, ad sets, ads, audiences, reporting.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.facebook_ads_service import FacebookAdsService
from app.services.credential_resolver import get_facebook_credentials

router = APIRouter()


async def _ads(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FacebookAdsService:
    creds = await get_facebook_credentials(db, user_id=current_user.id)
    return FacebookAdsService(
        app_id=creds.app_id,
        app_secret=creds.app_secret,
        access_token=creds.page_token,
        ad_account_id=creds.ad_account_id,
        page_id=creds.page_id,
    )


# ── Request models ───────────────────────────────────────

class CampaignCreateRequest(BaseModel):
    name: str
    objective: str = "OUTCOME_LEADS"
    daily_budget_cents: int = 2000
    status: str = "PAUSED"

class AdSetCreateRequest(BaseModel):
    campaign_id: str
    name: str
    daily_budget_cents: int = 2000
    targeting: Optional[Dict[str, Any]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CreativeImageRequest(BaseModel):
    image_url: str
    headline: str
    body_text: str
    link_url: str
    call_to_action: str = "SIGN_UP"

class CreativeVideoRequest(BaseModel):
    video_url: str
    headline: str
    body_text: str
    link_url: str
    call_to_action: str = "SIGN_UP"

class AdCreateRequest(BaseModel):
    ad_set_id: str
    creative_id: str
    name: str
    status: str = "PAUSED"

class FullAdRequest(BaseModel):
    name: str
    daily_budget_cents: int = 2000
    image_url: str
    headline: str
    body_text: str
    link_url: str
    call_to_action: str = "SIGN_UP"
    objective: str = "OUTCOME_LEADS"

class CustomAudienceRequest(BaseModel):
    name: str
    description: str = ""

class AudienceEmailsRequest(BaseModel):
    audience_id: str
    emails: List[str]

class LookalikeRequest(BaseModel):
    source_audience_id: str
    country: str = "US"
    ratio: float = 0.01


# ── Campaigns ────────────────────────────────────────────

@router.post("/campaigns")
async def create_campaign(req: CampaignCreateRequest, ads: FacebookAdsService = Depends(_ads)):
    return ads.create_campaign(req.name, req.objective, req.daily_budget_cents, req.status)

@router.get("/campaigns")
async def list_campaigns(ads: FacebookAdsService = Depends(_ads), limit: int = Query(25, ge=1, le=100)):
    return ads.get_campaigns(limit=limit)

@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: str, ads: FacebookAdsService = Depends(_ads)):
    return ads.pause_campaign(campaign_id)

@router.post("/campaigns/{campaign_id}/activate")
async def activate_campaign(campaign_id: str, ads: FacebookAdsService = Depends(_ads)):
    return ads.activate_campaign(campaign_id)


# ── Ad Sets ──────────────────────────────────────────────

@router.post("/ad-sets")
async def create_ad_set(req: AdSetCreateRequest, ads: FacebookAdsService = Depends(_ads)):
    return ads.create_ad_set(
        campaign_id=req.campaign_id,
        name=req.name,
        daily_budget_cents=req.daily_budget_cents,
        targeting=req.targeting,
        start_date=req.start_date,
        end_date=req.end_date,
    )


# ── Creatives ────────────────────────────────────────────

@router.post("/creatives/image")
async def create_image_creative(req: CreativeImageRequest, ads: FacebookAdsService = Depends(_ads)):
    return ads.create_image_creative(
        image_url=req.image_url,
        headline=req.headline,
        body_text=req.body_text,
        link_url=req.link_url,
        call_to_action=req.call_to_action,
    )

@router.post("/creatives/video")
async def create_video_creative(req: CreativeVideoRequest, ads: FacebookAdsService = Depends(_ads)):
    return ads.create_video_creative(
        video_url=req.video_url,
        headline=req.headline,
        body_text=req.body_text,
        link_url=req.link_url,
        call_to_action=req.call_to_action,
    )


# ── Ads ──────────────────────────────────────────────────

@router.post("/ads")
async def create_ad(req: AdCreateRequest, ads: FacebookAdsService = Depends(_ads)):
    return ads.create_ad(req.ad_set_id, req.creative_id, req.name, req.status)

@router.post("/ads/full")
async def create_full_ad(req: FullAdRequest, ads: FacebookAdsService = Depends(_ads)):
    """One-shot: campaign + ad set + creative + ad."""
    return ads.create_full_ad(
        name=req.name,
        daily_budget_cents=req.daily_budget_cents,
        image_url=req.image_url,
        headline=req.headline,
        body_text=req.body_text,
        link_url=req.link_url,
        call_to_action=req.call_to_action,
        objective=req.objective,
    )


# ── Audiences ────────────────────────────────────────────

@router.post("/audiences/custom")
async def create_custom_audience(req: CustomAudienceRequest, ads: FacebookAdsService = Depends(_ads)):
    return ads.create_custom_audience(req.name, req.description)

@router.post("/audiences/emails")
async def add_emails(req: AudienceEmailsRequest, ads: FacebookAdsService = Depends(_ads)):
    return ads.add_emails_to_audience(req.audience_id, req.emails)

@router.post("/audiences/lookalike")
async def create_lookalike(req: LookalikeRequest, ads: FacebookAdsService = Depends(_ads)):
    return ads.create_lookalike_audience(req.source_audience_id, req.country, req.ratio)


# ── Reporting ────────────────────────────────────────────

@router.get("/campaigns/{campaign_id}/insights")
async def campaign_insights(
    campaign_id: str,
    ads: FacebookAdsService = Depends(_ads),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    return ads.get_campaign_insights(campaign_id, date_from=date_from, date_to=date_to)

@router.get("/spend")
async def account_spend(ads: FacebookAdsService = Depends(_ads)):
    return ads.get_account_spend()
