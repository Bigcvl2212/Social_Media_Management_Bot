"""
Brand DNA Engine — learns your content style from existing posts,
builds a living Brand Profile, and applies it to all AI-generated content.

Three layers:
  1. Style Analyzer  — scrapes your page posts, analyzes tone/themes/patterns
  2. Brand Brief     — user-supplied direction merged with analyzed style
  3. Style-Locked Gen — every generated post references the Brand Profile
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

_DATA_DIR = Path(settings.UPLOAD_DIR) / "brand_dna"
_DATA_DIR.mkdir(parents=True, exist_ok=True)


class BrandDNAService:
    """Learns and maintains your brand's content DNA."""

    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        self._client = genai.Client(api_key=api_key)
        self._profile = self._load_profile()

    # ════════════════════════════════════════════════════════════════
    #  PERSISTENCE
    # ════════════════════════════════════════════════════════════════

    def _profile_path(self) -> Path:
        return _DATA_DIR / "brand_profile.json"

    def _load_profile(self) -> Dict[str, Any]:
        p = self._profile_path()
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                logger.warning("Corrupt brand profile, starting fresh")
        return self._default_profile()

    def _save_profile(self) -> None:
        self._profile_path().write_text(
            json.dumps(self._profile, indent=2, default=str),
            encoding="utf-8",
        )

    @staticmethod
    def _default_profile() -> Dict[str, Any]:
        return {
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "analysis": None,
            "brief": {
                "voice_description": "",
                "target_audience": "",
                "content_pillars": [],
                "dos": [],
                "donts": [],
                "custom_notes": "",
            },
            "style": {
                "tone": "",
                "emoji_usage": "moderate",
                "caption_length": "medium",
                "hashtag_style": "",
                "cta_style": "",
                "themes": [],
                "top_hashtags": [],
                "posting_patterns": {},
            },
            "posts_analyzed": 0,
            "last_analyzed_at": None,
        }

    # ════════════════════════════════════════════════════════════════
    #  GET / UPDATE PROFILE
    # ════════════════════════════════════════════════════════════════

    def get_profile(self) -> Dict[str, Any]:
        return self._profile

    def update_brief(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """User updates their brand brief (voice, pillars, dos/donts)."""
        b = self._profile.setdefault("brief", {})
        for key in ("voice_description", "target_audience", "custom_notes"):
            if key in brief_data:
                b[key] = brief_data[key]
        for key in ("content_pillars", "dos", "donts"):
            if key in brief_data and isinstance(brief_data[key], list):
                b[key] = brief_data[key]
        self._profile["updated_at"] = datetime.utcnow().isoformat()
        self._save_profile()
        return self._profile

    def update_style(self, style_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manually adjust auto-detected style parameters."""
        s = self._profile.setdefault("style", {})
        for key in ("tone", "emoji_usage", "caption_length", "hashtag_style", "cta_style"):
            if key in style_data:
                s[key] = style_data[key]
        for key in ("themes", "top_hashtags"):
            if key in style_data and isinstance(style_data[key], list):
                s[key] = style_data[key]
        self._profile["updated_at"] = datetime.utcnow().isoformat()
        self._save_profile()
        return self._profile

    # ════════════════════════════════════════════════════════════════
    #  ANALYZE POSTS — crawl page posts and build style profile
    # ════════════════════════════════════════════════════════════════

    async def analyze_posts(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Feed raw post data (from Facebook Graph API) and AI-analyze the brand style.

        posts: list of {message, created_time, likes, comments, shares, type, ...}
        """
        if not posts:
            return {"error": "No posts to analyze", "posts_analyzed": 0}

        # Build a text dump of posts for Gemini
        post_texts = []
        for i, p in enumerate(posts[:100]):  # cap at 100
            msg = p.get("message") or p.get("story") or ""
            ts = p.get("created_time", "")
            likes = p.get("likes", {}).get("summary", {}).get("total_count", 0) if isinstance(p.get("likes"), dict) else p.get("likes", 0)
            comments = p.get("comments", {}).get("summary", {}).get("total_count", 0) if isinstance(p.get("comments"), dict) else p.get("comments", 0)
            shares = p.get("shares", {}).get("count", 0) if isinstance(p.get("shares"), dict) else p.get("shares", 0)
            ptype = p.get("type", "status")
            post_texts.append(
                f"[Post {i+1}] ({ts[:10] if ts else '?'}) Type:{ptype} | "
                f"Likes:{likes} Comments:{comments} Shares:{shares}\n{msg}"
            )

        combined = "\n---\n".join(post_texts)

        prompt = f"""You are a brand strategist analyzing a business's social media page.
Below are the most recent {len(post_texts)} posts from this page.

Analyze the content and return a JSON object with:
{{
  "tone": "description of the brand's voice in 2-3 words (e.g. 'raw, motivational, direct')",
  "emoji_usage": "none | minimal | moderate | heavy",
  "caption_length": "short | medium | long" (short = 1-2 sentences, medium = 3-5, long = 6+),
  "hashtag_style": "description of how they use hashtags (count, type, placement)",
  "cta_style": "how they end posts / call-to-action pattern",
  "themes": ["list", "of", "top", "content", "themes", "found"],
  "top_hashtags": ["#hashtag1", "#hashtag2", "...up to 15"],
  "posting_patterns": {{
    "avg_posts_per_week": number,
    "best_performing_type": "type of post that gets most engagement",
    "best_performing_theme": "theme that resonates most",
    "peak_engagement_day": "day of week with most engagement"
  }},
  "brand_personality": "2-3 sentence description of the brand's personality based on content",
  "content_mix": {{
    "workout_fitness": percentage,
    "motivational": percentage,
    "promotional": percentage,
    "community": percentage,
    "educational": percentage,
    "other": percentage
  }},
  "strengths": ["what the brand does well", "up to 5"],
  "gaps": ["what's missing from their content strategy", "up to 5"],
  "recommendations": ["specific suggestions for improvement", "up to 5"]
}}

Return ONLY the JSON object, no markdown fences.

POSTS:
{combined}"""

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    max_output_tokens=2048,
                ),
            )
            raw = response.text or ""
            analysis = self._extract_json(raw)
            if not isinstance(analysis, dict):
                analysis = {"error": "AI returned invalid format", "raw": raw[:500]}
        except Exception as e:
            logger.error(f"Brand DNA analysis failed: {e}")
            analysis = {"error": str(e)}

        # Update profile with analysis results
        if "error" not in analysis:
            self._profile["analysis"] = analysis
            self._profile["posts_analyzed"] = len(post_texts)
            self._profile["last_analyzed_at"] = datetime.utcnow().isoformat()

            # Auto-populate style from analysis
            style = self._profile.setdefault("style", {})
            for key in ("tone", "emoji_usage", "caption_length", "hashtag_style",
                        "cta_style", "themes", "top_hashtags", "posting_patterns"):
                if key in analysis:
                    style[key] = analysis[key]

            self._profile["updated_at"] = datetime.utcnow().isoformat()
            self._save_profile()

        return {
            "posts_analyzed": len(post_texts),
            "analysis": analysis,
            "profile": self._profile,
        }

    # ════════════════════════════════════════════════════════════════
    #  CHAT — user gives natural language direction
    # ════════════════════════════════════════════════════════════════

    async def chat(self, message: str) -> Dict[str, Any]:
        """Process a natural language brand direction from the user.

        e.g. "Less emojis, more storytelling, always mention 24/7 access"
        Returns updated brief + AI interpretation.
        """
        current_brief = json.dumps(self._profile.get("brief", {}), indent=2)
        current_style = json.dumps(self._profile.get("style", {}), indent=2)

        prompt = f"""You are a brand strategist assistant. The user is giving you direction about their brand voice and content style.

CURRENT BRAND BRIEF:
{current_brief}

CURRENT STYLE PROFILE:
{current_style}

USER DIRECTION:
"{message}"

Based on the user's input, return a JSON object with the updated brief fields:
{{
  "voice_description": "updated voice description incorporating user's direction",
  "content_pillars": ["updated", "content", "pillars"],
  "dos": ["things to always do based on user's direction"],
  "donts": ["things to avoid based on user's direction"],
  "custom_notes": "any additional notes from user's input",
  "style_updates": {{
    "tone": "updated if user mentioned tone changes",
    "emoji_usage": "updated if user mentioned emoji preferences",
    "caption_length": "updated if relevant"
  }},
  "interpretation": "1-2 sentence summary of what you understood from the user's direction"
}}

Return ONLY the JSON object."""

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=1024,
                ),
            )
            raw = response.text or ""
            result = self._extract_json(raw)
            if not isinstance(result, dict):
                return {"error": "AI returned invalid format", "raw": raw[:500]}
        except Exception as e:
            logger.error(f"Brand DNA chat failed: {e}")
            return {"error": str(e)}

        # Apply updates
        brief = self._profile.setdefault("brief", {})
        for key in ("voice_description", "content_pillars", "dos", "donts", "custom_notes"):
            if key in result and result[key]:
                brief[key] = result[key]

        # Apply style updates if provided
        style_updates = result.get("style_updates", {})
        if style_updates:
            style = self._profile.setdefault("style", {})
            for k, v in style_updates.items():
                if v and v.lower() not in ("", "unchanged", "none", "n/a"):
                    style[k] = v

        self._profile["updated_at"] = datetime.utcnow().isoformat()
        self._save_profile()

        return {
            "interpretation": result.get("interpretation", "Direction applied."),
            "updated_brief": self._profile["brief"],
            "updated_style": self._profile["style"],
        }

    # ════════════════════════════════════════════════════════════════
    #  GENERATE PROMPT — returns a style instruction block for other services
    # ════════════════════════════════════════════════════════════════

    def get_style_prompt(self) -> str:
        """Return a prompt block that other services can prepend to their generation prompts
        to ensure content matches the brand DNA."""
        style = self._profile.get("style", {})
        brief = self._profile.get("brief", {})

        parts = ["=== BRAND DNA — Follow these rules for ALL content ==="]

        if style.get("tone"):
            parts.append(f"Tone: {style['tone']}")
        if brief.get("voice_description"):
            parts.append(f"Voice: {brief['voice_description']}")
        if style.get("emoji_usage"):
            parts.append(f"Emoji usage: {style['emoji_usage']}")
        if style.get("caption_length"):
            parts.append(f"Caption length: {style['caption_length']}")
        if style.get("hashtag_style"):
            parts.append(f"Hashtags: {style['hashtag_style']}")
        if style.get("cta_style"):
            parts.append(f"Call-to-action: {style['cta_style']}")
        if brief.get("content_pillars"):
            parts.append(f"Content pillars: {', '.join(brief['content_pillars'])}")
        if brief.get("dos"):
            parts.append(f"ALWAYS: {'; '.join(brief['dos'])}")
        if brief.get("donts"):
            parts.append(f"NEVER: {'; '.join(brief['donts'])}")
        if brief.get("custom_notes"):
            parts.append(f"Additional: {brief['custom_notes']}")
        if style.get("top_hashtags"):
            parts.append(f"Preferred hashtags: {' '.join(style['top_hashtags'][:10])}")

        parts.append("=== END BRAND DNA ===")
        return "\n".join(parts)

    # ════════════════════════════════════════════════════════════════
    #  RESET
    # ════════════════════════════════════════════════════════════════

    def reset_profile(self) -> Dict[str, Any]:
        """Reset the brand profile to defaults."""
        self._profile = self._default_profile()
        self._save_profile()
        return self._profile

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
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    pass
        return None
