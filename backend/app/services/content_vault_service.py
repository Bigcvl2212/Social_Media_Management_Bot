"""
Content Vault + Asset Tagger — Upload raw media, AI auto-tags everything,
smart search, and inventory tracking (what you have vs what you need).
"""

import asyncio
import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

_VAULT_DIR = Path(settings.UPLOAD_DIR) / "content_vault"
_VAULT_DIR.mkdir(parents=True, exist_ok=True)
_THUMBS_DIR = _VAULT_DIR / "thumbnails"
_THUMBS_DIR.mkdir(parents=True, exist_ok=True)
_INDEX_PATH = _VAULT_DIR / "vault_index.json"


class ContentVaultService:
    """Manages uploaded media assets with AI-powered tagging and search."""

    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        self._client = genai.Client(api_key=api_key)
        self._index = self._load_index()

    # ════════════════════════════════════════════════════════════════
    #  PERSISTENCE
    # ════════════════════════════════════════════════════════════════

    def _load_index(self) -> Dict[str, Any]:
        if _INDEX_PATH.exists():
            try:
                return json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
            except Exception:
                logger.warning("Corrupt vault index, starting fresh")
        return {"assets": {}, "tags_catalog": {}}

    def _save_index(self) -> None:
        _INDEX_PATH.write_text(
            json.dumps(self._index, indent=2, default=str),
            encoding="utf-8",
        )

    # ════════════════════════════════════════════════════════════════
    #  UPLOAD
    # ════════════════════════════════════════════════════════════════

    async def upload_asset(self, filename: str, data: bytes, media_type: str = "auto") -> Dict[str, Any]:
        """Save media file and auto-tag with AI.

        media_type: 'photo', 'video', or 'auto' (detect from extension)
        """
        asset_id = uuid.uuid4().hex[:12]

        ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
        if media_type == "auto":
            if ext in (".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"):
                media_type = "video"
            else:
                media_type = "photo"

        safe_name = f"{asset_id}_{filename}"
        dest = _VAULT_DIR / safe_name
        dest.write_bytes(data)

        # Generate thumbnail
        thumb_name = f"{asset_id}_thumb.jpg"
        if media_type == "video":
            await self._video_thumbnail(str(dest), str(_THUMBS_DIR / thumb_name))
        else:
            await self._image_thumbnail(str(dest), str(_THUMBS_DIR / thumb_name))

        record = {
            "id": asset_id,
            "filename": filename,
            "safe_name": safe_name,
            "path": str(dest),
            "media_type": media_type,
            "thumbnail": thumb_name,
            "size_bytes": len(data),
            "uploaded_at": datetime.utcnow().isoformat(),
            "tags": [],
            "ai_description": "",
            "category": "untagged",
            "usable_for": [],
            "used_in": [],
            "favorite": False,
        }

        self._index["assets"][asset_id] = record
        self._save_index()

        # Auto-tag asynchronously
        try:
            await self.auto_tag(asset_id)
        except Exception as e:
            logger.warning(f"Auto-tag failed for {asset_id}: {e}")

        return self._index["assets"][asset_id]

    # ════════════════════════════════════════════════════════════════
    #  AUTO-TAG with Gemini Vision
    # ════════════════════════════════════════════════════════════════

    async def auto_tag(self, asset_id: str) -> Dict[str, Any]:
        """AI-analyze an asset and generate tags."""
        rec = self._index["assets"].get(asset_id)
        if not rec:
            raise ValueError(f"Asset {asset_id} not found")

        # Read file for AI analysis
        thumb_path = _THUMBS_DIR / rec["thumbnail"]
        if not thumb_path.exists():
            raise ValueError("Thumbnail not available for analysis")

        img_bytes = thumb_path.read_bytes()

        prompt = """Analyze this image from a fitness business's content library.
Return a JSON object with:
{
  "tags": ["tag1", "tag2", "tag3", ...up to 10 descriptive tags],
  "description": "One sentence describing what's in this image",
  "category": one of ["workout", "gym_equipment", "member", "staff", "transformation", "facility", "outdoor", "food_nutrition", "event", "promotional", "lifestyle", "other"],
  "usable_for": ["types of social media posts this would work for, e.g. motivation, tutorial, before_after, promo, story"],
  "mood": "energetic | calm | intense | fun | professional | raw",
  "quality": "high | medium | low",
  "suggested_caption": "a caption that would work well with this image"
}
Return ONLY the JSON object."""

        try:
            parts = [prompt, types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")]
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=parts,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=512,
                ),
            )
            raw = response.text or ""
            result = self._extract_json(raw)
            if isinstance(result, dict):
                rec["tags"] = result.get("tags", [])
                rec["ai_description"] = result.get("description", "")
                rec["category"] = result.get("category", "other")
                rec["usable_for"] = result.get("usable_for", [])
                rec["mood"] = result.get("mood", "")
                rec["quality"] = result.get("quality", "medium")
                rec["suggested_caption"] = result.get("suggested_caption", "")

                # Update tags catalog
                for tag in rec["tags"]:
                    t = tag.lower().strip()
                    self._index["tags_catalog"][t] = self._index["tags_catalog"].get(t, 0) + 1

                self._save_index()
        except Exception as e:
            logger.error(f"Auto-tag AI failed: {e}")

        return rec

    # ════════════════════════════════════════════════════════════════
    #  LIST / SEARCH / GET
    # ════════════════════════════════════════════════════════════════

    def list_assets(self, category: Optional[str] = None, tag: Optional[str] = None,
                    media_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List assets with optional filtering."""
        assets = list(self._index["assets"].values())

        if category:
            assets = [a for a in assets if a.get("category") == category]
        if tag:
            tag_lower = tag.lower()
            assets = [a for a in assets if any(tag_lower in t.lower() for t in a.get("tags", []))]
        if media_type:
            assets = [a for a in assets if a.get("media_type") == media_type]

        assets.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
        return assets[:limit]

    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return self._index["assets"].get(asset_id)

    def search_assets(self, query: str) -> List[Dict[str, Any]]:
        """Smart text search across tags, descriptions, categories."""
        query_lower = query.lower()
        terms = query_lower.split()
        results = []
        for asset in self._index["assets"].values():
            score = 0
            searchable = " ".join([
                asset.get("ai_description", ""),
                " ".join(asset.get("tags", [])),
                asset.get("category", ""),
                asset.get("filename", ""),
                " ".join(asset.get("usable_for", [])),
            ]).lower()
            for term in terms:
                if term in searchable:
                    score += 1
            if score > 0:
                results.append((score, asset))
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:50]]

    def delete_asset(self, asset_id: str) -> bool:
        rec = self._index["assets"].pop(asset_id, None)
        if not rec:
            return False
        for p in (Path(rec["path"]), _THUMBS_DIR / rec.get("thumbnail", "")):
            if p.exists():
                p.unlink(missing_ok=True)
        self._save_index()
        return True

    def update_asset(self, asset_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Manually update tags, favorite, etc."""
        rec = self._index["assets"].get(asset_id)
        if not rec:
            return None
        for key in ("tags", "category", "favorite", "usable_for"):
            if key in updates:
                rec[key] = updates[key]
        self._save_index()
        return rec

    def toggle_favorite(self, asset_id: str) -> Optional[Dict[str, Any]]:
        rec = self._index["assets"].get(asset_id)
        if not rec:
            return None
        rec["favorite"] = not rec.get("favorite", False)
        self._save_index()
        return rec

    # ════════════════════════════════════════════════════════════════
    #  INVENTORY ANALYSIS — what you have vs what you need
    # ════════════════════════════════════════════════════════════════

    def get_inventory_stats(self) -> Dict[str, Any]:
        """Analyze content inventory: what categories are covered, what's missing."""
        assets = list(self._index["assets"].values())
        total = len(assets)
        if total == 0:
            return {"total": 0, "categories": {}, "gaps": ["Upload content to see inventory analysis"]}

        categories = {}
        for a in assets:
            cat = a.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1

        # Calculate percentages and identify gaps
        ideal_mix = {
            "workout": 30, "transformation": 15, "facility": 10,
            "member": 10, "staff": 5, "lifestyle": 10,
            "food_nutrition": 5, "promotional": 10, "event": 5,
        }
        gaps = []
        for cat, ideal_pct in ideal_mix.items():
            actual_count = categories.get(cat, 0)
            actual_pct = (actual_count / total) * 100 if total > 0 else 0
            if actual_pct < ideal_pct * 0.5:  # less than half the ideal
                gaps.append(f"Need more '{cat}' content ({actual_count} assets, {actual_pct:.0f}% vs {ideal_pct}% ideal)")

        tags_catalog = dict(sorted(
            self._index.get("tags_catalog", {}).items(),
            key=lambda x: x[1], reverse=True
        )[:30])

        return {
            "total": total,
            "photos": sum(1 for a in assets if a.get("media_type") == "photo"),
            "videos": sum(1 for a in assets if a.get("media_type") == "video"),
            "favorites": sum(1 for a in assets if a.get("favorite")),
            "categories": categories,
            "top_tags": tags_catalog,
            "gaps": gaps,
        }

    # ════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS
    # ════════════════════════════════════════════════════════════════

    async def _video_thumbnail(self, video_path: str, out_path: str) -> None:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-ss", "1", "-i", video_path,
            "-frames:v", "1", "-q:v", "4", out_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

    async def _image_thumbnail(self, img_path: str, out_path: str) -> None:
        """Create a resized thumbnail from an image using ffmpeg."""
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", img_path,
            "-vf", "scale=400:-1", "-q:v", "4", out_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

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
