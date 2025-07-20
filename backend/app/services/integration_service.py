"""
Integration service for managing CRM, e-commerce, and communication integrations
"""

import json
import secrets
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException

from app.models.integration import (
    Integration, IntegrationCampaign, APIKey, ZapierWebhook,
    IntegrationType, IntegrationStatus
)
from app.models.user import User
from app.schemas.integration import (
    IntegrationCreate, IntegrationUpdate,
    CampaignCreate, CampaignUpdate,
    APIKeyCreate, APIKeyUpdate,
    ZapierWebhookCreate, ZapierWebhookUpdate
)


class IntegrationService:
    """Service for managing integrations"""

    def __init__(self):
        pass

    async def create_integration(
        self, 
        db: AsyncSession, 
        integration_data: IntegrationCreate, 
        user_id: int
    ) -> Integration:
        """Create a new integration"""
        
        # Encrypt sensitive data if provided
        encrypted_config = None
        if integration_data.config_data:
            encrypted_config = self._encrypt_data(integration_data.config_data)
        
        encrypted_api_key = None
        if integration_data.api_key:
            encrypted_api_key = self._encrypt_data(integration_data.api_key)
        
        encrypted_api_secret = None
        if integration_data.api_secret:
            encrypted_api_secret = self._encrypt_data(integration_data.api_secret)
        
        integration = Integration(
            name=integration_data.name,
            type=integration_data.type,
            provider=integration_data.provider,
            config_data=encrypted_config,
            api_key=encrypted_api_key,
            api_secret=encrypted_api_secret,
            webhook_url=integration_data.webhook_url,
            user_id=user_id,
            status=IntegrationStatus.PENDING
        )
        
        db.add(integration)
        await db.commit()
        await db.refresh(integration)
        
        return integration

    async def get_user_integrations(
        self, 
        db: AsyncSession, 
        user_id: int,
        integration_type: Optional[IntegrationType] = None
    ) -> List[Integration]:
        """Get all integrations for a user"""
        query = select(Integration).where(Integration.user_id == user_id)
        
        if integration_type:
            query = query.where(Integration.type == integration_type)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_integration(
        self, 
        db: AsyncSession, 
        integration_id: int, 
        user_id: int
    ) -> Optional[Integration]:
        """Get a specific integration"""
        result = await db.execute(
            select(Integration).where(
                and_(
                    Integration.id == integration_id,
                    Integration.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_integration(
        self,
        db: AsyncSession,
        integration_id: int,
        integration_data: IntegrationUpdate,
        user_id: int
    ) -> Optional[Integration]:
        """Update an integration"""
        integration = await self.get_integration(db, integration_id, user_id)
        
        if not integration:
            return None
        
        update_data = integration_data.model_dump(exclude_unset=True)
        
        # Handle encryption for sensitive fields
        if "config_data" in update_data and update_data["config_data"]:
            update_data["config_data"] = self._encrypt_data(update_data["config_data"])
        
        if "api_key" in update_data and update_data["api_key"]:
            update_data["api_key"] = self._encrypt_data(update_data["api_key"])
        
        if "api_secret" in update_data and update_data["api_secret"]:
            update_data["api_secret"] = self._encrypt_data(update_data["api_secret"])
        
        for field, value in update_data.items():
            setattr(integration, field, value)
        
        integration.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(integration)
        
        return integration

    async def delete_integration(
        self, 
        db: AsyncSession, 
        integration_id: int, 
        user_id: int
    ) -> bool:
        """Delete an integration"""
        integration = await self.get_integration(db, integration_id, user_id)
        
        if not integration:
            return False
        
        await db.delete(integration)
        await db.commit()
        return True

    async def test_integration(
        self, 
        db: AsyncSession, 
        integration_id: int, 
        user_id: int
    ) -> Dict[str, Any]:
        """Test an integration connection"""
        integration = await self.get_integration(db, integration_id, user_id)
        
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Mock testing - in a real implementation, this would test actual connections
        test_results = {
            "status": "success",
            "message": f"Successfully connected to {integration.provider}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "provider": integration.provider,
                "type": integration.type,
                "connection_time_ms": 150
            }
        }
        
        # Update integration status
        integration.status = IntegrationStatus.ACTIVE
        integration.last_sync = datetime.now(timezone.utc)
        await db.commit()
        
        return test_results

    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data (simplified - use proper encryption in production)"""
        # This is a placeholder - implement proper encryption
        return hashlib.sha256(data.encode()).hexdigest()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data (simplified - use proper decryption in production)"""
        # This is a placeholder - implement proper decryption
        return encrypted_data


class CampaignService:
    """Service for managing email/SMS campaigns"""

    async def create_campaign(
        self,
        db: AsyncSession,
        campaign_data: CampaignCreate,
        user_id: int
    ) -> IntegrationCampaign:
        """Create a new campaign"""
        
        # Verify the integration exists and belongs to the user
        integration_result = await db.execute(
            select(Integration).where(
                and_(
                    Integration.id == campaign_data.integration_id,
                    Integration.user_id == user_id
                )
            )
        )
        integration = integration_result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        if integration.type not in [IntegrationType.EMAIL, IntegrationType.SMS]:
            raise HTTPException(
                status_code=400, 
                detail="Integration must be email or SMS type for campaigns"
            )
        
        campaign = IntegrationCampaign(
            name=campaign_data.name,
            type=campaign_data.type,
            subject=campaign_data.subject,
            content=campaign_data.content,
            integration_id=campaign_data.integration_id,
            user_id=user_id,
            is_scheduled=campaign_data.is_scheduled,
            scheduled_at=campaign_data.scheduled_at
        )
        
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        
        return campaign

    async def get_user_campaigns(
        self,
        db: AsyncSession,
        user_id: int,
        campaign_type: Optional[str] = None
    ) -> List[IntegrationCampaign]:
        """Get all campaigns for a user"""
        query = select(IntegrationCampaign).where(IntegrationCampaign.user_id == user_id)
        
        if campaign_type:
            query = query.where(IntegrationCampaign.type == campaign_type)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def send_campaign(
        self,
        db: AsyncSession,
        campaign_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Send a campaign"""
        campaign_result = await db.execute(
            select(IntegrationCampaign).where(
                and_(
                    IntegrationCampaign.id == campaign_id,
                    IntegrationCampaign.user_id == user_id
                )
            )
        )
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        if campaign.sent_at:
            raise HTTPException(status_code=400, detail="Campaign already sent")
        
        # Mock sending - in real implementation, integrate with email/SMS providers
        send_results = {
            "status": "success",
            "campaign_id": campaign_id,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "recipients_count": 100,  # Mock data
            "delivery_rate": 0.98
        }
        
        campaign.sent_at = datetime.now(timezone.utc)
        await db.commit()
        
        return send_results


class APIKeyService:
    """Service for managing public API keys"""

    async def create_api_key(
        self,
        db: AsyncSession,
        api_key_data: APIKeyCreate,
        user_id: int
    ) -> APIKey:
        """Create a new API key"""
        
        # Generate secure API key
        key_value = self._generate_api_key()
        key_secret = secrets.token_urlsafe(32)
        
        # Convert allowed endpoints to JSON
        allowed_endpoints_json = None
        if api_key_data.allowed_endpoints:
            allowed_endpoints_json = json.dumps(api_key_data.allowed_endpoints)
        
        api_key = APIKey(
            name=api_key_data.name,
            key_value=key_value,
            key_secret=key_secret,
            user_id=user_id,
            rate_limit=api_key_data.rate_limit,
            allowed_endpoints=allowed_endpoints_json,
            expires_at=api_key_data.expires_at
        )
        
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        
        return api_key

    async def get_user_api_keys(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[APIKey]:
        """Get all API keys for a user"""
        result = await db.execute(
            select(APIKey).where(APIKey.user_id == user_id)
        )
        return result.scalars().all()

    async def validate_api_key(
        self,
        db: AsyncSession,
        key_value: str
    ) -> Optional[APIKey]:
        """Validate an API key"""
        result = await db.execute(
            select(APIKey).where(
                and_(
                    APIKey.key_value == key_value,
                    APIKey.is_active == True
                )
            )
        )
        api_key = result.scalar_one_or_none()
        
        if api_key and api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
            return None
        
        if api_key:
            # Update usage tracking
            api_key.total_requests += 1
            api_key.last_used = datetime.now(timezone.utc)
            await db.commit()
        
        return api_key

    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"smm_{secrets.token_urlsafe(32)}"


class ZapierService:
    """Service for managing Zapier webhooks"""

    async def create_webhook(
        self,
        db: AsyncSession,
        webhook_data: ZapierWebhookCreate,
        user_id: int
    ) -> ZapierWebhook:
        """Create a new Zapier webhook"""
        
        webhook = ZapierWebhook(
            name=webhook_data.name,
            trigger_event=webhook_data.trigger_event,
            webhook_url=webhook_data.webhook_url,
            payload_template=webhook_data.payload_template,
            user_id=user_id
        )
        
        db.add(webhook)
        await db.commit()
        await db.refresh(webhook)
        
        return webhook

    async def get_user_webhooks(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[ZapierWebhook]:
        """Get all webhooks for a user"""
        result = await db.execute(
            select(ZapierWebhook).where(ZapierWebhook.user_id == user_id)
        )
        return result.scalars().all()

    async def trigger_webhook(
        self,
        db: AsyncSession,
        trigger_event: str,
        user_id: int,
        payload: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Trigger webhooks for a specific event"""
        
        # Get active webhooks for this event and user
        result = await db.execute(
            select(ZapierWebhook).where(
                and_(
                    ZapierWebhook.trigger_event == trigger_event,
                    ZapierWebhook.user_id == user_id,
                    ZapierWebhook.is_active == True
                )
            )
        )
        webhooks = result.scalars().all()
        
        triggered_webhooks = []
        
        for webhook in webhooks:
            # Mock webhook trigger - in real implementation, make HTTP request
            trigger_result = {
                "webhook_id": webhook.id,
                "webhook_url": webhook.webhook_url,
                "status": "success",
                "triggered_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Update webhook stats
            webhook.total_triggers += 1
            webhook.last_triggered = datetime.now(timezone.utc)
            
            triggered_webhooks.append(trigger_result)
        
        await db.commit()
        return triggered_webhooks


# Create service instances
integration_service = IntegrationService()
campaign_service = CampaignService()
api_key_service = APIKeyService()
zapier_service = ZapierService()