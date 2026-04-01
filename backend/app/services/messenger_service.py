"""
Messenger Automation Service
Handles Facebook Messenger conversations: auto-replies, FAQ bot, lead qualification.

NOTE: Requires `pages_messaging` permission which needs Meta App Review.
This service is fully implemented but will return permission errors until
the permission is granted. Set MESSENGER_ENABLED=true in .env once approved.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.services.gemini_ai_service import GeminiAIService
from app.services.lead_capture_service import LeadCaptureService

import logging
logger = logging.getLogger(__name__)

GRAPH_API = "https://graph.facebook.com/v21.0"

# Pre-built FAQ responses for instant reply (no AI needed)
FAQ_RESPONSES = {
    "hours": (
        "We're open 24/7! That's the Anytime Fitness difference — "
        "work out whenever fits your schedule. 💪\n\n"
        "Staffed hours are Mon-Thu 9am-7pm, Fri 9am-5pm, Sat 9am-12pm.\n"
        "Want to stop by for a tour? Just let us know what time works!"
    ),
    "price": (
        "Great question! Our membership plans start at a very affordable rate "
        "and we often have special promotions running. 🎉\n\n"
        "The best way to get current pricing is to stop by or give us a call "
        "at the club — we can find the perfect plan for your goals!\n\n"
        "Would you like to schedule a free tour?"
    ),
    "location": (
        "We're located at 28 S Main St, Fond du Lac, WI 54935! 📍\n\n"
        "Easy to find — right on Main Street. Come check us out anytime!"
    ),
    "classes": (
        "We offer a variety of classes and small group training options! 🏋️\n\n"
        "Check our schedule at the club or ask our staff about what's "
        "currently running. We'd love to help you find the right fit!\n\n"
        "Want to come try one out?"
    ),
    "trial": (
        "Absolutely! We'd love to have you try us out! 🎯\n\n"
        "Stop by during staffed hours and we'll get you set up with "
        "a free tour and trial workout. No pressure, just come see "
        "what we're all about!\n\n"
        "When works best for you?"
    ),
    "cancel": (
        "We're sorry to hear you're thinking about that. 😔\n\n"
        "For membership changes, please contact our front desk during "
        "staffed hours or call us directly. We'd love to chat about "
        "how we can help you stay on track with your goals!"
    ),
    "personal_training": (
        "We have amazing personal trainers who can help you reach your goals faster! 💪\n\n"
        "Whether you're just starting out or looking to level up, "
        "our trainers create personalized plans just for you.\n\n"
        "Want me to help you get connected with a trainer?"
    ),
}

# Keywords → FAQ key mapping
FAQ_KEYWORD_MAP = {
    "hours": ["hours", "open", "close", "when", "time", "schedule", "24/7", "staffed"],
    "price": ["price", "pricing", "cost", "how much", "rates", "membership", "fee", "pay", "afford"],
    "location": ["location", "address", "where", "find", "directions", "map"],
    "classes": ["class", "classes", "group", "yoga", "spin", "hiit", "crossfit", "zumba"],
    "trial": ["trial", "try", "tour", "visit", "check out", "free", "guest"],
    "cancel": ["cancel", "cancellation", "quit", "stop"],
    "personal_training": ["personal training", "trainer", "pt", "one on one", "1 on 1"],
}


class MessengerService:
    """Facebook Messenger automation.  Pass explicit credentials for multi-tenant,
    or omit to fall back to .env values."""

    def __init__(self, page_id: str = "", page_token: str = ""):
        self.page_id = page_id or settings.FACEBOOK_PAGE_ID or ""
        self.page_token = page_token or settings.FACEBOOK_PAGE_ACCESS_TOKEN or ""
        self.enabled = getattr(settings, "MESSENGER_ENABLED", False)
        self.ai = GeminiAIService()
        self.leads = LeadCaptureService()

        if not self.enabled:
            logger.info("Messenger service disabled (MESSENGER_ENABLED=false or pages_messaging not approved)")

    # ── Send Messages ────────────────────────────────────────

    async def send_message(self, recipient_id: str, text: str) -> Dict[str, Any]:
        """Send a text message to a user via Messenger."""
        if not self.enabled:
            return {"status": "disabled", "reason": "pages_messaging not approved"}

        url = f"{GRAPH_API}/{self.page_id}/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "messaging_type": "RESPONSE",
            "access_token": self.page_token,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return {"status": "sent", "recipient_id": recipient_id, "response": resp.json()}

    async def send_quick_replies(
        self,
        recipient_id: str,
        text: str,
        quick_replies: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Send a message with quick reply buttons."""
        if not self.enabled:
            return {"status": "disabled"}

        url = f"{GRAPH_API}/{self.page_id}/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "text": text,
                "quick_replies": [
                    {"content_type": "text", "title": qr["title"], "payload": qr.get("payload", qr["title"])}
                    for qr in quick_replies
                ],
            },
            "messaging_type": "RESPONSE",
            "access_token": self.page_token,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return {"status": "sent", "response": resp.json()}

    # ── Get Conversations ────────────────────────────────────

    async def get_conversations(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Get recent Messenger conversations."""
        if not self.enabled:
            return []

        url = f"{GRAPH_API}/{self.page_id}/conversations"
        params = {
            "fields": "id,snippet,updated_time,participants,message_count",
            "limit": str(limit),
            "access_token": self.page_token,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json().get("data", [])

    async def get_messages(self, conversation_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get messages in a conversation."""
        if not self.enabled:
            return []

        url = f"{GRAPH_API}/{conversation_id}/messages"
        params = {
            "fields": "id,message,from,created_time",
            "limit": str(limit),
            "access_token": self.page_token,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json().get("data", [])

    # ── Webhook Handler ──────────────────────────────────────

    async def handle_incoming_message(self, sender_id: str, message_text: str, sender_name: str = "") -> Dict[str, Any]:
        """Process an incoming Messenger message and auto-reply.
        Called by the webhook route when a messaging event arrives.
        """
        if not self.enabled:
            return {"status": "disabled"}

        logger.info(f"Messenger message from {sender_name or sender_id}: {message_text[:100]}")

        # 1. Check for FAQ match first (instant, no AI needed)
        faq_response = self._match_faq(message_text)
        if faq_response:
            await self.send_message(sender_id, faq_response)
            return {"status": "faq_reply", "matched": True}

        # 2. AI-generated reply for everything else
        try:
            reply = await self.ai.generate_comment_reply(
                comment_text=message_text,
                post_context="Facebook Messenger conversation with a potential gym member",
                tone="warm, friendly, and helpful — like a gym front desk staff member",
            )
            await self.send_message(sender_id, reply)
        except Exception as e:
            logger.error(f"AI reply failed for messenger: {e}")
            # Fallback
            await self.send_message(
                sender_id,
                "Thanks for reaching out! 😊 We'd love to help. "
                "For the fastest response, give us a call during staffed hours "
                "or stop by the club. We're here for you!"
            )

        # 3. Capture as lead
        try:
            await self.leads.capture_from_messenger(
                user_name=sender_name,
                user_id=sender_id,
                message_text=message_text,
            )
        except Exception as e:
            logger.error(f"Lead capture from messenger failed: {e}")

        return {"status": "ai_reply", "sender_id": sender_id}

    def _match_faq(self, text: str) -> Optional[str]:
        """Check if the message matches a known FAQ."""
        lower = text.lower()
        for faq_key, keywords in FAQ_KEYWORD_MAP.items():
            if any(kw in lower for kw in keywords):
                return FAQ_RESPONSES.get(faq_key)
        return None
