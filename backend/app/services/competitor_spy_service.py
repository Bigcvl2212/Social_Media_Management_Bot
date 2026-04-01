"""
Competitor Spy — Monitor competitor pages, track what they post,
identify winning content ideas, auto-generate response posts in YOUR style.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

_DATA_DIR = Path(settings.UPLOAD_DIR) / "competitor_data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_INDEX_PATH = _DATA_DIR / "competitor_index.json"


class CompetitorSpyService:
    """Monitors competitors and generates competitive content ideas."""

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
                logger.warning("Corrupt competitor data, starting fresh")
        return {
            "competitors": {},
            "snapshots": [],
            "insights": [],
            "stats": {"total_scanned": 0, "ideas_generated": 0},
        }

    def _save_data(self) -> None:
        _INDEX_PATH.write_text(
            json.dumps(self._data, indent=2, default=str),
            encoding="utf-8",
        )

    # ════════════════════════════════════════════════════════════════
    #  COMPETITOR MANAGEMENT
    # ════════════════════════════════════════════════════════════════

    def add_competitor(self, competitor: Dict[str, Any]) -> Dict[str, Any]:
        """Register a competitor to monitor.

        competitor: {name, page_id?, page_url?, platform?, category?}
        """
        cid = competitor.get("page_id") or f"comp_{len(self._data['competitors'])+1}"
        rec = {
            "id": cid,
            "name": competitor.get("name", ""),
            "page_id": competitor.get("page_id", ""),
            "page_url": competitor.get("page_url", ""),
            "platform": competitor.get("platform", "facebook"),
            "category": competitor.get("category", ""),
            "added_at": datetime.utcnow().isoformat(),
            "last_scanned": None,
            "total_posts_scanned": 0,
            "avg_engagement": 0,
            "notes": competitor.get("notes", ""),
        }
        self._data["competitors"][cid] = rec
        self._save_data()
        return rec

    def list_competitors(self) -> List[Dict[str, Any]]:
        return list(self._data["competitors"].values())

    def get_competitor(self, cid: str) -> Optional[Dict[str, Any]]:
        return self._data["competitors"].get(cid)

    def delete_competitor(self, cid: str) -> bool:
        if cid in self._data["competitors"]:
            del self._data["competitors"][cid]
            self._save_data()
            return True
        return False

    def update_competitor(self, cid: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        comp = self._data["competitors"].get(cid)
        if not comp:
            return None
        for key in ("name", "page_url", "category", "notes"):
            if key in updates:
                comp[key] = updates[key]
        self._save_data()
        return comp

    # ════════════════════════════════════════════════════════════════
    #  SCAN — ingest competitor posts and analyze
    # ════════════════════════════════════════════════════════════════

    async def scan_competitor(self, cid: str, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of competitor posts and generate insights.

        posts: list of {message, type, likes, comments, shares, created_time}
        """
        comp = self._data["competitors"].get(cid)
        if not comp:
            raise ValueError(f"Competitor {cid} not found")

        if not posts:
            return {"error": "No posts to scan"}

        # Calculate engagement metrics
        total_engagement = 0
        post_summaries = []
        for p in posts[:50]:  # cap at 50
            likes = p.get("likes", 0)
            comments = p.get("comments", 0)
            shares = p.get("shares", 0)
            eng = likes + comments * 3 + shares * 5
            total_engagement += eng
            post_summaries.append({
                "message": (p.get("message", "") or "")[:200],
                "type": p.get("type", "status"),
                "engagement": eng,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "created_time": p.get("created_time", ""),
            })

        avg_eng = total_engagement / len(post_summaries) if post_summaries else 0

        # Sort by engagement to find top performers
        post_summaries.sort(key=lambda x: x["engagement"], reverse=True)

        # Store snapshot
        snapshot = {
            "competitor_id": cid,
            "competitor_name": comp["name"],
            "scanned_at": datetime.utcnow().isoformat(),
            "posts_scanned": len(post_summaries),
            "avg_engagement": round(avg_eng, 1),
            "top_posts": post_summaries[:5],
        }
        self._data["snapshots"].append(snapshot)

        # Update competitor record
        comp["last_scanned"] = datetime.utcnow().isoformat()
        comp["total_posts_scanned"] = comp.get("total_posts_scanned", 0) + len(post_summaries)
        comp["avg_engagement"] = round(avg_eng, 1)

        self._data["stats"]["total_scanned"] += len(post_summaries)

        # AI analysis of competitor strategy
        ai_insights = await self._analyze_competitor_strategy(
            comp["name"], post_summaries[:20]
        )

        if ai_insights and "error" not in ai_insights:
            insight_rec = {
                "competitor_id": cid,
                "competitor_name": comp["name"],
                "generated_at": datetime.utcnow().isoformat(),
                **ai_insights,
            }
            self._data["insights"].append(insight_rec)
            self._data["stats"]["ideas_generated"] += len(ai_insights.get("content_ideas", []))

        # Trim data
        if len(self._data["snapshots"]) > 100:
            self._data["snapshots"] = self._data["snapshots"][-100:]
        if len(self._data["insights"]) > 50:
            self._data["insights"] = self._data["insights"][-50:]

        self._save_data()

        return {
            "snapshot": snapshot,
            "insights": ai_insights,
        }

    async def _analyze_competitor_strategy(self, name: str,
                                            posts: List[Dict]) -> Optional[Dict[str, Any]]:
        """AI analysis of competitor content strategy."""
        post_dump = "\n".join([
            f"- ({p['created_time'][:10] if p['created_time'] else '?'}) "
            f"[Eng:{p['engagement']}] {p['message'][:150]}"
            for p in posts
        ])

        prompt = f"""Analyze these posts from competitor "{name}" and return a JSON object:

POSTS:
{post_dump}

Return:
{{
  "strategy_summary": "2-3 sentence summary of their content strategy",
  "content_themes": ["theme1", "theme2", "...up to 5"],
  "posting_frequency": "how often they post",
  "top_performing_type": "what type of content gets most engagement",
  "weaknesses": ["weakness1", "weakness2"],
  "what_they_do_well": ["strength1", "strength2"],
  "content_ideas": [
    {{
      "idea": "specific post idea inspired by their content but unique to you",
      "why": "why this would work",
      "format": "reel | post | carousel | story"
    }}
  ],
  "opportunity_gaps": ["things they aren't doing that you could do first"]
}}

Return ONLY the JSON object."""

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.6, max_output_tokens=1024),
            )
            result = self._extract_json(response.text or "")
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
        return None

    # ════════════════════════════════════════════════════════════════
    #  GENERATE RESPONSE POST — "they posted X, let's do better"
    # ════════════════════════════════════════════════════════════════

    async def generate_counter_post(self, competitor_post: str,
                                     brand_prompt: str = "") -> Dict[str, Any]:
        """Generate a post that responds to/one-ups a competitor's content."""
        prompt = f"""{brand_prompt}

A competitor just posted this and it's getting good engagement:
"{competitor_post}"

Create a response post for YOUR page that:
1. Covers the same topic but better
2. Adds your unique spin/value
3. Doesn't mention the competitor
4. Feels natural, not reactive

Return JSON:
{{
  "caption": "the full post caption",
  "hook": "the attention-grabbing first line",
  "visual_suggestion": "what image/video would pair well",
  "hashtags": ["#tag1", "#tag2"],
  "why_better": "1 sentence on why this outperforms the competitor's post"
}}

Return ONLY the JSON."""

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.8, max_output_tokens=512),
            )
            result = self._extract_json(response.text or "")
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.error(f"Counter post generation failed: {e}")
        return {"error": "Failed to generate counter post"}

    # ════════════════════════════════════════════════════════════════
    #  DASHBOARD DATA
    # ════════════════════════════════════════════════════════════════

    def get_dashboard(self) -> Dict[str, Any]:
        return {
            "competitors": self.list_competitors(),
            "recent_insights": list(reversed(self._data["insights"][-10:])),
            "recent_scans": list(reversed(self._data["snapshots"][-10:])),
            "stats": self._data["stats"],
        }

    def get_insights(self, cid: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        items = self._data["insights"]
        if cid:
            items = [i for i in items if i.get("competitor_id") == cid]
        return list(reversed(items[-limit:]))

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
