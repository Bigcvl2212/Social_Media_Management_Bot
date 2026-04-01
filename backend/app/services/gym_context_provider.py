"""
Gym Context Provider
Reads gym-specific data (promotions, pricing, hours, staff, amenities)
from GymBot's gym_profile.json and ai_knowledge_documents table so that
every piece of AI-generated content is specific to the actual gym.
"""

import json
import sqlite3
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from app.core.config import settings

import logging
logger = logging.getLogger(__name__)

# Default paths — GymBot stores profile in LOCALAPPDATA/GymBot/
_GYMBOT_ROOT = Path(settings.GYMBOT_DB_PATH).parent.parent if settings.GYMBOT_DB_PATH else None
_PROFILE_PATH = _GYMBOT_ROOT / "gym_profile.json" if _GYMBOT_ROOT else None
_KNOWLEDGE_DB = Path(settings.GYMBOT_DB_PATH) if settings.GYMBOT_DB_PATH else None


class GymContextProvider:
    """Loads and caches gym-specific data for AI content generation."""

    _cache: Optional[Dict[str, Any]] = None
    _cache_ts: float = 0
    CACHE_TTL = 300  # 5 minutes

    @classmethod
    def get_context(cls) -> Dict[str, Any]:
        """Return the full gym context dict (cached)."""
        now = datetime.now().timestamp()
        if cls._cache and (now - cls._cache_ts) < cls.CACHE_TTL:
            return cls._cache
        ctx = cls._build_context()
        cls._cache = ctx
        cls._cache_ts = now
        return ctx

    @classmethod
    def invalidate(cls):
        cls._cache = None

    # ── Build ────────────────────────────────────────────────

    @classmethod
    def _build_context(cls) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {}

        # 1. Gym profile
        profile = cls._load_profile()
        if profile:
            ctx["gym_name"] = profile.get("gym_name", "Anytime Fitness")
            ctx["gym_phone"] = profile.get("gym_phone", "")
            ctx["gym_address"] = profile.get("gym_address", "")
            ctx["gym_website"] = profile.get("gym_website", "")
            ctx["gym_hours"] = profile.get("gym_hours", "24/7 member access")
            ctx["staffed_hours"] = profile.get("staffed_hours", "")
            ctx["manager_name"] = profile.get("manager_name", "")
            ctx["owner_name"] = profile.get("owner_name", "")
            ctx["ai_assistant_name"] = profile.get("ai_assistant_name", "")
            # Promotions from profile
            promos = profile.get("promotions", [])
            if promos:
                ctx["promotions_from_profile"] = promos
            # Staff
            staff = profile.get("staff_contacts", [])
            if staff:
                ctx["staff"] = [
                    {"name": s.get("name", ""), "role": s.get("role", "")}
                    for s in staff
                ]

        # 2. Knowledge base (promotions, pricing, gym_info)
        knowledge = cls._load_knowledge_docs()
        for doc in knowledge:
            cat = doc.get("category", "").lower()
            if cat == "promotions":
                ctx["promotions"] = doc.get("content", "")
            elif cat == "pricing":
                ctx["pricing"] = doc.get("content", "")
            elif cat in ("gym_info", "gym_details"):
                ctx["gym_info"] = doc.get("content", "")
            elif cat == "training":
                ctx["training_info"] = doc.get("content", "")
            else:
                ctx.setdefault("extra_knowledge", []).append({
                    "category": cat,
                    "title": doc.get("title", ""),
                    "content": doc.get("content", "")[:500],
                })

        return ctx

    # ── Data Sources ─────────────────────────────────────────

    @classmethod
    def _load_profile(cls) -> Optional[Dict[str, Any]]:
        if not _PROFILE_PATH or not _PROFILE_PATH.exists():
            logger.debug(f"gym_profile.json not found at {_PROFILE_PATH}")
            return None
        try:
            return json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Failed to read gym_profile.json: {e}")
            return None

    @classmethod
    def _load_knowledge_docs(cls) -> List[Dict[str, Any]]:
        if not _KNOWLEDGE_DB or not _KNOWLEDGE_DB.exists():
            logger.debug(f"gym_bot.db not found at {_KNOWLEDGE_DB}")
            return []
        try:
            conn = sqlite3.connect(str(_KNOWLEDGE_DB), timeout=5)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT category, title, content FROM ai_knowledge_documents "
                "WHERE is_active = 1 ORDER BY priority DESC"
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"Failed to read ai_knowledge_documents: {e}")
            return []

    # ── Formatted Prompt Block ───────────────────────────────

    @classmethod
    def get_prompt_block(cls) -> str:
        """Return a pre-formatted text block suitable for injection into AI prompts."""
        ctx = cls.get_context()
        if not ctx:
            return ""

        lines = ["=== GYM CONTEXT (use this data in your content) ==="]

        if ctx.get("gym_name"):
            lines.append(f"Gym: {ctx['gym_name']}")
        if ctx.get("gym_address"):
            lines.append(f"Location: {ctx['gym_address']}")
        if ctx.get("gym_phone"):
            lines.append(f"Phone: {ctx['gym_phone']}")
        if ctx.get("gym_website"):
            lines.append(f"Website: {ctx['gym_website']}")
        if ctx.get("gym_hours"):
            lines.append(f"Hours: {ctx['gym_hours']}")
        if ctx.get("staffed_hours"):
            lines.append(f"Staffed Hours: {ctx['staffed_hours']}")
        if ctx.get("manager_name"):
            lines.append(f"Manager: {ctx['manager_name']}")

        if ctx.get("promotions"):
            lines.append("")
            lines.append("=== CURRENT PROMOTIONS & OFFERS ===")
            lines.append(ctx["promotions"])

        if ctx.get("pricing"):
            lines.append("")
            lines.append("=== PRICING ===")
            lines.append(ctx["pricing"])

        if ctx.get("training_info"):
            lines.append("")
            lines.append("=== TRAINING PROGRAMS ===")
            lines.append(ctx["training_info"])

        if ctx.get("gym_info"):
            lines.append("")
            lines.append("=== GYM DETAILS ===")
            lines.append(ctx["gym_info"])

        if ctx.get("staff"):
            lines.append("")
            lines.append("=== STAFF ===")
            for s in ctx["staff"]:
                lines.append(f"- {s['name']} ({s['role']})")

        lines.append("=== END GYM CONTEXT ===")
        return "\n".join(lines)
