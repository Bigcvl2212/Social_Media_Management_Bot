"""
Direct messaging automation service
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import asyncio
from loguru import logger

from app.models.automation import DirectMessage, DirectMessageLog, DirectMessageType, DirectMessageStatus
from app.models.social_account import SocialAccount
from app.schemas.automation import (
    DirectMessageCreate, DirectMessageUpdate, DirectMessageStatsResponse
)


class DirectMessageService:
    """Service for automated direct messaging functionality"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_dm_campaign(self, dm_data: DirectMessageCreate, user_id: int) -> DirectMessage:
        """Create a new direct message campaign"""
        
        # Verify user owns the social account
        social_account_query = select(SocialAccount).where(
            and_(SocialAccount.id == dm_data.social_account_id, SocialAccount.user_id == user_id)
        )
        social_account_result = await self.db.execute(social_account_query)
        social_account = social_account_result.scalar_one_or_none()
        
        if not social_account:
            raise ValueError("Social account not found or not owned by user")
        
        dm_campaign = DirectMessage(
            **dm_data.model_dump(),
            user_id=user_id
        )
        
        self.db.add(dm_campaign)
        await self.db.commit()
        await self.db.refresh(dm_campaign)
        
        logger.info(f"Created DM campaign {dm_campaign.id} for user {user_id}")
        return dm_campaign
    
    async def get_dm_campaign(self, campaign_id: int, user_id: int) -> Optional[DirectMessage]:
        """Get a direct message campaign by ID"""
        
        query = select(DirectMessage).where(
            and_(DirectMessage.id == campaign_id, DirectMessage.user_id == user_id)
        ).options(
            selectinload(DirectMessage.social_account),
            selectinload(DirectMessage.message_logs)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_dm_campaigns(
        self, 
        user_id: int, 
        social_account_id: Optional[int] = None,
        message_type: Optional[DirectMessageType] = None,
        is_active: Optional[bool] = None,
        page: int = 1, 
        size: int = 20
    ) -> tuple[List[DirectMessage], int]:
        """List user's direct message campaigns with filters"""
        
        query = select(DirectMessage).where(DirectMessage.user_id == user_id)
        
        # Apply filters
        if social_account_id:
            query = query.where(DirectMessage.social_account_id == social_account_id)
        
        if message_type:
            query = query.where(DirectMessage.message_type == message_type)
        
        if is_active is not None:
            query = query.where(DirectMessage.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(DirectMessage.created_at)).offset((page - 1) * size).limit(size)
        query = query.options(selectinload(DirectMessage.social_account))
        
        result = await self.db.execute(query)
        campaigns = list(result.scalars().all())
        
        return campaigns, total
    
    async def update_dm_campaign(
        self, 
        campaign_id: int, 
        dm_data: DirectMessageUpdate, 
        user_id: int
    ) -> Optional[DirectMessage]:
        """Update a direct message campaign"""
        
        campaign = await self.get_dm_campaign(campaign_id, user_id)
        if not campaign:
            return None
        
        update_data = dm_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)
        
        await self.db.commit()
        await self.db.refresh(campaign)
        
        logger.info(f"Updated DM campaign {campaign_id} for user {user_id}")
        return campaign
    
    async def delete_dm_campaign(self, campaign_id: int, user_id: int) -> bool:
        """Delete a direct message campaign"""
        
        campaign = await self.get_dm_campaign(campaign_id, user_id)
        if not campaign:
            return False
        
        await self.db.delete(campaign)
        await self.db.commit()
        
        logger.info(f"Deleted DM campaign {campaign_id} for user {user_id}")
        return True
    
    async def send_direct_message(
        self, 
        campaign_id: int, 
        recipient_id: str, 
        recipient_username: Optional[str] = None
    ) -> DirectMessageLog:
        """Send a direct message to a specific recipient"""
        
        campaign_query = select(DirectMessage).where(DirectMessage.id == campaign_id)
        campaign_result = await self.db.execute(campaign_query)
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign or not campaign.is_active:
            raise ValueError("Campaign not found or not active")
        
        # Check rate limits
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        recent_sends_query = select(func.count()).select_from(DirectMessageLog).where(
            and_(
                DirectMessageLog.direct_message_id == campaign_id,
                DirectMessageLog.sent_at >= current_hour
            )
        )
        recent_sends_result = await self.db.execute(recent_sends_query)
        recent_sends = recent_sends_result.scalar()
        
        if recent_sends >= campaign.max_sends_per_day // 24:  # Rough hourly limit
            raise ValueError("Rate limit exceeded for this campaign")
        
        # Create message log entry
        message_log = DirectMessageLog(
            direct_message_id=campaign_id,
            recipient_id=recipient_id,
            recipient_username=recipient_username,
            sent_content=campaign.message_content,
            status=DirectMessageStatus.PENDING
        )
        
        try:
            # Here would be the actual platform API call
            # For now, we'll simulate success
            success = await self._send_message_to_platform(campaign, recipient_id, campaign.message_content)
            
            if success:
                message_log.status = DirectMessageStatus.SENT
                message_log.platform_message_id = f"msg_{campaign_id}_{recipient_id}_{int(datetime.utcnow().timestamp())}"
                
                # Update campaign statistics
                campaign.sent_count += 1
                campaign.success_count += 1
                campaign.last_sent_at = datetime.utcnow()
            else:
                message_log.status = DirectMessageStatus.FAILED
                message_log.error_message = "Platform API error"
                campaign.failure_count += 1
        
        except Exception as e:
            message_log.status = DirectMessageStatus.FAILED
            message_log.error_message = str(e)
            campaign.failure_count += 1
            logger.error(f"Failed to send DM from campaign {campaign_id}: {e}")
        
        self.db.add(message_log)
        await self.db.commit()
        await self.db.refresh(message_log)
        
        return message_log
    
    async def get_dm_stats(self, user_id: int) -> DirectMessageStatsResponse:
        """Get direct message statistics for user"""
        
        # Total campaigns
        total_query = select(func.count()).select_from(DirectMessage).where(DirectMessage.user_id == user_id)
        total_result = await self.db.execute(total_query)
        total_campaigns = total_result.scalar()
        
        # Active campaigns
        active_query = select(func.count()).select_from(DirectMessage).where(
            and_(DirectMessage.user_id == user_id, DirectMessage.is_active == True)
        )
        active_result = await self.db.execute(active_query)
        active_campaigns = active_result.scalar()
        
        # Total sent messages
        sent_query = select(func.sum(DirectMessage.sent_count)).where(DirectMessage.user_id == user_id)
        sent_result = await self.db.execute(sent_query)
        total_sent = sent_result.scalar() or 0
        
        # Success rate
        success_query = select(func.sum(DirectMessage.success_count)).where(DirectMessage.user_id == user_id)
        success_result = await self.db.execute(success_query)
        total_success = success_result.scalar() or 0
        
        success_rate = (total_success / total_sent * 100) if total_sent > 0 else 0
        
        # Recent sends (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_query = select(func.count()).select_from(DirectMessageLog).join(DirectMessage).where(
            and_(
                DirectMessage.user_id == user_id,
                DirectMessageLog.sent_at >= yesterday,
                DirectMessageLog.status == DirectMessageStatus.SENT
            )
        )
        recent_result = await self.db.execute(recent_query)
        recent_sends = recent_result.scalar()
        
        return DirectMessageStatsResponse(
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns,
            total_sent=total_sent,
            success_rate=round(success_rate, 2),
            recent_sends=recent_sends
        )
    
    async def get_dm_logs(
        self, 
        user_id: int, 
        campaign_id: Optional[int] = None,
        status: Optional[DirectMessageStatus] = None,
        page: int = 1, 
        size: int = 20
    ) -> tuple[List[DirectMessageLog], int]:
        """Get direct message sending logs"""
        
        query = select(DirectMessageLog).join(DirectMessage).where(DirectMessage.user_id == user_id)
        
        if campaign_id:
            query = query.where(DirectMessageLog.direct_message_id == campaign_id)
        
        if status:
            query = query.where(DirectMessageLog.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(DirectMessageLog.sent_at)).offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        
        return logs, total
    
    async def process_dm_triggers(self, user_id: int) -> None:
        """Process automated DM triggers (called by background task)"""
        
        # Get active campaigns
        campaigns_query = select(DirectMessage).where(
            and_(DirectMessage.user_id == user_id, DirectMessage.is_active == True)
        )
        campaigns_result = await self.db.execute(campaigns_query)
        campaigns = list(campaigns_result.scalars().all())
        
        for campaign in campaigns:
            try:
                # Check if it's time to send based on triggers
                should_send = await self._check_dm_triggers(campaign)
                
                if should_send:
                    # Get target recipients based on criteria
                    recipients = await self._get_target_recipients(campaign)
                    
                    # Send messages (with rate limiting)
                    for recipient in recipients[:campaign.max_sends_per_day]:
                        await asyncio.sleep(campaign.send_delay_minutes * 60)  # Respect delay
                        await self.send_direct_message(
                            campaign.id, 
                            recipient['id'], 
                            recipient.get('username')
                        )
                        
            except Exception as e:
                logger.error(f"Error processing DM campaign {campaign.id}: {e}")
    
    async def _send_message_to_platform(
        self, 
        campaign: DirectMessage, 
        recipient_id: str, 
        message: str
    ) -> bool:
        """Send message to the actual platform (placeholder implementation)"""
        
        # This is a placeholder - in a real implementation, you would:
        # 1. Get the social account platform API credentials
        # 2. Use the appropriate platform API to send the message
        # 3. Handle platform-specific rate limits and errors
        
        # For now, simulate success/failure
        await asyncio.sleep(0.1)  # Simulate API call
        return True  # Simulate success
    
    async def _check_dm_triggers(self, campaign: DirectMessage) -> bool:
        """Check if DM campaign should trigger based on conditions"""
        
        # This is a placeholder - in a real implementation, you would:
        # 1. Check campaign.target_criteria for conditions
        # 2. Query platform APIs for new followers, interactions, etc.
        # 3. Determine if conditions are met
        
        return False  # Default to not triggering for safety
    
    async def _get_target_recipients(self, campaign: DirectMessage) -> List[Dict[str, str]]:
        """Get list of target recipients based on campaign criteria"""
        
        # This is a placeholder - in a real implementation, you would:
        # 1. Parse campaign.target_criteria
        # 2. Query platform APIs for matching users
        # 3. Return list of recipient IDs and usernames
        
        return []  # Default to empty list for safety