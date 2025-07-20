"""
Automation configuration service for managing automation settings and admin controls
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from loguru import logger

from app.models.automation import AutomationConfig
from app.models.social_account import SocialAccount
from app.schemas.automation import (
    AutomationConfigCreate, AutomationConfigUpdate, AutomationDashboardResponse,
    AutomationActivityResponse
)
from app.services.direct_message_service import DirectMessageService
from app.services.comment_management_service import CommentManagementService
from app.services.moderation_service import ModerationService


class AutomationConfigService:
    """Service for automation configuration and admin controls"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dm_service = DirectMessageService(db)
        self.comment_service = CommentManagementService(db)
        self.moderation_service = ModerationService(db)
    
    async def create_automation_config(
        self, 
        config_data: AutomationConfigCreate, 
        user_id: int
    ) -> AutomationConfig:
        """Create automation configuration"""
        
        # Verify user owns the social account (if specified)
        if config_data.social_account_id:
            social_account_query = select(SocialAccount).where(
                and_(SocialAccount.id == config_data.social_account_id, SocialAccount.user_id == user_id)
            )
            social_account_result = await self.db.execute(social_account_query)
            social_account = social_account_result.scalar_one_or_none()
            
            if not social_account:
                raise ValueError("Social account not found or not owned by user")
        
        # Check if config already exists for this user/account combination
        existing_query = select(AutomationConfig).where(
            and_(
                AutomationConfig.user_id == user_id,
                AutomationConfig.social_account_id == config_data.social_account_id
            )
        )
        existing_result = await self.db.execute(existing_query)
        existing_config = existing_result.scalar_one_or_none()
        
        if existing_config:
            raise ValueError("Automation configuration already exists for this account")
        
        config = AutomationConfig(
            **config_data.model_dump(),
            user_id=user_id
        )
        
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        
        logger.info(f"Created automation config {config.id} for user {user_id}")
        return config
    
    async def get_automation_config(
        self, 
        user_id: int, 
        social_account_id: Optional[int] = None
    ) -> Optional[AutomationConfig]:
        """Get automation configuration for user/account"""
        
        query = select(AutomationConfig).where(
            and_(
                AutomationConfig.user_id == user_id,
                AutomationConfig.social_account_id == social_account_id
            )
        ).options(selectinload(AutomationConfig.social_account))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_automation_config(
        self, 
        config_data: AutomationConfigUpdate, 
        user_id: int,
        social_account_id: Optional[int] = None
    ) -> Optional[AutomationConfig]:
        """Update automation configuration"""
        
        config = await self.get_automation_config(user_id, social_account_id)
        if not config:
            # Create default config if none exists
            create_data = AutomationConfigCreate(
                social_account_id=social_account_id,
                **config_data.model_dump(exclude_unset=True)
            )
            return await self.create_automation_config(create_data, user_id)
        
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        await self.db.commit()
        await self.db.refresh(config)
        
        logger.info(f"Updated automation config for user {user_id}")
        return config
    
    async def list_automation_configs(self, user_id: int) -> List[AutomationConfig]:
        """List all automation configurations for a user"""
        
        query = select(AutomationConfig).where(AutomationConfig.user_id == user_id)
        query = query.options(selectinload(AutomationConfig.social_account))
        query = query.order_by(AutomationConfig.created_at)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_automation_dashboard(self, user_id: int) -> AutomationDashboardResponse:
        """Get comprehensive automation dashboard data"""
        
        # Get DM statistics
        dm_stats = await self.dm_service.get_dm_stats(user_id)
        
        # Get comment management statistics
        comment_stats = await self.comment_service.get_comment_stats(user_id)
        
        # Get moderation statistics
        moderation_stats = await self.moderation_service.get_moderation_stats(user_id)
        
        # Get recent activity
        recent_activity = await self._get_recent_activity(user_id)
        
        return AutomationDashboardResponse(
            dm_stats=dm_stats,
            comment_stats=comment_stats,
            moderation_stats=moderation_stats,
            recent_activity=recent_activity
        )
    
    async def get_automation_health_check(self, user_id: int) -> Dict[str, Any]:
        """Perform health check on automation systems"""
        
        health_status = {
            "overall_status": "healthy",
            "direct_messages": {"status": "healthy", "issues": []},
            "comment_management": {"status": "healthy", "issues": []},
            "moderation": {"status": "healthy", "issues": []},
            "configuration": {"status": "healthy", "issues": []}
        }
        
        # Check DM system health
        dm_stats = await self.dm_service.get_dm_stats(user_id)
        if dm_stats.total_campaigns > 0 and dm_stats.success_rate < 50:
            health_status["direct_messages"]["status"] = "warning"
            health_status["direct_messages"]["issues"].append("Low success rate for DM campaigns")
        
        # Check comment system health
        comment_stats = await self.comment_service.get_comment_stats(user_id)
        if comment_stats.get("pending_attention", 0) > 50:
            health_status["comment_management"]["status"] = "warning"
            health_status["comment_management"]["issues"].append("High number of pending comments")
        
        # Check moderation system health
        moderation_stats = await self.moderation_service.get_moderation_stats(user_id)
        if moderation_stats.get("active_rules", 0) == 0:
            health_status["moderation"]["status"] = "info"
            health_status["moderation"]["issues"].append("No active moderation rules configured")
        
        # Check configuration issues
        configs = await self.list_automation_configs(user_id)
        if not configs:
            health_status["configuration"]["status"] = "warning"
            health_status["configuration"]["issues"].append("No automation configuration found")
        
        # Determine overall status
        statuses = [item["status"] for item in health_status.values() if isinstance(item, dict)]
        if "warning" in statuses:
            health_status["overall_status"] = "warning"
        elif "error" in statuses:
            health_status["overall_status"] = "error"
        
        return health_status
    
    async def toggle_automation_feature(
        self, 
        user_id: int, 
        feature: str, 
        enabled: bool,
        social_account_id: Optional[int] = None
    ) -> bool:
        """Toggle specific automation feature on/off"""
        
        config = await self.get_automation_config(user_id, social_account_id)
        if not config:
            # Create default config
            create_data = AutomationConfigCreate(social_account_id=social_account_id)
            config = await self.create_automation_config(create_data, user_id)
        
        # Update the specific feature
        if feature == "dm_automation":
            config.dm_automation_enabled = enabled
        elif feature == "comment_management":
            config.comment_management_enabled = enabled
        elif feature == "auto_moderation":
            config.auto_moderation_enabled = enabled
        elif feature == "auto_escalation":
            config.auto_escalation_enabled = enabled
        else:
            raise ValueError(f"Unknown automation feature: {feature}")
        
        await self.db.commit()
        
        logger.info(f"Toggled {feature} to {enabled} for user {user_id}")
        return True
    
    async def update_rate_limits(
        self, 
        user_id: int, 
        max_dms_per_hour: Optional[int] = None,
        max_responses_per_hour: Optional[int] = None,
        social_account_id: Optional[int] = None
    ) -> bool:
        """Update rate limiting settings"""
        
        config = await self.get_automation_config(user_id, social_account_id)
        if not config:
            return False
        
        if max_dms_per_hour is not None:
            config.max_dms_per_hour = max_dms_per_hour
        
        if max_responses_per_hour is not None:
            config.max_responses_per_hour = max_responses_per_hour
        
        await self.db.commit()
        
        logger.info(f"Updated rate limits for user {user_id}")
        return True
    
    async def setup_business_hours(
        self, 
        user_id: int, 
        business_hours: Dict[str, Any],
        social_account_id: Optional[int] = None
    ) -> bool:
        """Configure business hours for automation"""
        
        config = await self.get_automation_config(user_id, social_account_id)
        if not config:
            return False
        
        # Validate business hours format
        required_fields = ["start", "end", "timezone"]
        if not all(field in business_hours for field in required_fields):
            raise ValueError("Business hours must include start, end, and timezone")
        
        config.business_hours = business_hours
        await self.db.commit()
        
        logger.info(f"Updated business hours for user {user_id}")
        return True
    
    async def get_automation_insights(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get insights and recommendations for automation improvement"""
        
        insights = {
            "recommendations": [],
            "performance_metrics": {},
            "optimization_suggestions": []
        }
        
        # Get statistics
        dm_stats = await self.dm_service.get_dm_stats(user_id)
        comment_stats = await self.comment_service.get_comment_stats(user_id, days)
        moderation_stats = await self.moderation_service.get_moderation_stats(user_id, days)
        
        # Analyze performance and provide recommendations
        if dm_stats.success_rate < 70:
            insights["recommendations"].append({
                "type": "dm_improvement",
                "message": "Consider reviewing your DM templates and targeting criteria to improve success rate",
                "priority": "medium"
            })
        
        if comment_stats.get("automation_rate", 0) < 50:
            insights["recommendations"].append({
                "type": "comment_automation",
                "message": "Increase comment automation by refining AI confidence thresholds",
                "priority": "low"
            })
        
        if moderation_stats.get("active_rules", 0) < 3:
            insights["recommendations"].append({
                "type": "moderation_setup",
                "message": "Consider setting up more moderation rules to automate content management",
                "priority": "medium"
            })
        
        # Performance metrics
        insights["performance_metrics"] = {
            "dm_success_rate": dm_stats.success_rate,
            "comment_automation_rate": comment_stats.get("automation_rate", 0),
            "moderation_automation_rate": moderation_stats.get("automation_rate", 0),
            "total_time_saved_hours": self._calculate_time_saved(dm_stats, comment_stats, moderation_stats)
        }
        
        # Optimization suggestions
        if dm_stats.recent_sends == 0:
            insights["optimization_suggestions"].append("No recent DM activity - check if campaigns are active")
        
        if comment_stats.get("pending_attention", 0) > 20:
            insights["optimization_suggestions"].append("High number of pending comments - consider adjusting AI thresholds")
        
        return insights
    
    async def _get_recent_activity(self, user_id: int) -> List[Dict[str, Any]]:
        """Get recent automation activity for dashboard"""
        
        activities = []
        
        # Get recent DM sends
        dm_logs, _ = await self.dm_service.get_dm_logs(user_id, page=1, size=5)
        for log in dm_logs:
            activities.append({
                "activity_type": "dm_sent",
                "description": f"Direct message sent to {log.recipient_username or log.recipient_id}",
                "timestamp": log.sent_at,
                "status": log.status.value,
                "platform": "multiple",  # Would get from related social account
                "details": {"message_id": log.platform_message_id}
            })
        
        # Get recent comment processing
        comments, _ = await self.comment_service.list_comments(
            user_id, 
            is_processed=True, 
            page=1, 
            size=5
        )
        for comment in comments:
            activities.append({
                "activity_type": "comment_processed",
                "description": f"Comment processed with {comment.action_taken.value if comment.action_taken else 'analysis'}",
                "timestamp": comment.processed_at or comment.created_at,
                "status": "success" if comment.is_processed else "pending",
                "platform": comment.social_account.platform.value if comment.social_account else "unknown",
                "details": {"sentiment": comment.sentiment_score}
            })
        
        # Get recent moderation actions
        mod_logs, _ = await self.moderation_service.get_moderation_logs(
            user_id, 
            page=1, 
            size=5
        )
        for log in mod_logs:
            activities.append({
                "activity_type": "content_moderated",
                "description": f"Content moderated with action: {log.action_taken.value}",
                "timestamp": log.created_at,
                "status": "automated" if log.is_automated else "manual",
                "platform": log.social_account.platform.value if log.social_account else "unknown",
                "details": {"content_type": log.content_type}
            })
        
        # Sort by timestamp and return most recent
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:10]
    
    def _calculate_time_saved(self, dm_stats, comment_stats, moderation_stats) -> float:
        """Calculate estimated time saved through automation"""
        
        # Rough estimates of time per action
        TIME_PER_DM = 2  # minutes
        TIME_PER_COMMENT = 1  # minutes
        TIME_PER_MODERATION = 0.5  # minutes
        
        dm_time_saved = dm_stats.success_count * TIME_PER_DM
        comment_time_saved = comment_stats.get("auto_processed", 0) * TIME_PER_COMMENT
        moderation_time_saved = moderation_stats.get("automated_actions", 0) * TIME_PER_MODERATION
        
        total_minutes = dm_time_saved + comment_time_saved + moderation_time_saved
        return round(total_minutes / 60, 1)  # Convert to hours