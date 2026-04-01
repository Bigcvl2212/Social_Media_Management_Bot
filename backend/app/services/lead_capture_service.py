"""
Lead Capture Service
Captures leads from Facebook comments, ads, webhooks, and conversations.
Stores locally and bridges to GymBot's SQLite database.
"""

import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings

import logging
logger = logging.getLogger(__name__)


class LeadCaptureService:
    """Captures leads from all social media sources and pushes them to GymBot."""

    def __init__(self):
        self.gymbot_db_path = settings.GYMBOT_DB_PATH or ""
        self._local_leads: List[Dict[str, Any]] = []  # In-memory buffer

    # ════════════════════════════════════════════════════════
    #  CAPTURE (from any source)
    # ════════════════════════════════════════════════════════

    async def capture_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Capture a lead from any source.  Stores locally and optionally bridges to GymBot."""
        lead = {
            "source": lead_data.get("source", "facebook"),
            "facebook_user_id": lead_data.get("facebook_user_id", ""),
            "facebook_name": lead_data.get("facebook_name", ""),
            "first_name": lead_data.get("first_name", ""),
            "last_name": lead_data.get("last_name", ""),
            "email": lead_data.get("email", ""),
            "phone": lead_data.get("phone", ""),
            "comment_text": lead_data.get("comment_text", ""),
            "post_id": lead_data.get("post_id", ""),
            "comment_id": lead_data.get("comment_id", ""),
            "ad_id": lead_data.get("ad_id", ""),
            "campaign_name": lead_data.get("campaign_name", ""),
            "classification": lead_data.get("classification", "lead"),
            "captured_at": lead_data.get("captured_at", datetime.now(timezone.utc).isoformat()),
            "synced_to_gymbot": False,
        }

        # Parse name if we only have facebook_name
        if lead["facebook_name"] and not lead["first_name"]:
            parts = lead["facebook_name"].split(" ", 1)
            lead["first_name"] = parts[0]
            lead["last_name"] = parts[1] if len(parts) > 1 else ""

        self._local_leads.append(lead)
        logger.info(f"Lead captured: {lead['first_name']} {lead['last_name']} from {lead['source']}")

        # Try to push to GymBot immediately if we have enough data
        if self.gymbot_db_path and (lead["email"] or lead["phone"] or lead["first_name"]):
            synced = self._push_to_gymbot(lead)
            lead["synced_to_gymbot"] = synced

        return lead

    async def capture_from_lead_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Capture a lead from a Facebook Lead Ad instant form.
        Called by the webhook handler when a lead_gen event arrives.
        """
        lead_data = {
            "source": "facebook_lead_ad",
            "first_name": form_data.get("first_name", ""),
            "last_name": form_data.get("last_name", ""),
            "email": form_data.get("email", ""),
            "phone": form_data.get("phone_number", ""),
            "ad_id": form_data.get("ad_id", ""),
            "campaign_name": form_data.get("campaign_name", ""),
        }
        return await self.capture_lead(lead_data)

    async def capture_from_comment(
        self,
        user_name: str,
        user_id: str,
        comment_text: str,
        post_id: str,
        comment_id: str,
    ) -> Dict[str, Any]:
        """Capture a lead from a Facebook comment."""
        return await self.capture_lead({
            "source": "facebook_comment",
            "facebook_user_id": user_id,
            "facebook_name": user_name,
            "comment_text": comment_text,
            "post_id": post_id,
            "comment_id": comment_id,
        })

    async def capture_from_messenger(
        self,
        user_name: str,
        user_id: str,
        message_text: str,
        email: str = "",
        phone: str = "",
    ) -> Dict[str, Any]:
        """Capture a lead from a Messenger conversation."""
        return await self.capture_lead({
            "source": "facebook_messenger",
            "facebook_user_id": user_id,
            "facebook_name": user_name,
            "comment_text": message_text,
            "email": email,
            "phone": phone,
        })

    # ════════════════════════════════════════════════════════
    #  GYMBOT BRIDGE
    # ════════════════════════════════════════════════════════

    def _push_to_gymbot(self, lead: Dict[str, Any]) -> bool:
        """Insert lead into GymBot's prospects table (direct SQLite)."""
        if not self.gymbot_db_path:
            return False

        db_path = Path(self.gymbot_db_path)
        if not db_path.exists():
            logger.warning(f"GymBot DB not found at {self.gymbot_db_path}")
            return False

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Check for duplicate by email or phone
            if lead["email"]:
                cursor.execute("SELECT id FROM prospects WHERE email = ?", (lead["email"],))
                if cursor.fetchone():
                    logger.info(f"Lead {lead['email']} already exists in GymBot — skipping")
                    conn.close()
                    return True  # Already synced

            if lead["phone"]:
                cursor.execute("SELECT id FROM prospects WHERE mobile_phone = ?", (lead["phone"],))
                if cursor.fetchone():
                    logger.info(f"Lead {lead['phone']} already exists in GymBot — skipping")
                    conn.close()
                    return True

            # Determine origination source
            source_map = {
                "facebook_lead_ad": "Facebook Lead Ad",
                "facebook_comment": "Facebook Comment",
                "facebook_messenger": "Facebook Messenger",
                "facebook": "Facebook",
            }
            originated_from = source_map.get(lead["source"], "Social Media Bot")

            cursor.execute("""
                INSERT INTO prospects (
                    first_name, last_name, full_name,
                    email, mobile_phone,
                    lead_source, originated_from,
                    interest_level, trial,
                    notes, status,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead["first_name"],
                lead["last_name"],
                f"{lead['first_name']} {lead['last_name']}".strip(),
                lead["email"] or None,
                lead["phone"] or None,
                "social_media_bot",
                originated_from,
                5,  # Default interest level (mid-range)
                1,  # trial = True
                f"Auto-captured from {originated_from}: {lead.get('comment_text', '')[:200]}",
                "New",
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ))

            conn.commit()
            conn.close()
            logger.info(f"Pushed lead to GymBot: {lead['first_name']} {lead['last_name']}")
            return True

        except Exception as e:
            logger.error(f"GymBot bridge error: {e}")
            return False

    async def sync_pending_leads(self) -> Dict[str, Any]:
        """Sync all un-synced leads to GymBot."""
        synced = 0
        failed = 0
        for lead in self._local_leads:
            if not lead["synced_to_gymbot"]:
                if self._push_to_gymbot(lead):
                    lead["synced_to_gymbot"] = True
                    synced += 1
                else:
                    failed += 1
        return {"synced": synced, "failed": failed, "total_leads": len(self._local_leads)}

    # ════════════════════════════════════════════════════════
    #  LEAD QUERIES
    # ════════════════════════════════════════════════════════

    async def get_leads(
        self,
        source: Optional[str] = None,
        synced_only: bool = False,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get captured leads, optionally filtered."""
        results = self._local_leads
        if source:
            results = [l for l in results if l["source"] == source]
        if synced_only:
            results = [l for l in results if l["synced_to_gymbot"]]
        return results[-limit:]

    async def get_lead_stats(self) -> Dict[str, Any]:
        """Get lead capture statistics."""
        total = len(self._local_leads)
        synced = sum(1 for l in self._local_leads if l["synced_to_gymbot"])
        by_source: Dict[str, int] = {}
        for lead in self._local_leads:
            src = lead["source"]
            by_source[src] = by_source.get(src, 0) + 1
        return {
            "total_leads": total,
            "synced_to_gymbot": synced,
            "pending_sync": total - synced,
            "by_source": by_source,
        }
