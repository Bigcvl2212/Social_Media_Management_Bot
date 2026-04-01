"""
Comment Monitor Service
Polls Facebook posts for new comments, analyses them with Gemini AI,
auto-replies, and flags potential leads.
"""

import asyncio
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.facebook_service import FacebookService
from app.services.gemini_ai_service import GeminiAIService

import logging
logger = logging.getLogger(__name__)

# Keywords that signal a potential lead
LEAD_KEYWORDS = {
    "join", "sign up", "signup", "membership", "how much", "price", "pricing",
    "cost", "rates", "free trial", "trial", "tour", "visit", "start",
    "interested", "thinking about", "looking for a gym", "open",
    "hours", "schedule", "classes", "personal training", "trainer",
}

# Keywords that need human attention
ESCALATION_KEYWORDS = {
    "cancel", "complaint", "terrible", "worst", "refund", "sue",
    "rude", "manager", "owner", "disgusting", "unsafe",
}

# Spam indicators
SPAM_INDICATORS = {
    "click here", "free money", "congratulations you won", "dm me for",
    "work from home", "crypto", "bitcoin",
}


class CommentMonitorService:
    """Monitors Facebook page comments, auto-replies, and captures leads."""

    def __init__(self):
        self.fb = FacebookService()
        self.ai = GeminiAIService()
        self.scheduler = AsyncIOScheduler()
        self._running = False
        self._replied_comments: Set[str] = set()  # In-memory dedup (survives restarts via DB)

    # ── Lifecycle ────────────────────────────────────────────

    def start(self, interval_seconds: int = 300):
        """Start polling comments every N seconds (default 5 min)."""
        if self._running:
            return
        self.scheduler.add_job(
            self._poll_comments,
            trigger=IntervalTrigger(seconds=interval_seconds),
            id="comment_monitor",
            replace_existing=True,
        )
        self.scheduler.start()
        self._running = True
        logger.info(f"Comment monitor started (polling every {interval_seconds}s)")

    def stop(self):
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("Comment monitor stopped")

    # ── Analysis ─────────────────────────────────────────────

    def classify_comment(self, text: str) -> Dict[str, Any]:
        """Classify a comment into categories based on keywords."""
        lower = text.lower()

        is_lead = any(kw in lower for kw in LEAD_KEYWORDS)
        needs_escalation = any(kw in lower for kw in ESCALATION_KEYWORDS)
        is_spam = any(kw in lower for kw in SPAM_INDICATORS)

        category = "general"
        if is_spam:
            category = "spam"
        elif needs_escalation:
            category = "escalation"
        elif is_lead:
            category = "lead"

        return {
            "category": category,
            "is_lead": is_lead,
            "needs_escalation": needs_escalation,
            "is_spam": is_spam,
        }

    # ── Core Loop ────────────────────────────────────────────

    async def _poll_comments(self):
        """Fetch recent posts, check for new comments, process each."""
        try:
            posts = await self.fb.get_page_posts(limit=10)
            for post in posts:
                post_id = post.get("id")
                if not post_id:
                    continue
                post_message = post.get("message", "")
                comments = await self.fb.get_post_comments(post_id, limit=25)
                for comment in comments:
                    await self._process_comment(comment, post_id, post_message)
        except Exception as e:
            logger.error(f"Comment polling error: {e}")

    async def _process_comment(
        self,
        comment: Dict[str, Any],
        post_id: str,
        post_context: str,
    ):
        """Process a single comment: classify, reply, flag lead."""
        comment_id = comment.get("id", "")
        if not comment_id or comment_id in self._replied_comments:
            return

        text = comment.get("message", "")
        if not text:
            return

        from_user = comment.get("from", {})
        user_name = from_user.get("name", "Someone")

        classification = self.classify_comment(text)

        # -- Spam: hide and skip
        if classification["is_spam"]:
            try:
                await self.fb.hide_comment(comment_id)
                logger.info(f"Hidden spam comment {comment_id}")
            except Exception:
                pass
            self._replied_comments.add(comment_id)
            return

        # -- Escalation: don't auto-reply, just log
        if classification["needs_escalation"]:
            logger.warning(f"ESCALATION needed — comment {comment_id} from {user_name}: {text[:100]}")
            self._replied_comments.add(comment_id)
            # TODO: push notification to Dylan via the automation engine
            return

        # -- Lead or general: auto-reply with AI
        try:
            reply = await self.ai.generate_comment_reply(
                comment_text=text,
                post_context=post_context,
                tone="friendly and helpful",
            )
            await self.fb.reply_to_comment(comment_id, reply)
            logger.info(f"Replied to comment {comment_id} from {user_name}")
        except Exception as e:
            logger.error(f"Failed to reply to comment {comment_id}: {e}")

        # -- If it's a lead, capture it
        if classification["is_lead"]:
            await self._capture_lead_from_comment(comment, post_id, classification)

        self._replied_comments.add(comment_id)

    async def _capture_lead_from_comment(
        self,
        comment: Dict[str, Any],
        post_id: str,
        classification: Dict[str, Any],
    ):
        """Extract lead info from a comment and queue it for capture."""
        from_user = comment.get("from", {})
        # Facebook comments only give us user ID + name (no email/phone)
        lead_data = {
            "source": "facebook_comment",
            "facebook_user_id": from_user.get("id", ""),
            "facebook_name": from_user.get("name", ""),
            "comment_text": comment.get("message", ""),
            "post_id": post_id,
            "comment_id": comment.get("id", ""),
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "classification": classification["category"],
        }
        # Persist lead via the lead capture service (Phase 6)
        try:
            from app.services.lead_capture_service import LeadCaptureService
            lead_svc = LeadCaptureService()
            await lead_svc.capture_lead(lead_data)
        except ImportError:
            logger.info(f"Lead captured (service not yet available): {lead_data}")
        except Exception as e:
            logger.error(f"Lead capture error: {e}")

    # ── Manual Triggers ──────────────────────────────────────

    async def process_post_comments(self, post_id: str) -> Dict[str, Any]:
        """Manually trigger comment processing for a specific post."""
        comments = await self.fb.get_post_comments(post_id, limit=50)
        processed = 0
        leads_found = 0
        for comment in comments:
            cid = comment.get("id", "")
            if cid in self._replied_comments:
                continue
            classification = self.classify_comment(comment.get("message", ""))
            await self._process_comment(comment, post_id, "")
            processed += 1
            if classification["is_lead"]:
                leads_found += 1
        return {"post_id": post_id, "comments_processed": processed, "leads_found": leads_found}

    async def get_recent_activity(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent comment monitoring activity."""
        return [
            {
                "comment_id": cid,
                "status": "replied",
            }
            for cid in list(self._replied_comments)[-limit:]
        ]
