"""
API routes for Zapier integration and webhooks
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.integration import (
    ZapierWebhook,
    ZapierWebhookCreate,
    ZapierWebhookUpdate,
)
from app.services.integration_service import zapier_service

router = APIRouter()


@router.post("/webhooks", response_model=ZapierWebhook, status_code=status.HTTP_201_CREATED)
async def create_zapier_webhook(
    webhook_data: ZapierWebhookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new Zapier webhook"""
    return await zapier_service.create_webhook(
        db=db,
        webhook_data=webhook_data,
        user_id=current_user.id
    )


@router.get("/webhooks", response_model=List[ZapierWebhook])
async def get_zapier_webhooks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all Zapier webhooks for the current user"""
    return await zapier_service.get_user_webhooks(
        db=db,
        user_id=current_user.id
    )


@router.post("/trigger/{trigger_event}")
async def trigger_zapier_webhooks(
    trigger_event: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger Zapier webhooks for a specific event"""
    try:
        payload = await request.json()
    except:
        payload = {}
    
    # Add user context to payload
    payload.update({
        "user_id": current_user.id,
        "user_email": current_user.email,
        "triggered_at": "2024-01-01T00:00:00Z"  # This would be actual timestamp
    })
    
    return await zapier_service.trigger_webhook(
        db=db,
        trigger_event=trigger_event,
        user_id=current_user.id,
        payload=payload
    )


@router.get("/events")
async def get_available_trigger_events():
    """Get list of available Zapier trigger events"""
    return {
        "events": [
            {
                "name": "content_posted",
                "description": "Triggered when content is posted to social media",
                "payload_example": {
                    "content_id": 123,
                    "platform": "instagram",
                    "content": "Sample post content",
                    "posted_at": "2024-01-01T00:00:00Z"
                }
            },
            {
                "name": "campaign_sent",
                "description": "Triggered when an email/SMS campaign is sent",
                "payload_example": {
                    "campaign_id": 456,
                    "campaign_type": "email",
                    "recipients_count": 100,
                    "sent_at": "2024-01-01T00:00:00Z"
                }
            },
            {
                "name": "analytics_milestone",
                "description": "Triggered when reaching follower or engagement milestones",
                "payload_example": {
                    "milestone_type": "followers",
                    "platform": "instagram",
                    "current_value": 1000,
                    "milestone_value": 1000,
                    "achieved_at": "2024-01-01T00:00:00Z"
                }
            },
            {
                "name": "integration_connected",
                "description": "Triggered when a new integration is successfully connected",
                "payload_example": {
                    "integration_id": 789,
                    "integration_type": "crm",
                    "provider": "hubspot",
                    "connected_at": "2024-01-01T00:00:00Z"
                }
            }
        ]
    }