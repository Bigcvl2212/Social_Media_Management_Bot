"""
Facebook Graph API Service
Handles all Facebook Page interactions: posting, comments, analytics, scheduling.
Uses Meta Graph API v21.0 with a permanent Page Access Token.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.core.config import settings

import logging
logger = logging.getLogger(__name__)

GRAPH_API = "https://graph.facebook.com/v21.0"


class FacebookService:
    """Facebook Graph API client.  Pass explicit credentials for multi-tenant,
    or omit to fall back to .env values (owner's account)."""

    def __init__(self, page_id: str = "", page_token: str = ""):
        self.page_id: str = page_id or settings.FACEBOOK_PAGE_ID or ""
        self.page_token: str = page_token or settings.FACEBOOK_PAGE_ACCESS_TOKEN or ""
        if not self.page_id or not self.page_token:
            logger.warning("FACEBOOK_PAGE_ID or FACEBOOK_PAGE_ACCESS_TOKEN not set")

    # ── helpers ──────────────────────────────────────────────

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.page_token}"}

    async def _get(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            params = params or {}
            params["access_token"] = self.page_token
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    async def _post(self, url: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            data = data or {}
            data["access_token"] = self.page_token
            if files:
                resp = await client.post(url, data=data, files=files)
            else:
                resp = await client.post(url, data=data)
            resp.raise_for_status()
            return resp.json()

    async def _delete(self, url: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.delete(url, params={"access_token": self.page_token})
            resp.raise_for_status()
            return resp.json()

    # ════════════════════════════════════════════════════════
    #  POSTING
    # ════════════════════════════════════════════════════════

    async def post_text(self, message: str, link: Optional[str] = None) -> Dict[str, Any]:
        """Publish a text-only (or text + link) post."""
        url = f"{GRAPH_API}/{self.page_id}/feed"
        data: Dict[str, str] = {"message": message}
        if link:
            data["link"] = link
        result = await self._post(url, data)
        return {"status": "posted", "post_id": result.get("id"), "posted_at": datetime.now(timezone.utc).isoformat()}

    async def post_photo(
        self,
        image_path: str,
        caption: str = "",
    ) -> Dict[str, Any]:
        """Upload and publish a photo post."""
        url = f"{GRAPH_API}/{self.page_id}/photos"
        with open(image_path, "rb") as f:
            files = {"source": (os.path.basename(image_path), f, "image/jpeg")}
            data = {"message": caption}
            result = await self._post(url, data, files)
        return {
            "status": "posted",
            "post_id": result.get("post_id") or result.get("id"),
            "posted_at": datetime.now(timezone.utc).isoformat(),
        }

    async def post_video(
        self,
        video_path: str,
        description: str = "",
        title: str = "",
    ) -> Dict[str, Any]:
        """Upload and publish a video post."""
        url = f"{GRAPH_API}/{self.page_id}/videos"
        with open(video_path, "rb") as f:
            files = {"source": (os.path.basename(video_path), f, "video/mp4")}
            data: Dict[str, str] = {"description": description}
            if title:
                data["title"] = title
            result = await self._post(url, data, files)
        return {
            "status": "posted",
            "video_id": result.get("id"),
            "posted_at": datetime.now(timezone.utc).isoformat(),
        }

    async def schedule_post(
        self,
        message: str,
        publish_timestamp: int,
        image_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Schedule a post for future publishing.
        publish_timestamp: Unix epoch (UTC), must be 10 min – 6 months in the future.
        """
        if image_path:
            url = f"{GRAPH_API}/{self.page_id}/photos"
            with open(image_path, "rb") as f:
                files = {"source": (os.path.basename(image_path), f, "image/jpeg")}
                data = {
                    "message": message,
                    "published": "false",
                    "scheduled_publish_time": str(publish_timestamp),
                }
                result = await self._post(url, data, files)
        else:
            url = f"{GRAPH_API}/{self.page_id}/feed"
            data = {
                "message": message,
                "published": "false",
                "scheduled_publish_time": str(publish_timestamp),
            }
            result = await self._post(url, data)

        return {
            "status": "scheduled",
            "post_id": result.get("id"),
            "scheduled_for": datetime.fromtimestamp(publish_timestamp, tz=timezone.utc).isoformat(),
        }

    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a published or scheduled post."""
        url = f"{GRAPH_API}/{post_id}"
        result = await self._delete(url)
        return {"status": "deleted", "post_id": post_id, "success": result.get("success", False)}

    async def edit_post(self, post_id: str, message: str) -> Dict[str, Any]:
        """Edit the text of an existing post."""
        url = f"{GRAPH_API}/{post_id}"
        result = await self._post(url, {"message": message})
        return {"status": "updated", "post_id": post_id, "success": result.get("success", True)}

    # ════════════════════════════════════════════════════════
    #  COMMENTS
    # ════════════════════════════════════════════════════════

    async def get_post_comments(
        self,
        post_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Fetch comments on a post."""
        url = f"{GRAPH_API}/{post_id}/comments"
        params = {"fields": "id,message,from,created_time,like_count,comment_count", "limit": str(limit)}
        data = await self._get(url, params)
        return data.get("data", [])

    async def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """Reply to a specific comment."""
        url = f"{GRAPH_API}/{comment_id}/comments"
        result = await self._post(url, {"message": message})
        return {"status": "replied", "comment_id": comment_id, "reply_id": result.get("id")}

    async def hide_comment(self, comment_id: str) -> Dict[str, Any]:
        """Hide a comment (spam/negative)."""
        url = f"{GRAPH_API}/{comment_id}"
        result = await self._post(url, {"is_hidden": "true"})
        return {"status": "hidden", "comment_id": comment_id}

    # ════════════════════════════════════════════════════════
    #  PAGE ANALYTICS / INSIGHTS
    # ════════════════════════════════════════════════════════

    async def get_page_insights(
        self,
        metrics: Optional[List[str]] = None,
        period: str = "day",
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch Page-level insights.
        Metrics: page_impressions, page_engaged_users, page_post_engagements,
                 page_fan_adds, page_views_total, etc.
        """
        url = f"{GRAPH_API}/{self.page_id}/insights"
        metrics_str = ",".join(metrics or [
            "page_impressions",
            "page_engaged_users",
            "page_post_engagements",
            "page_fan_adds",
            "page_views_total",
        ])
        params: Dict[str, str] = {"metric": metrics_str, "period": period}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        data = await self._get(url, params)
        return {
            "status": "success",
            "metrics": data.get("data", []),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        """Fetch engagement metrics for a specific post."""
        url = f"{GRAPH_API}/{post_id}/insights"
        params = {"metric": "post_impressions,post_engaged_users,post_clicks,post_reactions_like_total"}
        data = await self._get(url, params)
        return {
            "post_id": post_id,
            "metrics": data.get("data", []),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_page_posts(
        self,
        limit: int = 25,
        fields: str = "id,message,created_time,shares,likes.summary(true),comments.summary(true),full_picture",
    ) -> List[Dict[str, Any]]:
        """Get recent posts from the page."""
        url = f"{GRAPH_API}/{self.page_id}/posts"
        data = await self._get(url, {"fields": fields, "limit": str(limit)})
        return data.get("data", [])

    async def get_page_info(self) -> Dict[str, Any]:
        """Get basic page information."""
        url = f"{GRAPH_API}/{self.page_id}"
        params = {"fields": "id,name,fan_count,followers_count,about,category,link,location,phone"}
        return await self._get(url, params)

    # ════════════════════════════════════════════════════════
    #  CONVERSATIONS / MESSAGES (requires pages_messaging)
    # ════════════════════════════════════════════════════════

    async def get_page_conversations(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Get recent page conversations/messages."""
        url = f"{GRAPH_API}/{self.page_id}/conversations"
        data = await self._get(url, {"fields": "id,snippet,updated_time,participants", "limit": str(limit)})
        return data.get("data", [])
