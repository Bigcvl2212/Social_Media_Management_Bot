"""
Content Remix Engine — Takes top-performing posts and remixes them:
new caption, new angle, different format (photo → reel script, reel → carousel, etc.).
Recycles winning content every 60-90 days with a fresh spin.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

_DATA_DIR = Path(settings.UPLOAD_DIR) / "remix_data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_INDEX_PATH = _DATA_DIR / "remix_index.json"


# Format definitions for remixing
REMIX_FORMATS = {
    "instagram_reel": {"label": "Instagram Reel Script", "icon": "fab fa-instagram", "max_length": 60},
    "tiktok": {"label": "TikTok Script", "icon": "fab fa-tiktok", "max_length": 60},
    "instagram_carousel": {"label": "IG Carousel (5 slides)", "icon": "fas fa-images", "slides": 5},
    "facebook_post": {"label": "Facebook Post", "icon": "fab fa-facebook", "max_length": 500},
    "twitter_thread": {"label": "X/Twitter Thread", "icon": "fab fa-x-twitter", "tweets": 4},
    "youtube_short": {"label": "YouTube Short Script", "icon": "fab fa-youtube", "max_length": 60},
    "linkedin_post": {"label": "LinkedIn Post", "icon": "fab fa-linkedin", "max_length": 700},
    "story": {"label": "Story (IG/FB)", "icon": "fas fa-mobile-alt", "slides": 3},
    "blog_snippet": {"label": "Blog Snippet", "icon": "fas fa-blog", "max_length": 300},
}


class ContentRemixService:
    """Remixes top-performing content into fresh formats."""

    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        self._client = genai.Client(api_key=api_key)
        self._data = self._load_data()

    # ════════════════════════════════════════════════════════════════
    #  PERSISTENCE
    # ════════════════════════════════════════════════════════════════

    def _load_data(self) -> Dict[str, Any]:
        if _INDEX_PATH.exists():
            try:
                return json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
            except Exception:
                logger.warning("Corrupt remix data, starting fresh")
        return {"originals": {}, "remixes": [], "stats": {"total_remixes": 0}}

    def _save_data(self) -> None:
        _INDEX_PATH.write_text(
            json.dumps(self._data, indent=2, default=str),
            encoding="utf-8",
        )

    # ════════════════════════════════════════════════════════════════
    #  ADD ORIGINAL (top-performing post)
    # ════════════════════════════════════════════════════════════════

    def add_original(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Register a top-performing post for remixing.

        post: {message, type, likes, comments, shares, created_time, post_id, image_url?}
        """
        pid = post.get("post_id") or post.get("id") or f"post_{len(self._data['originals'])+1}"
        rec = {
            "id": pid,
            "message": post.get("message", ""),
            "type": post.get("type", "status"),
            "likes": post.get("likes", 0),
            "comments": post.get("comments", 0),
            "shares": post.get("shares", 0),
            "engagement_score": post.get("likes", 0) + post.get("comments", 0) * 3 + post.get("shares", 0) * 5,
            "created_time": post.get("created_time", ""),
            "image_url": post.get("image_url", ""),
            "added_at": datetime.utcnow().isoformat(),
            "remix_count": 0,
            "last_remixed": None,
        }
        self._data["originals"][pid] = rec
        self._save_data()
        return rec

    def list_originals(self) -> List[Dict[str, Any]]:
        """List all registered originals sorted by engagement."""
        items = list(self._data["originals"].values())
        items.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
        return items

    def delete_original(self, post_id: str) -> bool:
        if post_id in self._data["originals"]:
            del self._data["originals"][post_id]
            self._save_data()
            return True
        return False

    # ════════════════════════════════════════════════════════════════
    #  AUTO-DISCOVER top posts from Facebook data
    # ════════════════════════════════════════════════════════════════

    def discover_top_posts(self, posts: List[Dict[str, Any]], min_engagement: int = 10) -> List[Dict[str, Any]]:
        """Scan post data and auto-register high-performing ones."""
        added = []
        for p in posts:
            likes = p.get("likes", 0)
            if isinstance(likes, dict):
                likes = likes.get("summary", {}).get("total_count", 0)
            comments = p.get("comments", 0)
            if isinstance(comments, dict):
                comments = comments.get("summary", {}).get("total_count", 0)
            shares = p.get("shares", 0)
            if isinstance(shares, dict):
                shares = shares.get("count", 0)

            score = likes + comments * 3 + shares * 5
            if score >= min_engagement and p.get("message"):
                post_data = {
                    "post_id": p.get("id", ""),
                    "message": p.get("message", ""),
                    "type": p.get("type", "status"),
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "created_time": p.get("created_time", ""),
                }
                rec = self.add_original(post_data)
                added.append(rec)
        return added

    # ════════════════════════════════════════════════════════════════
    #  REMIX — transform content into new format
    # ════════════════════════════════════════════════════════════════

    async def remix(self, post_id: str, target_format: str,
                    brand_prompt: str = "", custom_angle: str = "") -> Dict[str, Any]:
        """Remix an original post into a new format.

        target_format: key from REMIX_FORMATS
        custom_angle: optional user direction like "focus on the transformation aspect"
        """
        original = self._data["originals"].get(post_id)
        if not original:
            raise ValueError(f"Original post {post_id} not found")

        fmt = REMIX_FORMATS.get(target_format)
        if not fmt:
            raise ValueError(f"Unknown format: {target_format}. Available: {list(REMIX_FORMATS.keys())}")

        angle_instruction = ""
        if custom_angle:
            angle_instruction = f"\nCustom angle from user: {custom_angle}"

        prompt = f"""{brand_prompt}

You are a professional social media content creator. Take this ORIGINAL high-performing post
and remix it into a completely new format. The remix should keep the core message but present
it in a fresh way that feels new — NOT copy-pasted.

ORIGINAL POST:
"{original['message']}"
(Engagement: {original['likes']} likes, {original['comments']} comments, {original['shares']} shares)

TARGET FORMAT: {fmt['label']}
{angle_instruction}

"""

        # Format-specific instructions
        if target_format in ("instagram_reel", "tiktok", "youtube_short"):
            prompt += f"""Create a {fmt.get('max_length', 60)}-second video script with:
- HOOK (first 3 seconds — attention-grabbing)
- BODY (main content)
- CTA (call to action)
- Suggested on-screen text overlays
- Suggested audio/music vibe

Return JSON:
{{"hook": "...", "body": "...", "cta": "...", "overlays": ["text1", "text2"], "music_vibe": "...", "caption": "...", "hashtags": ["#tag1"]}}"""

        elif target_format == "instagram_carousel":
            prompt += f"""Create a {fmt.get('slides', 5)}-slide Instagram carousel:
Return JSON:
{{"slides": [{{"headline": "...", "body": "..."}}], "caption": "...", "hashtags": ["#tag1"]}}"""

        elif target_format == "twitter_thread":
            prompt += f"""Create a {fmt.get('tweets', 4)}-tweet thread (each max 280 chars):
Return JSON:
{{"tweets": ["tweet1", "tweet2", "tweet3", "tweet4"]}}"""

        elif target_format == "story":
            prompt += f"""Create a {fmt.get('slides', 3)}-slide Story:
Return JSON:
{{"slides": [{{"text": "...", "visual_suggestion": "...", "sticker_suggestion": "..."}}], "cta": "..."}}"""

        else:
            prompt += f"""Rewrite in the {fmt['label']} format (max ~{fmt.get('max_length', 500)} words).
Return JSON:
{{"content": "the full rewritten post", "hashtags": ["#tag1"]}}"""

        prompt += "\nReturn ONLY the JSON, no markdown fences."

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.8, max_output_tokens=1024),
            )
            raw = response.text or ""
            content = self._extract_json(raw)
            if not isinstance(content, dict):
                content = {"content": raw, "error": "Could not parse structured output"}
        except Exception as e:
            logger.error(f"Remix generation failed: {e}")
            return {"error": str(e)}

        remix_rec = {
            "original_id": post_id,
            "target_format": target_format,
            "format_label": fmt["label"],
            "content": content,
            "custom_angle": custom_angle,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._data["remixes"].append(remix_rec)
        self._data["stats"]["total_remixes"] += 1

        # Update original's remix tracking
        original["remix_count"] = original.get("remix_count", 0) + 1
        original["last_remixed"] = datetime.utcnow().isoformat()

        # Trim remixes to last 200
        if len(self._data["remixes"]) > 200:
            self._data["remixes"] = self._data["remixes"][-200:]

        self._save_data()
        return remix_rec

    # ════════════════════════════════════════════════════════════════
    #  BATCH REMIX — remix all top posts into multiple formats
    # ════════════════════════════════════════════════════════════════

    async def batch_remix(self, target_formats: List[str],
                          brand_prompt: str = "", top_n: int = 5) -> List[Dict[str, Any]]:
        """Remix the top N posts into multiple formats."""
        originals = self.list_originals()[:top_n]
        results = []
        for orig in originals:
            for fmt in target_formats:
                try:
                    remix = await self.remix(orig["id"], fmt, brand_prompt)
                    results.append(remix)
                except Exception as e:
                    results.append({"error": str(e), "original_id": orig["id"], "format": fmt})
        return results

    def list_remixes(self, original_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List remixes, optionally filtered by original."""
        items = self._data["remixes"]
        if original_id:
            items = [r for r in items if r.get("original_id") == original_id]
        return list(reversed(items[-limit:]))

    def get_stats(self) -> Dict[str, Any]:
        return self._data["stats"]

    def get_formats(self) -> Dict[str, Any]:
        return REMIX_FORMATS

    # ════════════════════════════════════════════════════════════════
    #  UTILITY
    # ════════════════════════════════════════════════════════════════

    @staticmethod
    def _extract_json(text: str):
        text = text.strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m:
            text = m.group(1).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            for ch, end_ch in [("{", "}"), ("[", "]")]:
                start = text.find(ch)
                end = text.rfind(end_ch)
                if start != -1 and end != -1:
                    try:
                        return json.loads(text[start:end + 1])
                    except json.JSONDecodeError:
                        pass
        return None
