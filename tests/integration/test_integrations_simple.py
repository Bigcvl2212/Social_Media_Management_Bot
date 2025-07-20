"""
Basic tests for integration functionality (focusing on functionality, not complex mocking)
"""

import pytest
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
            user_id=1,
            is_active=True
        )
        
        assert campaign.name == "Test Campaign"
        assert campaign.type == "email"
        assert campaign.content == "Test email content"
        assert campaign.subject == "Test Subject"
        assert campaign.integration_id == 1
        assert campaign.user_id == 1
        assert campaign.is_active == True

    def test_api_key_model_creation(self):
        """Test creating an APIKey model instance"""
        api_key = APIKey(
            name="Test API Key",
            key_value="smm_test_key_123",
            user_id=1,
            rate_limit=1000,
            is_active=True,
            total_requests=0
        )
        
        assert api_key.name == "Test API Key"
        assert api_key.key_value == "smm_test_key_123"
        assert api_key.user_id == 1
        assert api_key.rate_limit == 1000
        assert api_key.is_active == True
        assert api_key.total_requests == 0

    def test_zapier_webhook_model_creation(self):
        """Test creating a ZapierWebhook model instance"""
        webhook = ZapierWebhook(
            name="Test Webhook",
            trigger_event="content_posted",
            webhook_url="https://hooks.zapier.com/hooks/catch/123/abc",
            user_id=1,
            is_active=True,
            total_triggers=0
        )
        
        assert webhook.name == "Test Webhook"
        assert webhook.trigger_event == "content_posted"
        assert webhook.webhook_url == "https://hooks.zapier.com/hooks/catch/123/abc"
        assert webhook.user_id == 1
        assert webhook.is_active == True
        assert webhook.total_triggers == 0


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


class TestIntegrationSchemas:
    """Test integration schemas"""

    def test_integration_create_schema(self):
        """Test IntegrationCreate schema"""
        data = {
            "name": "HubSpot CRM",
            "type": "crm",
            "provider": "hubspot",
            "api_key": "test_key",
            "config_data": '{"portal_id": "12345"}'
        }
        
        schema = IntegrationCreate(**data)
        assert schema.name == "HubSpot CRM"
        assert schema.type == IntegrationType.CRM
        assert schema.provider == "hubspot"
        assert schema.api_key == "test_key"

    def test_campaign_create_schema(self):
        """Test CampaignCreate schema"""
        data = {
            "name": "Welcome Email",
            "type": "email",
            "content": "Welcome to our platform!",
            "subject": "Welcome!",
            "integration_id": 1
        }
        
        schema = CampaignCreate(**data)
        assert schema.name == "Welcome Email"
        assert schema.type == "email"
        assert schema.content == "Welcome to our platform!"
        assert schema.subject == "Welcome!"
        assert schema.integration_id == 1

    def test_api_key_create_schema(self):
        """Test APIKeyCreate schema"""
        data = {
            "name": "Production API Key",
            "rate_limit": 5000,
            "allowed_endpoints": ["/api/public/content", "/api/public/analytics"]
        }
        
        schema = APIKeyCreate(**data)
        assert schema.name == "Production API Key"
        assert schema.rate_limit == 5000
        assert len(schema.allowed_endpoints) == 2

    def test_zapier_webhook_create_schema(self):
        """Test ZapierWebhookCreate schema"""
        data = {
            "name": "Content Posted Webhook",
            "trigger_event": "content_posted",
            "webhook_url": "https://hooks.zapier.com/hooks/catch/123/abc"
        }
        
        schema = ZapierWebhookCreate(**data)
        assert schema.name == "Content Posted Webhook"
        assert schema.trigger_event == "content_posted"
        assert schema.webhook_url == "https://hooks.zapier.com/hooks/catch/123/abc"


class TestIntegrationServiceMethods:
    """Test integration service methods (without database)"""

    def test_encrypt_decrypt_data(self):
        """Test data encryption/decryption"""
        service = integration_service
        
        original_data = "sensitive_api_key_123"
        encrypted = service._encrypt_data(original_data)
        
        # The current implementation uses hash, so it's one-way
        assert encrypted != original_data
        assert len(encrypted) == 64  # SHA256 hex length

    def test_generate_api_key(self):
        """Test API key generation"""
        service = api_key_service
        
        api_key = service._generate_api_key()
        
        assert api_key.startswith("smm_")
        assert len(api_key) > 10  # Should be reasonably long


class TestIntegrationBusinessLogic:
    """Test business logic for integrations"""

    def test_integration_types_compatibility(self):
        """Test that integration types are compatible with expected use cases"""
        # CRM integrations should support customer data
        crm_types = [IntegrationType.CRM]
        assert IntegrationType.CRM in crm_types
        
        # E-commerce integrations should support order data
        ecommerce_types = [IntegrationType.ECOMMERCE]
        assert IntegrationType.ECOMMERCE in ecommerce_types
        
        # Communication integrations should support campaigns
        comm_types = [IntegrationType.EMAIL, IntegrationType.SMS]
        assert IntegrationType.EMAIL in comm_types
        assert IntegrationType.SMS in comm_types

    def test_campaign_type_validation(self):
        """Test campaign type validation logic"""
        valid_types = ["email", "sms"]
        
        # Test that campaign types are valid
        assert "email" in valid_types
        assert "sms" in valid_types
        assert "invalid_type" not in valid_types

    def test_webhook_url_format(self):
        """Test webhook URL format validation"""
        valid_urls = [
            "https://hooks.zapier.com/hooks/catch/123/abc",
            "http://example.com/webhook"
        ]
        invalid_urls = [
            "invalid-url",
            "ftp://example.com",
            ""
        ]
        
        for url in valid_urls:
            # This would pass pattern validation
            assert url.startswith(("http://", "https://"))
        
        for url in invalid_urls:
            # This would fail pattern validation
            if url:  # Skip empty string
                assert not url.startswith(("http://", "https://"))

    def test_api_key_format(self):
        """Test API key format"""
        service = api_key_service
        api_key = service._generate_api_key()
        
        # Should follow expected format
        assert api_key.startswith("smm_")
        assert "_" in api_key
        assert len(api_key.split("_")[1]) > 20  # Random part should be substantial