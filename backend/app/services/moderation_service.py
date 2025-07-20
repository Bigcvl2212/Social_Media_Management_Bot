"""
Community moderation service for comments, live streams, and groups
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import re
from loguru import logger

from app.models.automation import ModerationRule, ModerationLog, ModerationAction
from app.models.social_account import SocialAccount
from app.schemas.automation import ModerationRuleCreate, ModerationRuleUpdate


class ModerationService:
    """Service for community moderation tools"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_moderation_rule(
        self, 
        rule_data: ModerationRuleCreate, 
        user_id: int
    ) -> ModerationRule:
        """Create a new moderation rule"""
        
        # Verify user owns the social account (if specified)
        if rule_data.social_account_id:
            social_account_query = select(SocialAccount).where(
                and_(SocialAccount.id == rule_data.social_account_id, SocialAccount.user_id == user_id)
            )
            social_account_result = await self.db.execute(social_account_query)
            social_account = social_account_result.scalar_one_or_none()
            
            if not social_account:
                raise ValueError("Social account not found or not owned by user")
        
        rule = ModerationRule(
            **rule_data.model_dump(),
            user_id=user_id
        )
        
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        
        logger.info(f"Created moderation rule {rule.id} for user {user_id}")
        return rule
    
    async def get_moderation_rule(self, rule_id: int, user_id: int) -> Optional[ModerationRule]:
        """Get a moderation rule by ID"""
        
        query = select(ModerationRule).where(
            and_(ModerationRule.id == rule_id, ModerationRule.user_id == user_id)
        ).options(selectinload(ModerationRule.social_account))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_moderation_rules(
        self, 
        user_id: int,
        social_account_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1, 
        size: int = 20
    ) -> tuple[List[ModerationRule], int]:
        """List moderation rules with filters"""
        
        query = select(ModerationRule).where(ModerationRule.user_id == user_id)
        
        # Apply filters
        if social_account_id is not None:
            if social_account_id == 0:  # Global rules
                query = query.where(ModerationRule.social_account_id.is_(None))
            else:
                query = query.where(ModerationRule.social_account_id == social_account_id)
        
        if is_active is not None:
            query = query.where(ModerationRule.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(ModerationRule.severity_level), desc(ModerationRule.created_at))
        query = query.offset((page - 1) * size).limit(size)
        query = query.options(selectinload(ModerationRule.social_account))
        
        result = await self.db.execute(query)
        rules = list(result.scalars().all())
        
        return rules, total
    
    async def update_moderation_rule(
        self, 
        rule_id: int, 
        rule_data: ModerationRuleUpdate, 
        user_id: int
    ) -> Optional[ModerationRule]:
        """Update a moderation rule"""
        
        rule = await self.get_moderation_rule(rule_id, user_id)
        if not rule:
            return None
        
        update_data = rule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        await self.db.commit()
        await self.db.refresh(rule)
        
        logger.info(f"Updated moderation rule {rule_id} for user {user_id}")
        return rule
    
    async def delete_moderation_rule(self, rule_id: int, user_id: int) -> bool:
        """Delete a moderation rule"""
        
        rule = await self.get_moderation_rule(rule_id, user_id)
        if not rule:
            return False
        
        await self.db.delete(rule)
        await self.db.commit()
        
        logger.info(f"Deleted moderation rule {rule_id} for user {user_id}")
        return True
    
    async def moderate_content(
        self,
        user_id: int,
        social_account_id: int,
        content_type: str,  # comment, post, live_stream
        platform_content_id: str,
        content_text: Optional[str],
        author_id: str,
        author_username: Optional[str],
        content_timestamp: datetime
    ) -> Optional[ModerationLog]:
        """Apply moderation rules to content"""
        
        # Get active moderation rules for this user and social account
        rules_query = select(ModerationRule).where(
            and_(
                ModerationRule.user_id == user_id,
                ModerationRule.is_active == True,
                or_(
                    ModerationRule.social_account_id == social_account_id,
                    ModerationRule.social_account_id.is_(None)  # Global rules
                )
            )
        ).order_by(desc(ModerationRule.severity_level))
        
        rules_result = await self.db.execute(rules_query)
        rules = list(rules_result.scalars().all())
        
        # Filter rules by content type
        applicable_rules = []
        for rule in rules:
            if (content_type == "comment" and rule.applies_to_comments) or \
               (content_type == "post" and rule.applies_to_posts) or \
               (content_type == "live_stream" and rule.applies_to_live_streams):
                applicable_rules.append(rule)
        
        # Check each rule
        for rule in applicable_rules:
            if await self._check_rule_conditions(rule, content_text, author_id, author_username):
                # Rule triggered - create log and take action
                moderation_log = ModerationLog(
                    rule_id=rule.id,
                    user_id=user_id,
                    social_account_id=social_account_id,
                    content_type=content_type,
                    platform_content_id=platform_content_id,
                    content_text=content_text,
                    author_id=author_id,
                    author_username=author_username,
                    action_taken=rule.action,
                    reason=f"Triggered rule: {rule.name}",
                    is_automated=True,
                    content_timestamp=content_timestamp
                )
                
                # Update rule statistics
                rule.trigger_count += 1
                rule.last_triggered_at = datetime.utcnow()
                
                self.db.add(moderation_log)
                await self.db.commit()
                await self.db.refresh(moderation_log)
                
                # Execute the moderation action
                await self._execute_moderation_action(rule, moderation_log)
                
                logger.info(f"Applied moderation rule {rule.id} to content {platform_content_id}")
                return moderation_log
        
        return None
    
    async def get_moderation_logs(
        self,
        user_id: int,
        social_account_id: Optional[int] = None,
        content_type: Optional[str] = None,
        action: Optional[ModerationAction] = None,
        is_automated: Optional[bool] = None,
        days: int = 30,
        page: int = 1,
        size: int = 20
    ) -> tuple[List[ModerationLog], int]:
        """Get moderation logs with filters"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        query = select(ModerationLog).where(
            and_(ModerationLog.user_id == user_id, ModerationLog.created_at >= start_date)
        )
        
        # Apply filters
        if social_account_id:
            query = query.where(ModerationLog.social_account_id == social_account_id)
        
        if content_type:
            query = query.where(ModerationLog.content_type == content_type)
        
        if action:
            query = query.where(ModerationLog.action_taken == action)
        
        if is_automated is not None:
            query = query.where(ModerationLog.is_automated == is_automated)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(ModerationLog.created_at)).offset((page - 1) * size).limit(size)
        query = query.options(
            selectinload(ModerationLog.rule),
            selectinload(ModerationLog.social_account)
        )
        
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        
        return logs, total
    
    async def get_moderation_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get moderation statistics"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total actions
        total_query = select(func.count()).select_from(ModerationLog).where(
            and_(ModerationLog.user_id == user_id, ModerationLog.created_at >= start_date)
        )
        total_result = await self.db.execute(total_query)
        total_actions = total_result.scalar()
        
        # Actions by type
        action_query = select(
            ModerationLog.action_taken, 
            func.count()
        ).where(
            and_(ModerationLog.user_id == user_id, ModerationLog.created_at >= start_date)
        ).group_by(ModerationLog.action_taken)
        action_result = await self.db.execute(action_query)
        actions_breakdown = {action.value: count for action, count in action_result.fetchall()}
        
        # Content type breakdown
        content_query = select(
            ModerationLog.content_type, 
            func.count()
        ).where(
            and_(ModerationLog.user_id == user_id, ModerationLog.created_at >= start_date)
        ).group_by(ModerationLog.content_type)
        content_result = await self.db.execute(content_query)
        content_breakdown = {content_type: count for content_type, count in content_result.fetchall()}
        
        # Automated vs manual
        automated_query = select(func.count()).select_from(ModerationLog).where(
            and_(
                ModerationLog.user_id == user_id,
                ModerationLog.created_at >= start_date,
                ModerationLog.is_automated == True
            )
        )
        automated_result = await self.db.execute(automated_query)
        automated_actions = automated_result.scalar()
        
        # Active rules count
        active_rules_query = select(func.count()).select_from(ModerationRule).where(
            and_(ModerationRule.user_id == user_id, ModerationRule.is_active == True)
        )
        active_rules_result = await self.db.execute(active_rules_query)
        active_rules = active_rules_result.scalar()
        
        return {
            "total_actions": total_actions,
            "actions_breakdown": actions_breakdown,
            "content_breakdown": content_breakdown,
            "automated_actions": automated_actions,
            "manual_actions": total_actions - automated_actions,
            "automation_rate": round(automated_actions / total_actions * 100, 2) if total_actions > 0 else 0,
            "active_rules": active_rules
        }
    
    async def create_template_rules(self, user_id: int, social_account_id: Optional[int] = None) -> List[ModerationRule]:
        """Create template moderation rules for common scenarios"""
        
        template_rules = [
            {
                "name": "Spam Filter",
                "description": "Automatically filter obvious spam comments",
                "conditions": {
                    "keywords": ["buy now", "click here", "free money", "limited offer"],
                    "min_matches": 1
                },
                "action": ModerationAction.FILTER_SPAM,
                "severity_level": 2,
                "applies_to_comments": True
            },
            {
                "name": "Toxic Language Filter",
                "description": "Remove comments with toxic language",
                "conditions": {
                    "keywords": ["hate", "stupid", "idiot", "kill", "die"],
                    "min_matches": 1
                },
                "action": ModerationAction.DELETE_CONTENT,
                "severity_level": 3,
                "applies_to_comments": True
            },
            {
                "name": "Promotional Content",
                "description": "Flag promotional content for review",
                "conditions": {
                    "keywords": ["discount", "sale", "promo", "offer", "deal"],
                    "min_matches": 1
                },
                "action": ModerationAction.MANUAL_REVIEW,
                "severity_level": 1,
                "applies_to_comments": True
            }
        ]
        
        created_rules = []
        for template in template_rules:
            rule = ModerationRule(
                user_id=user_id,
                social_account_id=social_account_id,
                name=template["name"],
                description=template["description"],
                conditions=template["conditions"],
                action=template["action"],
                severity_level=template["severity_level"],
                applies_to_comments=template["applies_to_comments"]
            )
            
            self.db.add(rule)
            created_rules.append(rule)
        
        await self.db.commit()
        for rule in created_rules:
            await self.db.refresh(rule)
        
        logger.info(f"Created {len(created_rules)} template moderation rules for user {user_id}")
        return created_rules
    
    async def _check_rule_conditions(
        self, 
        rule: ModerationRule, 
        content_text: Optional[str], 
        author_id: str, 
        author_username: Optional[str]
    ) -> bool:
        """Check if content matches rule conditions"""
        
        if not content_text:
            return False
        
        conditions = rule.conditions
        content_lower = content_text.lower()
        
        # Keyword matching
        if "keywords" in conditions:
            keywords = conditions["keywords"]
            min_matches = conditions.get("min_matches", 1)
            
            matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
            if matches >= min_matches:
                return True
        
        # Regex patterns
        if "patterns" in conditions:
            patterns = conditions["patterns"]
            for pattern in patterns:
                if re.search(pattern, content_text, re.IGNORECASE):
                    return True
        
        # User-specific conditions
        if "blocked_users" in conditions:
            blocked_users = conditions["blocked_users"]
            if author_id in blocked_users or (author_username and author_username in blocked_users):
                return True
        
        # Length conditions
        if "max_length" in conditions:
            if len(content_text) > conditions["max_length"]:
                return True
        
        if "min_length" in conditions:
            if len(content_text) < conditions["min_length"]:
                return True
        
        # URL detection
        if conditions.get("block_urls", False):
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            if re.search(url_pattern, content_text):
                return True
        
        return False
    
    async def _execute_moderation_action(self, rule: ModerationRule, log: ModerationLog) -> None:
        """Execute the moderation action (placeholder implementation)"""
        
        # This is a placeholder - in a real implementation, you would:
        # 1. Use platform APIs to actually perform the action
        # 2. Delete/hide content, ban users, send warnings, etc.
        # 3. Handle platform-specific API calls and rate limits
        
        logger.info(f"Executing moderation action {rule.action.value} for rule {rule.id}")
        
        # For now, just log the action that would be taken
        if rule.action == ModerationAction.DELETE_CONTENT:
            logger.info(f"Would delete content {log.platform_content_id}")
        elif rule.action == ModerationAction.BAN_USER:
            logger.info(f"Would ban user {log.author_id}")
        elif rule.action == ModerationAction.WARN_USER:
            logger.info(f"Would warn user {log.author_id}")
        elif rule.action == ModerationAction.FILTER_SPAM:
            logger.info(f"Would mark content {log.platform_content_id} as spam")
        
        # If there's an auto-response message, it would be sent here
        if rule.auto_response_message:
            logger.info(f"Would send auto-response: {rule.auto_response_message}")


# Import at the bottom to avoid circular imports
from sqlalchemy import or_