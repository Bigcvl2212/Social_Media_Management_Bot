"""
Tests for integration functionality
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock
from datetime import datetime, timedelta

from app.models.integration import (
    Integration, Campaign, APIKey, ZapierWebhook,
    IntegrationType, IntegrationStatus
)
from app.schemas.integration import (
    IntegrationCreate, CampaignCreate, APIKeyCreate, ZapierWebhookCreate
)
from app.services.integration_service import (
    integration_service, campaign_service, api_key_service, zapier_service
)


class TestIntegrationService:
    """Test integration service functionality"""

    @pytest.mark.asyncio
    async def test_create_integration(self):
        """Test creating a new integration"""
        db_mock = AsyncMock()
        
        integration_data = IntegrationCreate(
            name="HubSpot CRM",
            type=IntegrationType.CRM,
            provider="hubspot",
            api_key="test_api_key_123",
            config_data='{"portal_id": "12345"}'
        )
        
        # Mock the database operations
        integration_instance = Integration(
            id=1,
            name=integration_data.name,
            type=integration_data.type,
            provider=integration_data.provider,
            user_id=1,
            status=IntegrationStatus.PENDING
        )
        
        db_mock.add = AsyncMock()
        db_mock.commit = AsyncMock()
        db_mock.refresh = AsyncMock()
        
        with patch.object(integration_service, '_encrypt_data', return_value="encrypted_data"):
            result = await integration_service.create_integration(
                db=db_mock,
                integration_data=integration_data,
                user_id=1
            )
        
        assert result.name == integration_data.name
        assert result.type == integration_data.type
        assert result.provider == integration_data.provider
        assert result.user_id == 1

    @pytest.mark.asyncio
    async def test_get_user_integrations(self):
        """Test retrieving user integrations"""
        db_mock = AsyncMock()
        
        # Mock database query result
        mock_integrations = [
            Integration(
                id=1,
                name="HubSpot CRM",
                type=IntegrationType.CRM,
                provider="hubspot",
                user_id=1,
                status=IntegrationStatus.ACTIVE
            ),
            Integration(
                id=2,
                name="Shopify Store",
                type=IntegrationType.ECOMMERCE,
                provider="shopify",
                user_id=1,
                status=IntegrationStatus.ACTIVE
            )
        ]
        
        mock_result = AsyncMock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = mock_integrations
        mock_result.scalars = Mock(return_value=mock_scalars)
        db_mock.execute = AsyncMock(return_value=mock_result)
        
        result = await integration_service.get_user_integrations(
            db=db_mock,
            user_id=1
        )
        
        assert len(result) == 2
        assert result[0].name == "HubSpot CRM"
        assert result[1].name == "Shopify Store"

    @pytest.mark.asyncio
    async def test_test_integration_connection(self):
        """Test testing an integration connection"""
        db_mock = AsyncMock()
        
        # Mock integration
        mock_integration = Integration(
            id=1,
            name="HubSpot CRM",
            type=IntegrationType.CRM,
            provider="hubspot",
            user_id=1,
            status=IntegrationStatus.PENDING
        )
        
        with patch.object(integration_service, 'get_integration', return_value=mock_integration):
            db_mock.commit = AsyncMock()
            
            result = await integration_service.test_integration(
                db=db_mock,
                integration_id=1,
                user_id=1
            )
        
        assert result["status"] == "success"
        assert "hubspot" in result["message"]
        assert "details" in result
        assert mock_integration.status == IntegrationStatus.ACTIVE


class TestCampaignService:
    """Test campaign service functionality"""

    @pytest.mark.asyncio
    async def test_create_campaign(self):
        """Test creating a new campaign"""
        db_mock = AsyncMock()
        
        # Mock integration check
        mock_integration = Integration(
            id=1,
            type=IntegrationType.EMAIL,
            user_id=1
        )
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_integration)
        db_mock.execute = AsyncMock(return_value=mock_result)
        
        campaign_data = CampaignCreate(
            name="Welcome Email Campaign",
            type="email",
            content="Welcome to our platform!",
            subject="Welcome!",
            integration_id=1
        )
        
        db_mock.add = AsyncMock()
        db_mock.commit = AsyncMock()
        db_mock.refresh = AsyncMock()
        
        result = await campaign_service.create_campaign(
            db=db_mock,
            campaign_data=campaign_data,
            user_id=1
        )
        
        # Verify the campaign object was created
        db_mock.add.assert_called_once()
        db_mock.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_campaign(self):
        """Test sending a campaign"""
        db_mock = AsyncMock()
        
        # Mock campaign
        mock_campaign = Campaign(
            id=1,
            name="Test Campaign",
            type="email",
            content="Test content",
            user_id=1,
            sent_at=None
        )
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_campaign)
        db_mock.execute = AsyncMock(return_value=mock_result)
        db_mock.commit = AsyncMock()
        
        result = await campaign_service.send_campaign(
            db=db_mock,
            campaign_id=1,
            user_id=1
        )
        
        assert result["status"] == "success"
        assert result["campaign_id"] == 1
        assert "recipients_count" in result
        assert mock_campaign.sent_at is not None


class TestAPIKeyService:
    """Test API key service functionality"""

    @pytest.mark.asyncio
    async def test_create_api_key(self):
        """Test creating a new API key"""
        db_mock = AsyncMock()
        
        api_key_data = APIKeyCreate(
            name="Production API Key",
            rate_limit=5000,
            allowed_endpoints=["/api/public/content", "/api/public/analytics"]
        )
        
        db_mock.add = AsyncMock()
        db_mock.commit = AsyncMock()
        db_mock.refresh = AsyncMock()
        
        with patch.object(api_key_service, '_generate_api_key', return_value="smm_test_key_123"):
            result = await api_key_service.create_api_key(
                db=db_mock,
                api_key_data=api_key_data,
                user_id=1
            )
        
        db_mock.add.assert_called_once()
        db_mock.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_api_key(self):
        """Test validating an API key"""
        db_mock = AsyncMock()
        
        # Mock valid API key
        mock_api_key = APIKey(
            id=1,
            key_value="smm_test_key_123",
            user_id=1,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=30),
            total_requests=0
        )
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_api_key)
        db_mock.execute = AsyncMock(return_value=mock_result)
        db_mock.commit = AsyncMock()
        
        result = await api_key_service.validate_api_key(
            db=db_mock,
            key_value="smm_test_key_123"
        )
        
        assert result is not None
        assert result.key_value == "smm_test_key_123"
        assert result.total_requests == 1  # Should increment

    @pytest.mark.asyncio
    async def test_validate_expired_api_key(self):
        """Test validating an expired API key"""
        db_mock = AsyncMock()
        
        # Mock expired API key
        mock_api_key = APIKey(
            id=1,
            key_value="smm_expired_key",
            user_id=1,
            is_active=True,
            expires_at=datetime.utcnow() - timedelta(days=1)  # Expired
        )
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_api_key)
        db_mock.execute = AsyncMock(return_value=mock_result)
        
        result = await api_key_service.validate_api_key(
            db=db_mock,
            key_value="smm_expired_key"
        )
        
        assert result is None  # Should return None for expired key


class TestZapierService:
    """Test Zapier service functionality"""

    @pytest.mark.asyncio
    async def test_create_webhook(self):
        """Test creating a Zapier webhook"""
        db_mock = AsyncMock()
        
        webhook_data = ZapierWebhookCreate(
            name="Content Posted Webhook",
            trigger_event="content_posted",
            webhook_url="https://hooks.zapier.com/hooks/catch/123/abc",
            payload_template='{"content_id": "{{content_id}}", "platform": "{{platform}}"}'
        )
        
        db_mock.add = AsyncMock()
        db_mock.commit = AsyncMock()
        db_mock.refresh = AsyncMock()
        
        result = await zapier_service.create_webhook(
            db=db_mock,
            webhook_data=webhook_data,
            user_id=1
        )
        
        db_mock.add.assert_called_once()
        db_mock.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_webhook(self):
        """Test triggering webhooks"""
        db_mock = AsyncMock()
        
        # Mock webhooks
        mock_webhooks = [
            ZapierWebhook(
                id=1,
                name="Test Webhook",
                trigger_event="content_posted",
                webhook_url="https://hooks.zapier.com/hooks/catch/123/abc",
                user_id=1,
                is_active=True,
                total_triggers=0
            )
        ]
        
        mock_result = AsyncMock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = mock_webhooks
        mock_result.scalars = Mock(return_value=mock_scalars)
        db_mock.execute = AsyncMock(return_value=mock_result)
        db_mock.commit = AsyncMock()
        
        payload = {
            "content_id": 123,
            "platform": "instagram",
            "content": "Test post"
        }
        
        result = await zapier_service.trigger_webhook(
            db=db_mock,
            trigger_event="content_posted",
            user_id=1,
            payload=payload
        )
        
        assert len(result) == 1
        assert result[0]["webhook_id"] == 1
        assert result[0]["status"] == "success"
        assert mock_webhooks[0].total_triggers == 1


class TestIntegrationModels:
    """Test integration models"""

    def test_integration_model_creation(self):
        """Test creating an Integration model instance"""
        integration = Integration(
            name="Test Integration",
            type=IntegrationType.CRM,
            provider="hubspot",
            user_id=1,
            status=IntegrationStatus.ACTIVE
        )
        
        assert integration.name == "Test Integration"
        assert integration.type == IntegrationType.CRM
        assert integration.provider == "hubspot"
        assert integration.user_id == 1
        assert integration.status == IntegrationStatus.ACTIVE

    def test_campaign_model_creation(self):
        """Test creating a Campaign model instance"""
        campaign = Campaign(
            name="Test Campaign",
            type="email",
            content="Test email content",
            subject="Test Subject",
            integration_id=1,
            user_id=1
        )
        
        assert campaign.name == "Test Campaign"
        assert campaign.type == "email"
        assert campaign.content == "Test email content"
        assert campaign.subject == "Test Subject"
        assert campaign.integration_id == 1
        assert campaign.user_id == 1

    def test_api_key_model_creation(self):
        """Test creating an APIKey model instance"""
        api_key = APIKey(
            name="Test API Key",
            key_value="smm_test_key_123",
            user_id=1,
            rate_limit=1000
        )
        
        assert api_key.name == "Test API Key"
        assert api_key.key_value == "smm_test_key_123"
        assert api_key.user_id == 1
        # Note: Default values are applied at database insert time, not at model creation

    def test_zapier_webhook_model_creation(self):
        """Test creating a ZapierWebhook model instance"""
        webhook = ZapierWebhook(
            name="Test Webhook",
            trigger_event="content_posted",
            webhook_url="https://hooks.zapier.com/hooks/catch/123/abc",
            user_id=1
        )
        
        assert webhook.name == "Test Webhook"
        assert webhook.trigger_event == "content_posted"
        assert webhook.webhook_url == "https://hooks.zapier.com/hooks/catch/123/abc"
        assert webhook.user_id == 1
        # Note: Default values are applied at database insert time, not at model creation


class TestIntegrationEnums:
    """Test integration enums"""

    def test_integration_type_enum(self):
        """Test IntegrationType enum values"""
        assert IntegrationType.CRM == "crm"
        assert IntegrationType.ECOMMERCE == "ecommerce"
        assert IntegrationType.EMAIL == "email"
        assert IntegrationType.SMS == "sms"
        assert IntegrationType.API == "api"
        assert IntegrationType.ZAPIER == "zapier"

    def test_integration_status_enum(self):
        """Test IntegrationStatus enum values"""
        assert IntegrationStatus.ACTIVE == "active"
        assert IntegrationStatus.INACTIVE == "inactive"
        assert IntegrationStatus.ERROR == "error"
        assert IntegrationStatus.PENDING == "pending"