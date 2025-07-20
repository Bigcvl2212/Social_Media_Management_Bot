"""
Pydantic schemas for automation and engagement features
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.automation import (
    DirectMessageType, DirectMessageStatus, CommentAction, ModerationAction
)


# Direct Messaging Schemas
class DirectMessageCreate(BaseModel):
    """Schema for creating a direct message campaign"""
    social_account_id: int
    message_type: DirectMessageType
    subject: Optional[str] = None
    message_content: str = Field(..., min_length=1, max_length=2000)
    target_criteria: Optional[Dict[str, Any]] = None
    send_delay_minutes: int = Field(default=0, ge=0, le=1440)  # Max 24 hours
    max_sends_per_day: int = Field(default=50, ge=1, le=200)
    is_active: bool = True


class DirectMessageUpdate(BaseModel):
    """Schema for updating a direct message campaign"""
    subject: Optional[str] = None
    message_content: Optional[str] = Field(None, min_length=1, max_length=2000)
    target_criteria: Optional[Dict[str, Any]] = None
    send_delay_minutes: Optional[int] = Field(None, ge=0, le=1440)
    max_sends_per_day: Optional[int] = Field(None, ge=1, le=200)
    is_active: Optional[bool] = None


class DirectMessageResponse(BaseModel):
    """Schema for direct message campaign response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    social_account_id: int
    message_type: DirectMessageType
    subject: Optional[str]
    message_content: str
    target_criteria: Optional[Dict[str, Any]]
    send_delay_minutes: int
    status: DirectMessageStatus
    sent_count: int
    success_count: int
    failure_count: int
    is_active: bool
    max_sends_per_day: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_sent_at: Optional[datetime]


class DirectMessageLogResponse(BaseModel):
    """Schema for direct message log response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    direct_message_id: int
    recipient_id: str
    recipient_username: Optional[str]
    sent_content: str
    platform_message_id: Optional[str]
    status: DirectMessageStatus
    error_message: Optional[str]
    sent_at: datetime


class DirectMessageStatsResponse(BaseModel):
    """Schema for direct message statistics"""
    total_campaigns: int
    active_campaigns: int
    total_sent: int
    success_rate: float
    recent_sends: int  # Last 24 hours


# Comment Management Schemas
class CommentManagementCreate(BaseModel):
    """Schema for creating comment management entry"""
    social_account_id: int
    platform_comment_id: str
    content_id: str
    comment_text: str
    commenter_id: str
    commenter_username: Optional[str] = None
    comment_timestamp: datetime


class CommentManagementUpdate(BaseModel):
    """Schema for updating comment management"""
    action_taken: Optional[CommentAction] = None
    auto_response: Optional[str] = None
    escalated_to_user: Optional[bool] = None
    needs_attention: Optional[bool] = None
    is_spam: Optional[bool] = None


class CommentManagementResponse(BaseModel):
    """Schema for comment management response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    social_account_id: int
    platform_comment_id: str
    content_id: str
    comment_text: str
    commenter_id: str
    commenter_username: Optional[str]
    sentiment_score: Optional[str]
    spam_score: Optional[str]
    toxicity_score: Optional[str]
    ai_summary: Optional[str]
    action_taken: Optional[CommentAction]
    auto_response: Optional[str]
    escalated_to_user: bool
    is_processed: bool
    needs_attention: bool
    is_spam: bool
    created_at: datetime
    processed_at: Optional[datetime]
    comment_timestamp: datetime


class CommentAnalysisResponse(BaseModel):
    """Schema for AI comment analysis results"""
    sentiment_score: str  # positive, negative, neutral
    spam_score: str  # low, medium, high
    toxicity_score: str  # low, medium, high
    ai_summary: str
    recommended_action: CommentAction
    confidence_score: float


# Moderation Schemas
class ModerationRuleCreate(BaseModel):
    """Schema for creating moderation rule"""
    social_account_id: Optional[int] = None  # Null for global rules
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    conditions: Dict[str, Any]  # Keywords, patterns, user criteria
    action: ModerationAction
    auto_response_message: Optional[str] = None
    severity_level: int = Field(default=1, ge=1, le=3)
    applies_to_comments: bool = True
    applies_to_posts: bool = False
    applies_to_live_streams: bool = False
    is_active: bool = True


class ModerationRuleUpdate(BaseModel):
    """Schema for updating moderation rule"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    action: Optional[ModerationAction] = None
    auto_response_message: Optional[str] = None
    severity_level: Optional[int] = Field(None, ge=1, le=3)
    applies_to_comments: Optional[bool] = None
    applies_to_posts: Optional[bool] = None
    applies_to_live_streams: Optional[bool] = None
    is_active: Optional[bool] = None


class ModerationRuleResponse(BaseModel):
    """Schema for moderation rule response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    social_account_id: Optional[int]
    name: str
    description: Optional[str]
    conditions: Dict[str, Any]
    action: ModerationAction
    auto_response_message: Optional[str]
    is_active: bool
    severity_level: int
    applies_to_comments: bool
    applies_to_posts: bool
    applies_to_live_streams: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_triggered_at: Optional[datetime]
    trigger_count: int


class ModerationLogResponse(BaseModel):
    """Schema for moderation log response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    rule_id: Optional[int]
    user_id: int
    social_account_id: int
    content_type: str
    platform_content_id: str
    content_text: Optional[str]
    author_id: str
    author_username: Optional[str]
    action_taken: ModerationAction
    reason: Optional[str]
    is_automated: bool
    created_at: datetime
    content_timestamp: datetime


# Automation Configuration Schemas
class AutomationConfigCreate(BaseModel):
    """Schema for creating automation configuration"""
    social_account_id: Optional[int] = None  # Null for global config
    dm_automation_enabled: bool = False
    comment_management_enabled: bool = False
    auto_moderation_enabled: bool = False
    ai_confidence_threshold: str = Field(default="medium", pattern="^(low|medium|high)$")
    auto_escalation_enabled: bool = True
    max_dms_per_hour: int = Field(default=10, ge=1, le=100)
    max_responses_per_hour: int = Field(default=20, ge=1, le=200)
    business_hours: Optional[Dict[str, Any]] = None
    notify_on_escalation: bool = True
    notify_on_spam_detection: bool = True
    notification_email: Optional[str] = None


class AutomationConfigUpdate(BaseModel):
    """Schema for updating automation configuration"""
    dm_automation_enabled: Optional[bool] = None
    comment_management_enabled: Optional[bool] = None
    auto_moderation_enabled: Optional[bool] = None
    ai_confidence_threshold: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    auto_escalation_enabled: Optional[bool] = None
    max_dms_per_hour: Optional[int] = Field(None, ge=1, le=100)
    max_responses_per_hour: Optional[int] = Field(None, ge=1, le=200)
    business_hours: Optional[Dict[str, Any]] = None
    notify_on_escalation: Optional[bool] = None
    notify_on_spam_detection: Optional[bool] = None
    notification_email: Optional[str] = None


class AutomationConfigResponse(BaseModel):
    """Schema for automation configuration response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    social_account_id: Optional[int]
    dm_automation_enabled: bool
    comment_management_enabled: bool
    auto_moderation_enabled: bool
    ai_confidence_threshold: str
    auto_escalation_enabled: bool
    max_dms_per_hour: int
    max_responses_per_hour: int
    business_hours: Optional[Dict[str, Any]]
    notify_on_escalation: bool
    notify_on_spam_detection: bool
    notification_email: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


# Dashboard and Analytics Schemas
class AutomationDashboardResponse(BaseModel):
    """Schema for automation dashboard statistics"""
    dm_stats: DirectMessageStatsResponse
    comment_stats: Dict[str, Any]
    moderation_stats: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]


class AutomationActivityResponse(BaseModel):
    """Schema for recent automation activity"""
    activity_type: str  # dm_sent, comment_processed, content_moderated
    description: str
    timestamp: datetime
    status: str
    platform: str
    details: Optional[Dict[str, Any]] = None


# Batch Operations
class BatchDirectMessageCreate(BaseModel):
    """Schema for creating multiple direct message campaigns"""
    campaigns: List[DirectMessageCreate]


class BatchModerationRuleCreate(BaseModel):
    """Schema for creating multiple moderation rules"""
    rules: List[ModerationRuleCreate]