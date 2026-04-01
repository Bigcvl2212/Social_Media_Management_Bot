"""
Analytics Aggregation Service
Pulls real metrics from Facebook Page insights, ad account, and local lead data.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from app.services.facebook_service import FacebookService
from app.services.facebook_ads_service import FacebookAdsService
from app.services.lead_capture_service import LeadCaptureService

import logging
logger = logging.getLogger(__name__)


class AnalyticsAggregationService:
    """Aggregates analytics from Facebook Page, Ads, and local lead data."""

    def __init__(self, page_id: str = "", page_token: str = "",
                 ad_account_id: str = ""):
        self.fb = FacebookService(page_id=page_id, page_token=page_token)
        self.ads = FacebookAdsService(page_id=page_id, access_token=page_token,
                                       ad_account_id=ad_account_id)
        self.leads = LeadCaptureService()

    # ════════════════════════════════════════════════════════
    #  DASHBOARD OVERVIEW
    # ════════════════════════════════════════════════════════

    async def get_dashboard_overview(self) -> Dict[str, Any]:
        """Full dashboard snapshot: page metrics + ad spend + leads."""
        overview: Dict[str, Any] = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

        # Page info
        try:
            page_info = await self.fb.get_page_info()
            overview["page"] = {
                "name": page_info.get("name", ""),
                "followers": page_info.get("followers_count", 0),
                "fans": page_info.get("fan_count", 0),
                "category": page_info.get("category", ""),
            }
        except Exception as e:
            logger.error(f"Page info fetch failed: {e}")
            overview["page"] = {"error": str(e)}

        # Page insights (last 7 days)
        try:
            insights = await self.fb.get_page_insights(period="week")
            metrics = {}
            for m in insights.get("metrics", []):
                name = m.get("name", "")
                values = m.get("values", [{}])
                if values:
                    metrics[name] = values[-1].get("value", 0)
            overview["page_metrics_7d"] = metrics
        except Exception as e:
            logger.error(f"Page insights fetch failed: {e}")
            overview["page_metrics_7d"] = {"error": str(e)}

        # Ad account spend
        if self.ads.enabled:
            try:
                spend = self.ads.get_account_spend(date_preset="last_7d")
                overview["ad_spend_7d"] = spend
            except Exception as e:
                logger.error(f"Ad spend fetch failed: {e}")
                overview["ad_spend_7d"] = {"error": str(e)}
        else:
            overview["ad_spend_7d"] = {"status": "ads_not_configured"}

        # Lead stats
        try:
            lead_stats = await self.leads.get_lead_stats()
            overview["leads"] = lead_stats
        except Exception as e:
            overview["leads"] = {"error": str(e)}

        return overview

    # ════════════════════════════════════════════════════════
    #  POST PERFORMANCE
    # ════════════════════════════════════════════════════════

    async def get_post_performance(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Get performance metrics for recent posts."""
        try:
            posts = await self.fb.get_page_posts(limit=limit)
            results = []
            for post in posts:
                likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
                comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
                shares = post.get("shares", {}).get("count", 0) if post.get("shares") else 0
                engagement = likes + comments + shares

                results.append({
                    "post_id": post.get("id", ""),
                    "message": (post.get("message", "") or "")[:100],
                    "created_time": post.get("created_time", ""),
                    "image": post.get("full_picture", ""),
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "engagement": engagement,
                })
            # Sort by engagement descending
            results.sort(key=lambda x: x["engagement"], reverse=True)
            return results
        except Exception as e:
            logger.error(f"Post performance fetch failed: {e}")
            return []

    # ════════════════════════════════════════════════════════
    #  AD PERFORMANCE
    # ════════════════════════════════════════════════════════

    async def get_ad_performance(self, date_preset: str = "last_7d") -> Dict[str, Any]:
        """Get ad account performance summary."""
        if not self.ads.enabled:
            return {"status": "ads_not_configured"}

        try:
            campaigns = self.ads.get_campaigns()
            campaign_insights = []
            for camp in campaigns:
                cid = camp.get("id", "")
                try:
                    insights = self.ads.get_campaign_insights(cid, date_preset=date_preset)
                    if insights:
                        campaign_insights.append({
                            "campaign_id": cid,
                            "name": camp.get("name", ""),
                            "status": camp.get("status", ""),
                            **insights[0],
                        })
                except Exception:
                    pass

            account_spend = self.ads.get_account_spend(date_preset=date_preset)

            return {
                "account_summary": account_spend,
                "campaigns": campaign_insights,
                "date_preset": date_preset,
            }
        except Exception as e:
            logger.error(f"Ad performance fetch failed: {e}")
            return {"error": str(e)}

    # ════════════════════════════════════════════════════════
    #  LEAD FUNNEL
    # ════════════════════════════════════════════════════════

    async def get_lead_funnel(self) -> Dict[str, Any]:
        """Lead funnel: impressions → clicks → leads → synced to GymBot."""
        funnel: Dict[str, Any] = {}

        # Impressions + clicks from ads
        if self.ads.enabled:
            try:
                spend = self.ads.get_account_spend(date_preset="last_30d")
                funnel["impressions_30d"] = int(spend.get("impressions", 0))
                funnel["clicks_30d"] = int(spend.get("clicks", 0))
                funnel["spend_30d"] = spend.get("spend", "0")
            except Exception:
                pass

        # Leads captured
        try:
            stats = await self.leads.get_lead_stats()
            funnel["leads_captured"] = stats.get("total_leads", 0)
            funnel["leads_synced_to_gymbot"] = stats.get("synced_to_gymbot", 0)
            funnel["leads_by_source"] = stats.get("by_source", {})
        except Exception:
            pass

        # Cost per lead
        if funnel.get("spend_30d") and funnel.get("leads_captured"):
            try:
                spend_val = float(funnel["spend_30d"])
                leads_val = funnel["leads_captured"]
                if leads_val > 0:
                    funnel["cost_per_lead"] = round(spend_val / leads_val, 2)
            except (ValueError, ZeroDivisionError):
                pass

        return funnel

    # ════════════════════════════════════════════════════════
    #  CONTENT INSIGHTS
    # ════════════════════════════════════════════════════════

    async def get_best_performing_content(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top N posts by engagement."""
        posts = await self.get_post_performance(limit=50)
        return posts[:limit]

    async def get_posting_time_analysis(self) -> Dict[str, Any]:
        """Analyze which posting times get the best engagement."""
        posts = await self.get_post_performance(limit=50)
        hour_engagement: Dict[int, List[int]] = {}
        day_engagement: Dict[str, List[int]] = {}

        for post in posts:
            created = post.get("created_time", "")
            if not created:
                continue
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                hour = dt.hour
                day = dt.strftime("%A")
                eng = post["engagement"]

                hour_engagement.setdefault(hour, []).append(eng)
                day_engagement.setdefault(day, []).append(eng)
            except Exception:
                continue

        # Average engagement by hour and day
        best_hours = {
            h: round(sum(v) / len(v), 1)
            for h, v in sorted(hour_engagement.items())
            if v
        }
        best_days = {
            d: round(sum(v) / len(v), 1)
            for d, v in day_engagement.items()
            if v
        }

        return {"by_hour": best_hours, "by_day": best_days}
