"""
Facebook Ads Manager Service
Full ad lifecycle via the Facebook Marketing API (facebook-business SDK).
Create campaigns, ad sets, ads, manage budgets, targeting, and reporting.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.adobjects.targeting import Targeting

from app.core.config import settings

import logging
logger = logging.getLogger(__name__)


class FacebookAdsService:
    """Facebook Marketing API client.  Pass explicit credentials for multi-tenant,
    or omit to fall back to .env values (owner's account)."""

    def __init__(
        self,
        app_id: str = "",
        app_secret: str = "",
        access_token: str = "",
        ad_account_id: str = "",
        page_id: str = "",
    ):
        self.app_id = app_id or settings.FACEBOOK_APP_ID or ""
        self.app_secret = app_secret or settings.FACEBOOK_APP_SECRET or ""
        self.access_token = access_token or settings.FACEBOOK_PAGE_ACCESS_TOKEN or ""
        self.ad_account_id = ad_account_id or settings.FACEBOOK_AD_ACCOUNT_ID or ""
        self.page_id = page_id or settings.FACEBOOK_PAGE_ID or ""

        if not self.ad_account_id:
            logger.warning("FACEBOOK_AD_ACCOUNT_ID not set — ads features disabled")
            self._enabled = False
            return

        # Ensure act_ prefix
        if not self.ad_account_id.startswith("act_"):
            self.ad_account_id = f"act_{self.ad_account_id}"

        FacebookAdsApi.init(
            app_id=self.app_id,
            app_secret=self.app_secret,
            access_token=self.access_token,
        )
        self.account = AdAccount(self.ad_account_id)
        self._enabled = True

    @property
    def enabled(self) -> bool:
        return self._enabled

    # ════════════════════════════════════════════════════════
    #  CAMPAIGNS
    # ════════════════════════════════════════════════════════

    def create_campaign(
        self,
        name: str,
        objective: str = "OUTCOME_LEADS",
        daily_budget_cents: int = 2000,
        status: str = "PAUSED",
        special_ad_categories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new ad campaign.
        Objectives: OUTCOME_AWARENESS, OUTCOME_TRAFFIC, OUTCOME_ENGAGEMENT,
                    OUTCOME_LEADS, OUTCOME_SALES, OUTCOME_APP_PROMOTION
        """
        params = {
            "name": name,
            "objective": objective,
            "status": status,
            "special_ad_categories": special_ad_categories or [],
            "daily_budget": str(daily_budget_cents),
        }
        campaign = self.account.create_campaign(fields=[], params=params)
        logger.info(f"Created campaign: {campaign['id']} — {name}")
        return {"campaign_id": campaign["id"], "name": name, "objective": objective, "status": status}

    def get_campaigns(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all campaigns in the ad account."""
        fields = [
            Campaign.Field.id,
            Campaign.Field.name,
            Campaign.Field.objective,
            Campaign.Field.status,
            Campaign.Field.daily_budget,
            Campaign.Field.lifetime_budget,
            Campaign.Field.created_time,
            Campaign.Field.start_time,
            Campaign.Field.stop_time,
        ]
        params = {}
        if status_filter:
            params["filtering"] = [{"field": "status", "operator": "EQUAL", "value": status_filter}]
        campaigns = self.account.get_campaigns(fields=fields, params=params)
        return [dict(c) for c in campaigns]

    def update_campaign(self, campaign_id: str, **kwargs) -> Dict[str, Any]:
        """Update campaign fields (name, status, daily_budget, etc.)."""
        campaign = Campaign(campaign_id)
        campaign.api_update(params=kwargs)
        return {"campaign_id": campaign_id, "updated": list(kwargs.keys())}

    def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        return self.update_campaign(campaign_id, status="PAUSED")

    def resume_campaign(self, campaign_id: str) -> Dict[str, Any]:
        return self.update_campaign(campaign_id, status="ACTIVE")

    def delete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        campaign = Campaign(campaign_id)
        campaign.api_delete()
        return {"campaign_id": campaign_id, "status": "deleted"}

    # ════════════════════════════════════════════════════════
    #  AD SETS (targeting + budget + schedule)
    # ════════════════════════════════════════════════════════

    def create_ad_set(
        self,
        name: str,
        campaign_id: str,
        daily_budget_cents: int = 1000,
        optimization_goal: str = "LEAD_GENERATION",
        billing_event: str = "IMPRESSIONS",
        targeting: Optional[Dict[str, Any]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        status: str = "PAUSED",
    ) -> Dict[str, Any]:
        """Create an ad set with targeting and budget."""
        # Default targeting: Fond du Lac area, 18-65, fitness interests
        if targeting is None:
            targeting = self._default_gym_targeting()

        params: Dict[str, Any] = {
            "name": name,
            "campaign_id": campaign_id,
            "daily_budget": str(daily_budget_cents),
            "optimization_goal": optimization_goal,
            "billing_event": billing_event,
            "targeting": targeting,
            "status": status,
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        adset = self.account.create_ad_set(fields=[], params=params)
        logger.info(f"Created ad set: {adset['id']} — {name}")
        return {"adset_id": adset["id"], "name": name, "campaign_id": campaign_id}

    def _default_gym_targeting(self) -> Dict[str, Any]:
        """Default targeting for Anytime Fitness Fond du Lac."""
        return {
            "geo_locations": {
                "cities": [
                    {"key": "2428870", "name": "Fond du Lac", "region": "Wisconsin", "country": "US", "radius": 15, "distance_unit": "mile"}
                ],
            },
            "age_min": 18,
            "age_max": 65,
            "interests": [
                {"id": "6003107902433", "name": "Physical fitness"},
                {"id": "6003659420716", "name": "Gym"},
                {"id": "6003384248805", "name": "Weight training"},
                {"id": "6003327847662", "name": "Running"},
                {"id": "6003253385455", "name": "Yoga"},
                {"id": "6003349442805", "name": "Physical exercise"},
            ],
            "publisher_platforms": ["facebook"],
            "facebook_positions": ["feed", "video_feeds", "instant_article", "marketplace"],
        }

    def get_ad_sets(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List ad sets, optionally filtered by campaign."""
        fields = [
            AdSet.Field.id,
            AdSet.Field.name,
            AdSet.Field.campaign_id,
            AdSet.Field.daily_budget,
            AdSet.Field.status,
            AdSet.Field.optimization_goal,
            AdSet.Field.targeting,
            AdSet.Field.start_time,
            AdSet.Field.end_time,
        ]
        params = {}
        if campaign_id:
            params["filtering"] = [{"field": "campaign.id", "operator": "EQUAL", "value": campaign_id}]
        adsets = self.account.get_ad_sets(fields=fields, params=params)
        return [dict(a) for a in adsets]

    def update_ad_set(self, adset_id: str, **kwargs) -> Dict[str, Any]:
        adset = AdSet(adset_id)
        adset.api_update(params=kwargs)
        return {"adset_id": adset_id, "updated": list(kwargs.keys())}

    def pause_ad_set(self, adset_id: str) -> Dict[str, Any]:
        return self.update_ad_set(adset_id, status="PAUSED")

    # ════════════════════════════════════════════════════════
    #  ADS + CREATIVES
    # ════════════════════════════════════════════════════════

    def upload_ad_image(self, image_path: str) -> str:
        """Upload an image and return the image hash."""
        image = self.account.create_ad_image(
            fields=[],
            params={},
            files={"filename": image_path},
        )
        image_hash = image["images"]["filename"]["hash"]
        logger.info(f"Uploaded ad image: {image_hash}")
        return image_hash

    def create_ad_creative(
        self,
        name: str,
        image_hash: str,
        headline: str,
        primary_text: str,
        description: str = "",
        link_url: str = "",
        cta_type: str = "LEARN_MORE",
    ) -> Dict[str, Any]:
        """Create an ad creative with image, copy, and CTA."""
        link = link_url or f"https://www.anytimefitness.com/gyms/3153/fond-du-lac-wi-54935/"
        params = {
            "name": name,
            "object_story_spec": {
                "page_id": self.page_id,
                "link_data": {
                    "image_hash": image_hash,
                    "link": link,
                    "message": primary_text,
                    "name": headline,
                    "description": description,
                    "call_to_action": {
                        "type": cta_type,
                        "value": {"link": link},
                    },
                },
            },
        }
        creative = self.account.create_ad_creative(fields=[], params=params)
        logger.info(f"Created ad creative: {creative['id']}")
        return {"creative_id": creative["id"], "name": name}

    def create_video_ad_creative(
        self,
        name: str,
        video_id: str,
        headline: str,
        primary_text: str,
        description: str = "",
        link_url: str = "",
        cta_type: str = "LEARN_MORE",
        thumbnail_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a video ad creative."""
        link = link_url or f"https://www.anytimefitness.com/gyms/3153/fond-du-lac-wi-54935/"
        video_data: Dict[str, Any] = {
            "video_id": video_id,
            "link": link,
            "message": primary_text,
            "name": headline,
            "description": description,
            "call_to_action": {
                "type": cta_type,
                "value": {"link": link},
            },
        }
        if thumbnail_url:
            video_data["image_url"] = thumbnail_url

        params = {
            "name": name,
            "object_story_spec": {
                "page_id": self.page_id,
                "video_data": video_data,
            },
        }
        creative = self.account.create_ad_creative(fields=[], params=params)
        logger.info(f"Created video ad creative: {creative['id']}")
        return {"creative_id": creative["id"], "name": name}

    def create_ad(
        self,
        name: str,
        adset_id: str,
        creative_id: str,
        status: str = "PAUSED",
    ) -> Dict[str, Any]:
        """Create an ad linking a creative to an ad set."""
        params = {
            "name": name,
            "adset_id": adset_id,
            "creative": {"creative_id": creative_id},
            "status": status,
        }
        ad = self.account.create_ad(fields=[], params=params)
        logger.info(f"Created ad: {ad['id']} in adset {adset_id}")
        return {"ad_id": ad["id"], "name": name, "adset_id": adset_id, "creative_id": creative_id}

    def get_ads(self, adset_id: Optional[str] = None) -> List[Dict[str, Any]]:
        fields = [Ad.Field.id, Ad.Field.name, Ad.Field.adset_id, Ad.Field.status, Ad.Field.creative]
        params = {}
        if adset_id:
            params["filtering"] = [{"field": "adset.id", "operator": "EQUAL", "value": adset_id}]
        ads = self.account.get_ads(fields=fields, params=params)
        return [dict(a) for a in ads]

    def pause_ad(self, ad_id: str) -> Dict[str, Any]:
        ad = Ad(ad_id)
        ad.api_update(params={"status": "PAUSED"})
        return {"ad_id": ad_id, "status": "PAUSED"}

    # ════════════════════════════════════════════════════════
    #  AUDIENCES
    # ════════════════════════════════════════════════════════

    def create_custom_audience(
        self,
        name: str,
        description: str = "",
        subtype: str = "CUSTOM",
    ) -> Dict[str, Any]:
        """Create a custom audience (for email list uploads, etc.)."""
        params = {
            "name": name,
            "subtype": subtype,
            "description": description,
            "customer_file_source": "USER_PROVIDED_ONLY",
        }
        audience = self.account.create_custom_audience(fields=[], params=params)
        logger.info(f"Created custom audience: {audience['id']}")
        return {"audience_id": audience["id"], "name": name}

    def add_emails_to_audience(self, audience_id: str, emails: List[str]) -> Dict[str, Any]:
        """Add hashed emails to a custom audience for targeting."""
        audience = CustomAudience(audience_id)
        # Facebook requires SHA-256 hashed, lowercased, trimmed emails
        hashed = [hashlib.sha256(e.strip().lower().encode()).hexdigest() for e in emails]
        schema = ["EMAIL_SHA256"]
        data = [[h] for h in hashed]
        result = audience.add_users(schema=schema, users=data)
        return {"audience_id": audience_id, "num_added": len(emails), "result": str(result)}

    def create_lookalike_audience(
        self,
        name: str,
        source_audience_id: str,
        country: str = "US",
        ratio: float = 0.01,
    ) -> Dict[str, Any]:
        """Create a lookalike audience from an existing custom audience."""
        params = {
            "name": name,
            "subtype": "LOOKALIKE",
            "origin_audience_id": source_audience_id,
            "lookalike_spec": json.dumps({
                "type": "similarity",
                "country": country,
                "ratio": ratio,
            }),
        }
        audience = self.account.create_custom_audience(fields=[], params=params)
        return {"audience_id": audience["id"], "name": name, "source": source_audience_id}

    # ════════════════════════════════════════════════════════
    #  REPORTING / INSIGHTS
    # ════════════════════════════════════════════════════════

    def get_campaign_insights(
        self,
        campaign_id: str,
        date_preset: str = "last_7d",
    ) -> List[Dict[str, Any]]:
        """Get performance insights for a campaign."""
        campaign = Campaign(campaign_id)
        fields = [
            "campaign_name", "impressions", "reach", "clicks",
            "spend", "cpc", "cpm", "ctr",
            "actions", "cost_per_action_type",
        ]
        insights = campaign.get_insights(fields=fields, params={"date_preset": date_preset})
        return [dict(i) for i in insights]

    def get_adset_insights(self, adset_id: str, date_preset: str = "last_7d") -> List[Dict[str, Any]]:
        adset = AdSet(adset_id)
        fields = [
            "adset_name", "impressions", "reach", "clicks",
            "spend", "cpc", "cpm", "ctr",
            "actions", "cost_per_action_type",
        ]
        insights = adset.get_insights(fields=fields, params={"date_preset": date_preset})
        return [dict(i) for i in insights]

    def get_ad_insights(self, ad_id: str, date_preset: str = "last_7d") -> List[Dict[str, Any]]:
        ad = Ad(ad_id)
        fields = [
            "ad_name", "impressions", "reach", "clicks",
            "spend", "cpc", "cpm", "ctr",
            "actions", "cost_per_action_type",
        ]
        insights = ad.get_insights(fields=fields, params={"date_preset": date_preset})
        return [dict(i) for i in insights]

    def get_account_spend(self, date_preset: str = "last_7d") -> Dict[str, Any]:
        """Get total ad account spend for the period."""
        fields = ["spend", "impressions", "reach", "clicks", "cpc", "cpm", "ctr"]
        insights = self.account.get_insights(fields=fields, params={"date_preset": date_preset})
        if insights:
            return dict(insights[0])
        return {"spend": "0", "impressions": "0"}

    # ════════════════════════════════════════════════════════
    #  CONVENIENCE: FULL AD CREATION FLOW
    # ════════════════════════════════════════════════════════

    def create_full_ad(
        self,
        campaign_name: str,
        adset_name: str,
        ad_name: str,
        image_path: str,
        headline: str,
        primary_text: str,
        description: str = "",
        link_url: str = "",
        cta_type: str = "LEARN_MORE",
        daily_budget_cents: int = 1000,
        targeting: Optional[Dict[str, Any]] = None,
        objective: str = "OUTCOME_LEADS",
    ) -> Dict[str, Any]:
        """One-call creation: campaign → ad set → creative → ad.  All created PAUSED."""
        # 1. Campaign
        camp = self.create_campaign(
            name=campaign_name,
            objective=objective,
            daily_budget_cents=daily_budget_cents,
        )

        # 2. Ad Set
        aset = self.create_ad_set(
            name=adset_name,
            campaign_id=camp["campaign_id"],
            daily_budget_cents=daily_budget_cents,
            targeting=targeting,
        )

        # 3. Upload image + creative
        image_hash = self.upload_ad_image(image_path)
        creative = self.create_ad_creative(
            name=f"{ad_name} Creative",
            image_hash=image_hash,
            headline=headline,
            primary_text=primary_text,
            description=description,
            link_url=link_url,
            cta_type=cta_type,
        )

        # 4. Ad
        ad = self.create_ad(
            name=ad_name,
            adset_id=aset["adset_id"],
            creative_id=creative["creative_id"],
        )

        return {
            "campaign": camp,
            "adset": aset,
            "creative": creative,
            "ad": ad,
            "status": "created_paused",
        }
