"""
Admin panel routes for integration and platform management
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.integration import IntegrationType, IntegrationStatus
from app.schemas.integration import (
    Integration,
    IntegrationWithConfig,
    Campaign,
    APIKey,
    ZapierWebhook,
)
from app.services.integration_service import (
    integration_service,
    campaign_service,
    api_key_service,
    zapier_service
)

router = APIRouter()


@router.get("/dashboard/overview")
async def get_admin_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard overview"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get integration statistics
    integrations = await integration_service.get_user_integrations(
        db=db,
        user_id=current_user.id
    )
    
    campaigns = await campaign_service.get_user_campaigns(
        db=db,
        user_id=current_user.id
    )
    
    api_keys = await api_key_service.get_user_api_keys(
        db=db,
        user_id=current_user.id
    )
    
    webhooks = await zapier_service.get_user_webhooks(
        db=db,
        user_id=current_user.id
    )
    
    # Calculate statistics
    integration_stats = {}
    for integration_type in IntegrationType:
        count = len([i for i in integrations if i.type == integration_type])
        active_count = len([i for i in integrations if i.type == integration_type and i.status == IntegrationStatus.ACTIVE])
        integration_stats[integration_type.value] = {
            "total": count,
            "active": active_count
        }
    
    campaign_stats = {
        "total": len(campaigns),
        "email": len([c for c in campaigns if c.type == "email"]),
        "sms": len([c for c in campaigns if c.type == "sms"]),
        "sent": len([c for c in campaigns if c.sent_at is not None])
    }
    
    api_stats = {
        "total_keys": len(api_keys),
        "active_keys": len([k for k in api_keys if k.is_active]),
        "total_requests": sum(k.total_requests for k in api_keys)
    }
    
    webhook_stats = {
        "total": len(webhooks),
        "active": len([w for w in webhooks if w.is_active]),
        "total_triggers": sum(w.total_triggers for w in webhooks)
    }
    
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role
        },
        "integrations": integration_stats,
        "campaigns": campaign_stats,
        "api": api_stats,
        "webhooks": webhook_stats,
        "recent_activity": await _get_recent_activity(db, current_user.id)
    }


@router.get("/integrations/all", response_model=List[IntegrationWithConfig])
async def get_all_integrations_admin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    integration_type: Optional[IntegrationType] = None,
    status: Optional[IntegrationStatus] = None
):
    """Get all integrations with configuration data (admin only)"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    integrations = await integration_service.get_user_integrations(
        db=db,
        user_id=current_user.id,
        integration_type=integration_type
    )
    
    # Filter by status if provided
    if status:
        integrations = [i for i in integrations if i.status == status]
    
    return integrations


@router.get("/integrations/providers")
async def get_supported_providers(
    current_user: User = Depends(get_current_user)
):
    """Get list of supported integration providers"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    providers = {
        "crm": [
            {
                "id": "hubspot",
                "name": "HubSpot",
                "description": "Customer relationship management platform",
                "auth_type": "oauth",
                "required_fields": ["access_token"],
                "optional_fields": ["portal_id"]
            },
            {
                "id": "salesforce",
                "name": "Salesforce",
                "description": "Cloud-based CRM platform",
                "auth_type": "oauth",
                "required_fields": ["access_token", "instance_url"],
                "optional_fields": ["refresh_token"]
            }
        ],
        "ecommerce": [
            {
                "id": "shopify",
                "name": "Shopify",
                "description": "E-commerce platform",
                "auth_type": "oauth",
                "required_fields": ["shop_url", "access_token"],
                "optional_fields": ["webhook_secret"]
            },
            {
                "id": "woocommerce",
                "name": "WooCommerce",
                "description": "WordPress e-commerce plugin",
                "auth_type": "api_key",
                "required_fields": ["site_url", "consumer_key", "consumer_secret"],
                "optional_fields": []
            }
        ],
        "email": [
            {
                "id": "mailchimp",
                "name": "Mailchimp",
                "description": "Email marketing platform",
                "auth_type": "api_key",
                "required_fields": ["api_key", "server_prefix"],
                "optional_fields": ["list_id"]
            },
            {
                "id": "sendgrid",
                "name": "SendGrid",
                "description": "Email delivery service",
                "auth_type": "api_key",
                "required_fields": ["api_key"],
                "optional_fields": ["template_id"]
            }
        ],
        "sms": [
            {
                "id": "twilio",
                "name": "Twilio",
                "description": "SMS and communication platform",
                "auth_type": "api_key",
                "required_fields": ["account_sid", "auth_token", "from_number"],
                "optional_fields": []
            }
        ]
    }
    
    return providers


@router.post("/integrations/bulk-test")
async def bulk_test_integrations(
    integration_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test multiple integrations at once"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    results = []
    
    for integration_id in integration_ids:
        try:
            result = await integration_service.test_integration(
                db=db,
                integration_id=integration_id,
                user_id=current_user.id
            )
            results.append({
                "integration_id": integration_id,
                "status": "success",
                "result": result
            })
        except Exception as e:
            results.append({
                "integration_id": integration_id,
                "status": "error",
                "error": str(e)
            })
    
    return {"results": results}


@router.get("/campaigns/analytics")
async def get_campaign_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, description="Number of days to analyze")
):
    """Get campaign performance analytics"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    campaigns = await campaign_service.get_user_campaigns(
        db=db,
        user_id=current_user.id
    )
    
    # Mock analytics data - in real implementation, this would aggregate actual metrics
    analytics = {
        "total_campaigns": len(campaigns),
        "sent_campaigns": len([c for c in campaigns if c.sent_at]),
        "email_campaigns": len([c for c in campaigns if c.type == "email"]),
        "sms_campaigns": len([c for c in campaigns if c.type == "sms"]),
        "performance_metrics": {
            "average_open_rate": 0.24,  # Mock data
            "average_click_rate": 0.08,
            "average_delivery_rate": 0.97,
            "total_recipients": 2500
        },
        "top_performing_campaigns": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "mock_open_rate": 0.32,
                "mock_click_rate": 0.12
            }
            for c in campaigns[:5] if c.sent_at
        ]
    }
    
    return analytics


@router.get("/api/usage-analytics")
async def get_api_usage_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, description="Number of days to analyze")
):
    """Get API usage analytics"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    api_keys = await api_key_service.get_user_api_keys(
        db=db,
        user_id=current_user.id
    )
    
    # Mock analytics data
    analytics = {
        "total_requests": sum(k.total_requests for k in api_keys),
        "active_keys": len([k for k in api_keys if k.is_active]),
        "average_requests_per_key": sum(k.total_requests for k in api_keys) / len(api_keys) if api_keys else 0,
        "top_endpoints": [
            {"endpoint": "/api/public/content", "requests": 1250},
            {"endpoint": "/api/public/analytics", "requests": 890},
            {"endpoint": "/api/public/social-accounts", "requests": 567}
        ],
        "usage_by_key": [
            {
                "key_id": k.id,
                "key_name": k.name,
                "total_requests": k.total_requests,
                "last_used": k.last_used.isoformat() if k.last_used else None
            }
            for k in api_keys
        ]
    }
    
    return analytics


@router.get("/webhooks/event-logs")
async def get_webhook_event_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, description="Number of recent events to return")
):
    """Get recent webhook event logs"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    webhooks = await zapier_service.get_user_webhooks(
        db=db,
        user_id=current_user.id
    )
    
    # Mock event logs - in real implementation, store actual event history
    event_logs = []
    for webhook in webhooks:
        if webhook.last_triggered:
            event_logs.append({
                "webhook_id": webhook.id,
                "webhook_name": webhook.name,
                "trigger_event": webhook.trigger_event,
                "triggered_at": webhook.last_triggered.isoformat(),
                "status": "success",
                "response_time_ms": 150
            })
    
    # Sort by triggered time and limit results
    event_logs.sort(key=lambda x: x["triggered_at"], reverse=True)
    return {"events": event_logs[:limit]}


async def _get_recent_activity(db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
    """Get recent activity for the dashboard"""
    # Mock recent activity - in real implementation, track actual events
    return [
        {
            "type": "integration_connected",
            "description": "HubSpot CRM integration connected",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "type": "campaign_sent",
            "description": "Welcome Email campaign sent to 150 recipients",
            "timestamp": "2024-01-15T09:15:00Z"
        },
        {
            "type": "api_key_created",
            "description": "New API key 'Production Key' created",
            "timestamp": "2024-01-14T16:45:00Z"
        },
        {
            "type": "webhook_triggered",
            "description": "Content Posted webhook triggered 3 times",
            "timestamp": "2024-01-14T14:20:00Z"
        }
    ]