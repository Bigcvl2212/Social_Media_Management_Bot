

# Import all models here to ensure they are registered with SQLAlchemy
from .monetization import Brand, Campaign, Collaboration, AffiliateLink

from app.models.user import User
from app.models.curation import CurationCollection
from app.models.automation import DirectMessage, CommentManagement, ModerationRule, ModerationLog, AutomationConfig


"""
Database models for the Social Media Management Bot
"""

from .user import User, UserRole
from .social_account import SocialAccount, SocialPlatform
from .content import Content, ContentStatus
from .analytics import Analytics
from .integration import (
    Integration,
    IntegrationCampaign,
    APIKey,
    ZapierWebhook,
    IntegrationType,
    IntegrationStatus
)
from .automation import (
    DirectMessage,
    DirectMessageLog,
    CommentManagement,
    ModerationRule,
    ModerationLog,
    AutomationConfig,
    DirectMessageType,
    DirectMessageStatus,
    CommentAction,
    ModerationAction
)

__all__ = [
    "User",
    "UserRole",
    "SocialAccount",
    "SocialPlatform",
    "Content",
    "ContentStatus",
    "Analytics",
    "Integration",
    "IntegrationCampaign",
    "APIKey",
    "ZapierWebhook",
    "IntegrationType",
    "IntegrationStatus",
    "DirectMessage",
    "DirectMessageLog",
    "CommentManagement",
    "ModerationRule",
    "ModerationLog",
    "AutomationConfig",
    "DirectMessageType",
    "DirectMessageStatus",
    "CommentAction",
    "ModerationAction",
]

