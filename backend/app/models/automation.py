"""
Automation and Engagement models for direct messaging, comment management, and moderation
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class DirectMessageType(str, enum.Enum):
    """Types of automated direct messages"""
    WELCOME = "welcome"
    FOLLOW_UP = "follow_up"
    THANK_YOU = "thank_you"
    PROMOTION = "promotion"
    CUSTOM = "custom"


class DirectMessageStatus(str, enum.Enum):
    """Status of direct message sending"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class CommentAction(str, enum.Enum):
    """Actions for comment management"""
    AUTO_RESPOND = "auto_respond"
    ESCALATE = "escalate"
    FILTER_SPAM = "filter_spam"
    APPROVE = "approve"
    DELETE = "delete"
    HIDE = "hide"


class ModerationAction(str, enum.Enum):
    """Actions for content moderation"""
    AUTO_APPROVE = "auto_approve"
    AUTO_REJECT = "auto_reject"
    MANUAL_REVIEW = "manual_review"
    BAN_USER = "ban_user"
    WARN_USER = "warn_user"
    DELETE_CONTENT = "delete_content"


class DirectMessage(Base):
    """Model for automated direct message campaigns"""
    
    __tablename__ = "direct_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False)
    
    # Message details
    message_type = Column(SQLEnum(DirectMessageType), nullable=False)
    subject = Column(String(200), nullable=True)  # For platforms that support it
    message_content = Column(Text, nullable=False)
    
    # Targeting and conditions
    target_criteria = Column(JSON, nullable=True)  # Conditions for sending (new followers, etc.)
    send_delay_minutes = Column(Integer, default=0)  # Delay after trigger
    
    # Status and tracking
    status = Column(SQLEnum(DirectMessageStatus), default=DirectMessageStatus.PENDING)
    sent_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Settings
    is_active = Column(Boolean, default=True)
    max_sends_per_day = Column(Integer, default=50)  # Rate limiting
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="direct_messages")
    social_account = relationship("SocialAccount", back_populates="direct_messages")
    message_logs = relationship("DirectMessageLog", back_populates="direct_message", cascade="all, delete-orphan")


class DirectMessageLog(Base):
    """Log of individual direct message sends"""
    
    __tablename__ = "direct_message_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    direct_message_id = Column(Integer, ForeignKey("direct_messages.id"), nullable=False)
    
    # Recipient details
    recipient_id = Column(String, nullable=False)  # Platform-specific user ID
    recipient_username = Column(String, nullable=True)
    
    # Message details
    sent_content = Column(Text, nullable=False)
    platform_message_id = Column(String, nullable=True)  # Platform's message ID
    
    # Status
    status = Column(SQLEnum(DirectMessageStatus), nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    direct_message = relationship("DirectMessage", back_populates="message_logs")


class CommentManagement(Base):
    """Model for AI-driven comment and inbox management"""
    
    __tablename__ = "comment_management"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False)
    
    # Comment details
    platform_comment_id = Column(String, nullable=False)
    content_id = Column(String, nullable=False)  # Platform content ID
    comment_text = Column(Text, nullable=False)
    commenter_id = Column(String, nullable=False)
    commenter_username = Column(String, nullable=True)
    
    # AI Analysis
    sentiment_score = Column(String, nullable=True)  # positive, negative, neutral
    spam_score = Column(String, nullable=True)  # low, medium, high
    toxicity_score = Column(String, nullable=True)  # low, medium, high
    ai_summary = Column(Text, nullable=True)
    
    # Actions taken
    action_taken = Column(SQLEnum(CommentAction), nullable=True)
    auto_response = Column(Text, nullable=True)
    escalated_to_user = Column(Boolean, default=False)
    
    # Status
    is_processed = Column(Boolean, default=False)
    needs_attention = Column(Boolean, default=False)
    is_spam = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    comment_timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="comment_management")
    social_account = relationship("SocialAccount", back_populates="comment_management")


class ModerationRule(Base):
    """Rules for community moderation"""
    
    __tablename__ = "moderation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=True)  # Null for global rules
    
    # Rule details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Conditions (JSON format for flexibility)
    conditions = Column(JSON, nullable=False)  # Keywords, patterns, user criteria, etc.
    
    # Actions
    action = Column(SQLEnum(ModerationAction), nullable=False)
    auto_response_message = Column(Text, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    severity_level = Column(Integer, default=1)  # 1=low, 2=medium, 3=high
    applies_to_comments = Column(Boolean, default=True)
    applies_to_posts = Column(Boolean, default=False)
    applies_to_live_streams = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    trigger_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="moderation_rules")
    social_account = relationship("SocialAccount", back_populates="moderation_rules")
    moderation_logs = relationship("ModerationLog", back_populates="rule", cascade="all, delete-orphan")


class ModerationLog(Base):
    """Log of moderation actions taken"""
    
    __tablename__ = "moderation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("moderation_rules.id"), nullable=True)  # Null for manual actions
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False)
    
    # Content details
    content_type = Column(String(50), nullable=False)  # comment, post, live_stream
    platform_content_id = Column(String, nullable=False)
    content_text = Column(Text, nullable=True)
    author_id = Column(String, nullable=False)
    author_username = Column(String, nullable=True)
    
    # Action details
    action_taken = Column(SQLEnum(ModerationAction), nullable=False)
    reason = Column(Text, nullable=True)
    is_automated = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    content_timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    rule = relationship("ModerationRule", back_populates="moderation_logs")
    user = relationship("User", back_populates="moderation_logs")
    social_account = relationship("SocialAccount", back_populates="moderation_logs")


class AutomationConfig(Base):
    """Configuration settings for automation features"""
    
    __tablename__ = "automation_config"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=True)  # Null for global config
    
    # Feature toggles
    dm_automation_enabled = Column(Boolean, default=False)
    comment_management_enabled = Column(Boolean, default=False)
    auto_moderation_enabled = Column(Boolean, default=False)
    
    # AI settings
    ai_confidence_threshold = Column(String, default="medium")  # low, medium, high
    auto_escalation_enabled = Column(Boolean, default=True)
    
    # Rate limiting
    max_dms_per_hour = Column(Integer, default=10)
    max_responses_per_hour = Column(Integer, default=20)
    
    # Business hours (JSON format)
    business_hours = Column(JSON, nullable=True)  # {"start": "09:00", "end": "17:00", "timezone": "UTC"}
    
    # Notification settings
    notify_on_escalation = Column(Boolean, default=True)
    notify_on_spam_detection = Column(Boolean, default=True)
    notification_email = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="automation_config")
    social_account = relationship("SocialAccount", back_populates="automation_config")