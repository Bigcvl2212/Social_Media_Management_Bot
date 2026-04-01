"""
Facebook Webhook receiver — lead form submissions and Messenger events.
"""

import hashlib
import hmac
import logging
from fastapi import APIRouter, HTTPException, Query, Request

from app.core.config import settings
from app.services.lead_capture_service import LeadCaptureService
from app.services.messenger_service import MessengerService

router = APIRouter()
logger = logging.getLogger(__name__)

_leads = None
_messenger = None

def _get_leads():
    global _leads
    if _leads is None:
        _leads = LeadCaptureService()
    return _leads

def _get_messenger():
    global _messenger
    if _messenger is None:
        _messenger = MessengerService()
    return _messenger


# ── Verification (GET) ───────────────────────────────────

@router.get("/facebook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Facebook sends a GET to verify the webhook endpoint."""
    expected = settings.WEBHOOK_VERIFY_TOKEN or ""
    if hub_mode == "subscribe" and hub_verify_token == expected:
        logger.info("Webhook verified successfully")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


# ── Event Receiver (POST) ────────────────────────────────

@router.post("/facebook")
async def receive_webhook(request: Request):
    """Handle incoming Facebook webhook events."""
    body = await request.json()
    obj = body.get("object")

    if obj == "page":
        for entry in body.get("entry", []):
            # Lead form submissions
            for change in entry.get("changes", []):
                if change.get("field") == "leadgen":
                    await _handle_leadgen(change.get("value", {}))

            # Messenger messages
            for messaging_event in entry.get("messaging", []):
                await _handle_messaging(messaging_event)

    return {"status": "ok"}


async def _handle_leadgen(value: dict):
    """Process a lead form submission webhook."""
    try:
        leadgen_id = value.get("leadgen_id", "")
        form_id = value.get("form_id", "")
        page_id = value.get("page_id", "")
        logger.info(f"Lead form submission: leadgen={leadgen_id} form={form_id}")
        await _get_leads().capture_from_lead_form({
            "leadgen_id": leadgen_id,
            "form_id": form_id,
            "page_id": page_id,
            "field_data": value.get("field_data", []),
        })
    except Exception as e:
        logger.error(f"Lead form processing error: {e}")


async def _handle_messaging(event: dict):
    """Process a Messenger message webhook."""
    try:
        sender_id = event.get("sender", {}).get("id", "")
        # Skip messages from our own page
        page_id = settings.FACEBOOK_PAGE_ID or ""
        if sender_id == page_id:
            return
        message = event.get("message", {})
        text = message.get("text", "")
        if not text:
            return
        logger.info(f"Messenger message from {sender_id}: {text[:80]}")
        await _get_messenger().handle_incoming_message(sender_id=sender_id, message_text=text)
    except Exception as e:
        logger.error(f"Messenger event processing error: {e}")
