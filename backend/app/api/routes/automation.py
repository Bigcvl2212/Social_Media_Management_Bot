"""
API routes for automation and engagement features
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.automation import (
    # Direct Messages
    DirectMessageCreate, DirectMessageUpdate, DirectMessageResponse,
    DirectMessageLogResponse, DirectMessageStatsResponse,
    # Comment Management
    CommentManagementCreate, CommentManagementUpdate, CommentManagementResponse,
    CommentAnalysisResponse,
    # Moderation
    ModerationRuleCreate, ModerationRuleUpdate, ModerationRuleResponse,
    ModerationLogResponse,
    # Configuration
    AutomationConfigCreate, AutomationConfigUpdate, AutomationConfigResponse,
    AutomationDashboardResponse,
    # Batch operations
    BatchDirectMessageCreate, BatchModerationRuleCreate
)
from app.services.direct_message_service import DirectMessageService
from app.services.comment_management_service import CommentManagementService
from app.services.moderation_service import ModerationService
from app.services.automation_service import AutomationConfigService

router = APIRouter()


# Direct Messaging Endpoints
@router.post("/direct-messages", response_model=DirectMessageResponse)
async def create_dm_campaign(
    dm_data: DirectMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new direct message campaign"""
    try:
        service = DirectMessageService(db)
        dm_campaign = await service.create_dm_campaign(dm_data, current_user.id)
        return dm_campaign
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/direct-messages", response_model=List[DirectMessageResponse])
async def list_dm_campaigns(
    social_account_id: Optional[int] = Query(None),
    message_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List direct message campaigns"""
    service = DirectMessageService(db)
    campaigns, total = await service.list_dm_campaigns(
        current_user.id, social_account_id, message_type, is_active, page, size
    )
    return campaigns


@router.get("/direct-messages/{campaign_id}", response_model=DirectMessageResponse)
async def get_dm_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific direct message campaign"""
    service = DirectMessageService(db)
    campaign = await service.get_dm_campaign(campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return campaign


@router.put("/direct-messages/{campaign_id}", response_model=DirectMessageResponse)
async def update_dm_campaign(
    campaign_id: int,
    dm_data: DirectMessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a direct message campaign"""
    service = DirectMessageService(db)
    campaign = await service.update_dm_campaign(campaign_id, dm_data, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return campaign


@router.delete("/direct-messages/{campaign_id}")
async def delete_dm_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a direct message campaign"""
    service = DirectMessageService(db)
    success = await service.delete_dm_campaign(campaign_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return {"message": "Campaign deleted successfully"}


@router.get("/direct-messages/stats", response_model=DirectMessageStatsResponse)
async def get_dm_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get direct message statistics"""
    service = DirectMessageService(db)
    return await service.get_dm_stats(current_user.id)


@router.get("/direct-messages/logs", response_model=List[DirectMessageLogResponse])
async def get_dm_logs(
    campaign_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get direct message sending logs"""
    service = DirectMessageService(db)
    logs, total = await service.get_dm_logs(current_user.id, campaign_id, status, page, size)
    return logs


@router.post("/direct-messages/batch", response_model=List[DirectMessageResponse])
async def create_batch_dm_campaigns(
    batch_data: BatchDirectMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create multiple direct message campaigns"""
    service = DirectMessageService(db)
    campaigns = []
    
    for dm_data in batch_data.campaigns:
        try:
            campaign = await service.create_dm_campaign(dm_data, current_user.id)
            campaigns.append(campaign)
        except ValueError as e:
            # Continue with other campaigns, log error
            continue
    
    return campaigns


# Comment Management Endpoints
@router.post("/comments", response_model=CommentManagementResponse)
async def process_comment(
    comment_data: CommentManagementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process a new comment with AI analysis"""
    try:
        service = CommentManagementService(db)
        comment = await service.process_comment(comment_data, current_user.id)
        return comment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/comments", response_model=List[CommentManagementResponse])
async def list_comments(
    social_account_id: Optional[int] = Query(None),
    needs_attention: Optional[bool] = Query(None),
    is_spam: Optional[bool] = Query(None),
    is_processed: Optional[bool] = Query(None),
    sentiment: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List comments with filters"""
    service = CommentManagementService(db)
    comments, total = await service.list_comments(
        current_user.id, social_account_id, needs_attention, is_spam, 
        is_processed, sentiment, page, size
    )
    return comments


@router.get("/comments/{comment_id}", response_model=CommentManagementResponse)
async def get_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific comment"""
    service = CommentManagementService(db)
    comment = await service.get_comment(comment_id, current_user.id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.put("/comments/{comment_id}", response_model=CommentManagementResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentManagementUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a comment management entry"""
    service = CommentManagementService(db)
    comment = await service.update_comment(comment_id, comment_data, current_user.id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.get("/comments/stats")
async def get_comment_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comment management statistics"""
    service = CommentManagementService(db)
    return await service.get_comment_stats(current_user.id, days)


@router.post("/comments/bulk-process/{social_account_id}")
async def bulk_process_comments(
    social_account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk process pending comments for a social account"""
    service = CommentManagementService(db)
    return await service.bulk_process_comments(current_user.id, social_account_id)


# Moderation Endpoints
@router.post("/moderation/rules", response_model=ModerationRuleResponse)
async def create_moderation_rule(
    rule_data: ModerationRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new moderation rule"""
    try:
        service = ModerationService(db)
        rule = await service.create_moderation_rule(rule_data, current_user.id)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/moderation/rules", response_model=List[ModerationRuleResponse])
async def list_moderation_rules(
    social_account_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List moderation rules"""
    service = ModerationService(db)
    rules, total = await service.list_moderation_rules(
        current_user.id, social_account_id, is_active, page, size
    )
    return rules


@router.get("/moderation/rules/{rule_id}", response_model=ModerationRuleResponse)
async def get_moderation_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific moderation rule"""
    service = ModerationService(db)
    rule = await service.get_moderation_rule(rule_id, current_user.id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.put("/moderation/rules/{rule_id}", response_model=ModerationRuleResponse)
async def update_moderation_rule(
    rule_id: int,
    rule_data: ModerationRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a moderation rule"""
    service = ModerationService(db)
    rule = await service.update_moderation_rule(rule_id, rule_data, current_user.id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.delete("/moderation/rules/{rule_id}")
async def delete_moderation_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a moderation rule"""
    service = ModerationService(db)
    success = await service.delete_moderation_rule(rule_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return {"message": "Rule deleted successfully"}


@router.get("/moderation/logs", response_model=List[ModerationLogResponse])
async def get_moderation_logs(
    social_account_id: Optional[int] = Query(None),
    content_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    is_automated: Optional[bool] = Query(None),
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get moderation logs"""
    service = ModerationService(db)
    logs, total = await service.get_moderation_logs(
        current_user.id, social_account_id, content_type, action, 
        is_automated, days, page, size
    )
    return logs


@router.get("/moderation/stats")
async def get_moderation_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get moderation statistics"""
    service = ModerationService(db)
    return await service.get_moderation_stats(current_user.id, days)


@router.post("/moderation/rules/templates", response_model=List[ModerationRuleResponse])
async def create_template_rules(
    social_account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create template moderation rules"""
    service = ModerationService(db)
    rules = await service.create_template_rules(current_user.id, social_account_id)
    return rules


@router.post("/moderation/rules/batch", response_model=List[ModerationRuleResponse])
async def create_batch_moderation_rules(
    batch_data: BatchModerationRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create multiple moderation rules"""
    service = ModerationService(db)
    rules = []
    
    for rule_data in batch_data.rules:
        try:
            rule = await service.create_moderation_rule(rule_data, current_user.id)
            rules.append(rule)
        except ValueError as e:
            # Continue with other rules, log error
            continue
    
    return rules


# Configuration Endpoints
@router.get("/config", response_model=AutomationConfigResponse)
async def get_automation_config(
    social_account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get automation configuration"""
    service = AutomationConfigService(db)
    config = await service.get_automation_config(current_user.id, social_account_id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")
    return config


@router.post("/config", response_model=AutomationConfigResponse)
async def create_automation_config(
    config_data: AutomationConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create automation configuration"""
    try:
        service = AutomationConfigService(db)
        config = await service.create_automation_config(config_data, current_user.id)
        return config
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/config", response_model=AutomationConfigResponse)
async def update_automation_config(
    config_data: AutomationConfigUpdate,
    social_account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update automation configuration"""
    service = AutomationConfigService(db)
    config = await service.update_automation_config(config_data, current_user.id, social_account_id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")
    return config


@router.get("/config/all", response_model=List[AutomationConfigResponse])
async def list_automation_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all automation configurations for user"""
    service = AutomationConfigService(db)
    return await service.list_automation_configs(current_user.id)


# Dashboard and Analytics Endpoints
@router.get("/dashboard", response_model=AutomationDashboardResponse)
async def get_automation_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive automation dashboard"""
    service = AutomationConfigService(db)
    return await service.get_automation_dashboard(current_user.id)


@router.get("/health")
async def get_automation_health(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get automation system health check"""
    service = AutomationConfigService(db)
    return await service.get_automation_health_check(current_user.id)


@router.get("/insights")
async def get_automation_insights(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get automation insights and recommendations"""
    service = AutomationConfigService(db)
    return await service.get_automation_insights(current_user.id, days)


# Feature Toggle Endpoints
@router.post("/toggle/{feature}")
async def toggle_automation_feature(
    feature: str,
    enabled: bool = Query(...),
    social_account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle specific automation feature on/off"""
    try:
        service = AutomationConfigService(db)
        success = await service.toggle_automation_feature(
            current_user.id, feature, enabled, social_account_id
        )
        return {"message": f"Feature {feature} {'enabled' if enabled else 'disabled'} successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))