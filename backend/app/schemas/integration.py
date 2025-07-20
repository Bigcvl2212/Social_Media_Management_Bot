"""
Pydantic schemas for integration models
"""

from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.integration import IntegrationType, IntegrationStatus


# Integration schemas
class IntegrationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: IntegrationType
    provider: str = Field(..., min_length=1, max_length=50)


class IntegrationCreate(IntegrationBase):
    config_data: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    webhook_url: Optional[str] = None


class IntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[IntegrationStatus] = None
    config_data: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    webhook_url: Optional[str] = None


class Integration(IntegrationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: IntegrationStatus
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None


class IntegrationWithConfig(Integration):
    """Integration with configuration data (for admin access)"""
    config_data: Optional[str] = None
    webhook_url: Optional[str] = None


# Campaign schemas
class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(email|sms)$")
    content: str = Field(..., min_length=1)
    subject: Optional[str] = Field(None, max_length=200)


class CampaignCreate(CampaignBase):
    integration_id: int
    is_scheduled: bool = False
    scheduled_at: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    subject: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    is_scheduled: Optional[bool] = None
    scheduled_at: Optional[datetime] = None


class Campaign(CampaignBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    integration_id: int
    user_id: int
    is_active: bool
    is_scheduled: bool
    scheduled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


# API Key schemas
class APIKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class APIKeyCreate(APIKeyBase):
    rate_limit: int = Field(1000, ge=1, le=10000)
    allowed_endpoints: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    rate_limit: Optional[int] = Field(None, ge=1, le=10000)
    allowed_endpoints: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class APIKey(APIKeyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    key_value: str
    user_id: int
    is_active: bool
    rate_limit: int
    total_requests: int
    last_used: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class APIKeyWithSecret(APIKey):
    """API Key with secret (for initial creation only)"""
    key_secret: Optional[str] = None


# Zapier Webhook schemas
class ZapierWebhookBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    trigger_event: str = Field(..., min_length=1, max_length=100)
    webhook_url: str = Field(..., pattern=r"^https?://.*")


class ZapierWebhookCreate(ZapierWebhookBase):
    payload_template: Optional[str] = None


class ZapierWebhookUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    trigger_event: Optional[str] = Field(None, min_length=1, max_length=100)
    webhook_url: Optional[str] = Field(None, pattern=r"^https?://.*")
    is_active: Optional[bool] = None
    payload_template: Optional[str] = None


class ZapierWebhook(ZapierWebhookBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    is_active: bool
    payload_template: Optional[str] = None
    total_triggers: int
    last_triggered: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Configuration schemas for specific integrations
class ShopifyConfig(BaseModel):
    shop_url: str = Field(..., pattern=r"^https://.*\.myshopify\.com$")
    access_token: str
    webhook_secret: Optional[str] = None


class HubSpotConfig(BaseModel):
    access_token: str
    portal_id: Optional[str] = None


class WooCommerceConfig(BaseModel):
    site_url: str = Field(..., pattern=r"^https?://.*")
    consumer_key: str
    consumer_secret: str


class MailchimpConfig(BaseModel):
    api_key: str
    server_prefix: str = Field(..., pattern=r"^us\d+$")
    list_id: Optional[str] = None


class TwilioConfig(BaseModel):
    account_sid: str
    auth_token: str
    from_number: str = Field(..., pattern=r"^\+\d{10,15}$")


# Generic configuration union
IntegrationConfig = ShopifyConfig | HubSpotConfig | WooCommerceConfig | MailchimpConfig | TwilioConfig