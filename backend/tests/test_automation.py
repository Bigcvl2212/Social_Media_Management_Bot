"""
Tests for automation and engagement features
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any

from app.models.automation import (
    DirectMessage, DirectMessageType, DirectMessageStatus,
    CommentManagement, CommentAction,
    ModerationRule, ModerationAction,
    AutomationConfig
)
from app.services.direct_message_service import DirectMessageService
from app.services.comment_management_service import CommentManagementService
from app.services.moderation_service import ModerationService
from app.services.automation_service import AutomationConfigService
from app.schemas.automation import (
    DirectMessageCreate, CommentManagementCreate, ModerationRuleCreate,
    AutomationConfigCreate
)


class TestDirectMessageService:
    """Test direct message automation service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = AsyncMock()
        self.service = DirectMessageService(self.mock_db)
        self.user_id = 1
        self.social_account_id = 1
    
    @pytest.mark.asyncio
    async def test_create_dm_campaign(self):
        """Test creating a DM campaign"""
        # Mock social account validation
        mock_social_account = Mock()
        mock_social_account.user_id = self.user_id
        
        self.mock_db.execute.return_value.scalar_one_or_none.return_value = mock_social_account
        
        dm_data = DirectMessageCreate(
            social_account_id=self.social_account_id,
            message_type=DirectMessageType.WELCOME,
            message_content="Welcome to our community!",
            max_sends_per_day=50
        )
        
        # Mock the creation
        self.mock_db.add = Mock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        campaign = await self.service.create_dm_campaign(dm_data, self.user_id)
        
        # Verify the service calls
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_dm_stats(self):
        """Test getting DM statistics"""
        # Mock database results - need to mock the full chain
        mock_result = Mock()
        mock_result.scalar.side_effect = [5, 3, 100, 95, 10]
        self.mock_db.execute.return_value = mock_result
        
        stats = await self.service.get_dm_stats(self.user_id)
        
        assert stats.total_campaigns == 5
        assert stats.active_campaigns == 3
        assert stats.total_sent == 100
        assert stats.success_rate == 95.0
        assert stats.recent_sends == 10
    
    @pytest.mark.asyncio
    async def test_send_direct_message_rate_limit(self):
        """Test rate limiting for DM sending"""
        # Mock campaign
        mock_campaign = Mock()
        mock_campaign.id = 1
        mock_campaign.is_active = True
        mock_campaign.max_sends_per_day = 24
        mock_campaign.message_content = "Test message"
        
        self.mock_db.execute.return_value.scalar_one_or_none.return_value = mock_campaign
        
        # Mock rate limit check - exceed limit
        self.mock_db.execute.return_value.scalar.return_value = 2  # Already sent 2 this hour
        
        with pytest.raises(ValueError, match="Rate limit exceeded"):
            await self.service.send_direct_message(1, "recipient_123")


class TestCommentManagementService:
    """Test comment management service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = AsyncMock()
        self.service = CommentManagementService(self.mock_db)
        self.user_id = 1
        self.social_account_id = 1
    
    @pytest.mark.asyncio
    async def test_process_comment_positive_sentiment(self):
        """Test processing a positive comment"""
        # Mock social account validation
        mock_social_account = Mock()
        mock_social_account.user_id = self.user_id
        
        self.mock_db.execute.return_value.scalar_one_or_none.return_value = mock_social_account
        
        comment_data = CommentManagementCreate(
            social_account_id=self.social_account_id,
            platform_comment_id="comment_123",
            content_id="post_456",
            comment_text="This is amazing! Love your content!",
            commenter_id="user_789",
            comment_timestamp=datetime.utcnow()
        )
        
        # Mock the creation
        self.mock_db.add = Mock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        comment = await self.service.process_comment(comment_data, self.user_id)
        
        # Verify the service calls
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_comment_spam_detection(self):
        """Test spam detection in comment analysis"""
        spam_text = "Buy now! Click here for free money! Limited offer!"
        
        analysis = await self.service._analyze_comment(spam_text)
        
        assert analysis.spam_score == "high"
        assert analysis.recommended_action == CommentAction.FILTER_SPAM
        assert analysis.confidence_score >= 0.8
    
    @pytest.mark.asyncio
    async def test_analyze_comment_toxicity_detection(self):
        """Test toxicity detection in comment analysis"""
        toxic_text = "You're an idiot and I hate this stupid content"
        
        analysis = await self.service._analyze_comment(toxic_text)
        
        assert analysis.toxicity_score == "high"
        assert analysis.sentiment_score == "negative"
        assert analysis.recommended_action == CommentAction.DELETE
    
    @pytest.mark.asyncio
    async def test_get_comment_stats(self):
        """Test getting comment statistics"""
        # Mock database results for various queries
        self.mock_db.execute.return_value.scalar.side_effect = [50, 5, 40, 30, 10]
        self.mock_db.execute.return_value.fetchall.side_effect = [
            [("positive", 30), ("negative", 10), ("neutral", 10)]  # sentiment breakdown
        ]
        
        stats = await self.service.get_comment_stats(self.user_id, 30)
        
        assert stats["total_comments"] == 50
        assert stats["sentiment_breakdown"]["positive"] == 30
        assert stats["spam_detected"] == 5
        assert stats["auto_processed"] == 40
        assert stats["escalated"] == 30
        assert stats["pending_attention"] == 10


class TestModerationService:
    """Test moderation service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = AsyncMock()
        self.service = ModerationService(self.mock_db)
        self.user_id = 1
        self.social_account_id = 1
    
    @pytest.mark.asyncio
    async def test_create_moderation_rule(self):
        """Test creating a moderation rule"""
        # Mock social account validation
        mock_social_account = Mock()
        mock_social_account.user_id = self.user_id
        
        self.mock_db.execute.return_value.scalar_one_or_none.return_value = mock_social_account
        
        rule_data = ModerationRuleCreate(
            social_account_id=self.social_account_id,
            name="Spam Filter",
            description="Filter obvious spam comments",
            conditions={"keywords": ["buy now", "click here"], "min_matches": 1},
            action=ModerationAction.FILTER_SPAM,
            applies_to_comments=True
        )
        
        # Mock the creation
        self.mock_db.add = Mock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        rule = await self.service.create_moderation_rule(rule_data, self.user_id)
        
        # Verify the service calls
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_rule_conditions_keyword_match(self):
        """Test rule condition checking for keyword matches"""
        rule = Mock()
        rule.conditions = {
            "keywords": ["spam", "buy now"],
            "min_matches": 1
        }
        
        # Test positive match
        result = await self.service._check_rule_conditions(
            rule, "This is spam content", "user123", "username"
        )
        assert result is True
        
        # Test no match
        result = await self.service._check_rule_conditions(
            rule, "This is good content", "user123", "username"
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_rule_conditions_url_blocking(self):
        """Test rule condition checking for URL blocking"""
        rule = Mock()
        rule.conditions = {"block_urls": True}
        
        # Test URL match
        result = await self.service._check_rule_conditions(
            rule, "Check out this link: https://spam.com", "user123", "username"
        )
        assert result is True
        
        # Test no URL
        result = await self.service._check_rule_conditions(
            rule, "This is normal text", "user123", "username"
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_create_template_rules(self):
        """Test creating template moderation rules"""
        # Mock the creation
        self.mock_db.add = Mock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        rules = await self.service.create_template_rules(self.user_id, self.social_account_id)
        
        # Should create 3 template rules
        assert len(rules) == 3
        assert self.mock_db.commit.call_count == 1


class TestAutomationConfigService:
    """Test automation configuration service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = AsyncMock()
        self.service = AutomationConfigService(self.mock_db)
        self.user_id = 1
        self.social_account_id = 1
    
    @pytest.mark.asyncio
    async def test_create_automation_config(self):
        """Test creating automation configuration"""
        # Mock social account validation
        mock_social_account = Mock()
        mock_social_account.user_id = self.user_id
        
        # Mock no existing config
        self.mock_db.execute.return_value.scalar_one_or_none.side_effect = [
            mock_social_account,  # Social account exists
            None  # No existing config
        ]
        
        config_data = AutomationConfigCreate(
            social_account_id=self.social_account_id,
            dm_automation_enabled=True,
            comment_management_enabled=True,
            max_dms_per_hour=20
        )
        
        # Mock the creation
        self.mock_db.add = Mock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        config = await self.service.create_automation_config(config_data, self.user_id)
        
        # Verify the service calls
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_toggle_automation_feature(self):
        """Test toggling automation features"""
        # Mock existing config
        mock_config = Mock()
        mock_config.dm_automation_enabled = False
        
        self.mock_db.execute.return_value.scalar_one_or_none.return_value = mock_config
        self.mock_db.commit = AsyncMock()
        
        success = await self.service.toggle_automation_feature(
            self.user_id, "dm_automation", True, self.social_account_id
        )
        
        assert success is True
        assert mock_config.dm_automation_enabled is True
        self.mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_automation_health_check(self):
        """Test automation health check"""
        # Mock service dependencies
        self.service.dm_service.get_dm_stats = AsyncMock(return_value=Mock(
            total_campaigns=5, success_rate=80.0
        ))
        self.service.comment_service.get_comment_stats = AsyncMock(return_value={
            "pending_attention": 10
        })
        self.service.moderation_service.get_moderation_stats = AsyncMock(return_value={
            "active_rules": 3
        })
        
        # Mock configs
        self.mock_db.execute.return_value.scalars.return_value.all.return_value = [Mock()]
        
        health = await self.service.get_automation_health_check(self.user_id)
        
        assert health["overall_status"] == "healthy"
        assert "direct_messages" in health
        assert "comment_management" in health
        assert "moderation" in health
        assert "configuration" in health


class TestAutomationIntegration:
    """Integration tests for automation features"""
    
    @pytest.mark.asyncio
    async def test_comment_to_moderation_workflow(self):
        """Test workflow from comment processing to moderation"""
        # This would test the full workflow:
        # 1. Comment is received
        # 2. AI analysis is performed
        # 3. Moderation rules are checked
        # 4. Action is taken
        # 5. Log is created
        
        # Mock setup for integration test
        mock_db = AsyncMock()
        
        comment_service = CommentManagementService(mock_db)
        moderation_service = ModerationService(mock_db)
        
        # Test the workflow...
        # This would be a more complex integration test
        pass
    
    @pytest.mark.asyncio
    async def test_dm_automation_with_rate_limiting(self):
        """Test DM automation with proper rate limiting"""
        # Test that DM automation respects:
        # 1. Rate limits per hour
        # 2. Business hours configuration
        # 3. User-defined delays
        
        mock_db = AsyncMock()
        dm_service = DirectMessageService(mock_db)
        
        # Test the rate limiting logic...
        pass


# Fixtures for pytest
@pytest.fixture
def sample_dm_campaign():
    """Sample DM campaign for testing"""
    return DirectMessage(
        id=1,
        user_id=1,
        social_account_id=1,
        message_type=DirectMessageType.WELCOME,
        message_content="Welcome to our community!",
        status=DirectMessageStatus.PENDING,
        is_active=True,
        max_sends_per_day=50
    )


@pytest.fixture
def sample_comment():
    """Sample comment for testing"""
    return CommentManagement(
        id=1,
        user_id=1,
        social_account_id=1,
        platform_comment_id="comment_123",
        content_id="post_456",
        comment_text="This is a test comment",
        commenter_id="user_789",
        comment_timestamp=datetime.utcnow(),
        is_processed=False
    )


@pytest.fixture
def sample_moderation_rule():
    """Sample moderation rule for testing"""
    return ModerationRule(
        id=1,
        user_id=1,
        social_account_id=1,
        name="Test Rule",
        conditions={"keywords": ["spam"], "min_matches": 1},
        action=ModerationAction.FILTER_SPAM,
        is_active=True,
        applies_to_comments=True
    )


@pytest.fixture
def sample_automation_config():
    """Sample automation config for testing"""
    return AutomationConfig(
        id=1,
        user_id=1,
        social_account_id=1,
        dm_automation_enabled=True,
        comment_management_enabled=True,
        auto_moderation_enabled=True,
        max_dms_per_hour=10,
        max_responses_per_hour=20
    )