"""
Integration models for CRM, e-commerce, email/SMS, and API management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class IntegrationType(str, enum.Enum):
    """Types of integrations supported"""
    CRM = "crm"
    ECOMMERCE = "ecommerce"
    EMAIL = "email"
    SMS = "sms"
    API = "api"
    ZAPIER = "zapier"


class IntegrationStatus(str, enum.Enum):
    """Status of integrations"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


class Integration(Base):
    """Base model for all integrations"""
    
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(IntegrationType), nullable=False)
    provider = Column(String, nullable=False)  # e.g., "shopify", "hubspot", "mailchimp"
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING)
    
    # Configuration stored as JSON-like text
    config_data = Column(Text, nullable=True)  # Encrypted configuration data
    api_key = Column(String, nullable=True)  # Encrypted API key
    api_secret = Column(String, nullable=True)  # Encrypted API secret
    webhook_url = Column(String, nullable=True)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Table configuration
    __table_args__ = {'extend_existing': True}
    
    # Relationships
    user = relationship("User", back_populates="integrations")
    campaigns = relationship("IntegrationCampaign", back_populates="integration", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Integration(id={self.id}, name='{self.name}', type='{self.type}', provider='{self.provider}')>"


class IntegrationCampaign(Base):
    """Campaign model for email/SMS campaigns"""
    
    __tablename__ = "integration_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "email" or "sms"
    subject = Column(String, nullable=True)  # For email campaigns
    content = Column(Text, nullable=False)
    
    # Campaign settings
    is_active = Column(Boolean, default=True)
    is_scheduled = Column(Boolean, default=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Integration association
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    integration = relationship("Integration", back_populates="campaigns")
    user = relationship("User", back_populates="campaigns")
    
    def __repr__(self):
        return f"<IntegrationCampaign(id={self.id}, name='{self.name}', type='{self.type}')>"


class APIKey(Base):
    """Public API key management"""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key_value = Column(String, unique=True, nullable=False, index=True)
    key_secret = Column(String, nullable=True)  # For OAuth-like flows
    
    # Permissions and limits
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=1000)  # Requests per hour
    allowed_endpoints = Column(Text, nullable=True)  # JSON array of allowed endpoints
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class ZapierWebhook(Base):
    """Zapier webhook configurations"""
    
    __tablename__ = "zapier_webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    trigger_event = Column(String, nullable=False)  # e.g., "content_posted", "campaign_sent"
    webhook_url = Column(String, nullable=False)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    payload_template = Column(Text, nullable=True)  # Custom payload format
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Usage tracking
    total_triggers = Column(Integer, default=0)
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="zapier_webhooks")
    
    def __repr__(self):
        return f"<ZapierWebhook(id={self.id}, name='{self.name}', trigger='{self.trigger_event}')>"