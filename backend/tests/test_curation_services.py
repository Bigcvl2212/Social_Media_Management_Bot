"""
Tests for content curation and inspiration board functionality
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.services.content_curation_service import ContentCurationService
from app.services.realtime_trend_monitoring_service import RealTimeTrendMonitoringService
from app.models.curation import (
    CurationCollectionType, CurationItemType, CurationItemStatus
)
from app.models.social_account import SocialPlatform as Platform
from app.schemas.curation import (
    CurationCollectionCreate, CurationItemCreate, TrendWatchCreate,
    TrendingContentRequest, QuickSaveRequest
)


class TestContentCurationService:
    """Test content curation service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def curation_service(self, mock_db):
        return ContentCurationService(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_collection(self, curation_service, mock_db):
        """Test creating a new curation collection"""
        collection_data = CurationCollectionCreate(
            name="My Inspiration Board",
            description="Collection of trending content ideas",
            collection_type=CurationCollectionType.INSPIRATION_BOARD,
            tags=["tech", "viral"]
        )
        
        # Mock database operations
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        collection = await curation_service.create_collection(collection_data, user_id=1)
        
        assert collection is not None
        assert mock_db.add.called
        assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_add_item_to_collection(self, curation_service, mock_db):
        """Test adding an item to a collection"""
        # Mock collection exists
        mock_collection = MagicMock()
        mock_collection.id = 1
        mock_collection.user_id = 1
        
        curation_service.get_collection_by_id = AsyncMock(return_value=mock_collection)
        
        item_data = CurationItemCreate(
            collection_id=1,
            item_type=CurationItemType.CONTENT_IDEA,
            title="Viral TikTok Idea",
            description="Dance challenge with trending audio",
            user_tags=["dance", "challenge"]
        )
        
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        item = await curation_service.add_item_to_collection(item_data, user_id=1)
        
        assert item is not None
        assert mock_db.add.called
        assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_quick_save_content(self, curation_service, mock_db):
        """Test quick save functionality"""
        # Mock collection exists
        mock_collection = MagicMock()
        mock_collection.id = 1
        mock_collection.user_id = 1
        
        curation_service.get_collection_by_id = AsyncMock(return_value=mock_collection)
        curation_service.add_item_to_collection = AsyncMock(return_value=MagicMock(id=123))
        
        request = QuickSaveRequest(
            url="https://www.tiktok.com/@user/video/123",
            collection_id=1,
            title="Trending TikTok",
            notes="Good example of viral content"
        )
        
        result = await curation_service.quick_save_content(request, user_id=1)
        
        assert result["success"] is True
        assert "item_id" in result
        assert result["item_id"] == 123
    
    @pytest.mark.asyncio
    async def test_create_trend_watch(self, curation_service, mock_db):
        """Test creating a trend watch"""
        watch_data = TrendWatchCreate(
            name="AI Technology Watch",
            keywords=["AI", "artificial intelligence", "machine learning"],
            platforms=["tiktok", "instagram"],
            alert_threshold=5000,
            notification_frequency="daily"
        )
        
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        trend_watch = await curation_service.create_trend_watch(watch_data, user_id=1)
        
        assert trend_watch is not None
        assert mock_db.add.called
        assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_get_inspiration_board_summary(self, curation_service, mock_db):
        """Test getting inspiration board summary"""
        # Mock database queries
        mock_db.execute = AsyncMock()
        
        # Mock various query results
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5  # Mock counts
        mock_result.scalars.return_value.all.return_value = []  # Mock lists
        mock_result.fetchall.return_value = []  # Mock group by results
        
        mock_db.execute.return_value = mock_result
        
        summary = await curation_service.get_inspiration_board_summary(user_id=1)
        
        assert summary is not None
        assert hasattr(summary, 'total_collections')
        assert hasattr(summary, 'total_items')
        assert hasattr(summary, 'trending_items')
        assert hasattr(summary, 'recent_additions')
    
    @pytest.mark.asyncio
    async def test_discover_trending_content(self, curation_service):
        """Test trending content discovery"""
        request = TrendingContentRequest(
            platforms=["tiktok", "instagram"],
            keywords=["AI", "tech"],
            time_range="24h"
        )
        
        # Mock the internal method
        curation_service._fetch_platform_trends = AsyncMock(return_value={
            "trends": [{"name": "AI Tech", "volume": 100000}],
            "hashtags": [{"tag": "#ai", "posts": 50000}],
            "viral_content": [{"title": "Viral AI Post", "engagement": 1000000}]
        })
        
        trending_content = await curation_service.discover_trending_content(request)
        
        assert isinstance(trending_content, list)
        assert len(trending_content) == 2  # Two platforms
        for response in trending_content:
            assert "platform" in response.__dict__
            assert "trends" in response.__dict__
            assert "hashtags" in response.__dict__


class TestRealTimeTrendMonitoringService:
    """Test real-time trend monitoring service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def monitoring_service(self, mock_db):
        return RealTimeTrendMonitoringService(mock_db)
    
    @pytest.mark.asyncio
    async def test_monitor_trending_hashtags_realtime(self, monitoring_service):
        """Test real-time hashtag monitoring"""
        platforms = [Platform.TIKTOK, Platform.INSTAGRAM]
        
        result = await monitoring_service.monitor_trending_hashtags_realtime(platforms)
        
        assert "timestamp" in result
        assert "platforms_monitored" in result
        assert "hashtag_data" in result
        assert result["platforms_monitored"] == 2
        assert "tiktok" in result["hashtag_data"]
        assert "instagram" in result["hashtag_data"]
    
    @pytest.mark.asyncio
    async def test_monitor_trending_sounds_realtime(self, monitoring_service):
        """Test real-time sound monitoring"""
        platforms = [Platform.TIKTOK, Platform.INSTAGRAM]
        
        result = await monitoring_service.monitor_trending_sounds_realtime(platforms)
        
        assert "timestamp" in result
        assert "platforms_monitored" in result
        assert "sound_data" in result
        assert result["platforms_monitored"] == 2
    
    @pytest.mark.asyncio
    async def test_detect_viral_content_spikes(self, monitoring_service):
        """Test viral content spike detection"""
        platform = Platform.TIKTOK
        
        viral_spikes = await monitoring_service.detect_viral_content_spikes(platform)
        
        assert isinstance(viral_spikes, list)
        for spike in viral_spikes:
            if "error" not in spike:
                assert "content_id" in spike
                assert "platform" in spike
                assert "current_engagement" in spike
                assert "spike_multiplier" in spike
    
    @pytest.mark.asyncio
    async def test_get_real_time_platform_insights(self, monitoring_service):
        """Test comprehensive platform insights"""
        platform = Platform.INSTAGRAM
        
        insights = await monitoring_service.get_real_time_platform_insights(platform)
        
        if "error" not in insights:
            assert "platform" in insights
            assert "timestamp" in insights
            assert "trending_hashtags" in insights
            assert "trending_topics" in insights
            assert "viral_content_spikes" in insights
            assert "platform_health" in insights
            assert "optimal_posting_window" in insights
    
    @pytest.mark.asyncio
    async def test_create_smart_trend_alerts(self, monitoring_service):
        """Test smart trend alert creation"""
        keywords = ["AI", "technology", "innovation"]
        platforms = [Platform.TIKTOK, Platform.LINKEDIN]
        
        alerts = await monitoring_service.create_smart_trend_alerts(
            user_id=1, keywords=keywords, platforms=platforms
        )
        
        assert isinstance(alerts, list)
        for alert in alerts:
            if "error" not in alert:
                assert "keyword" in alert
                assert "platform" in alert
                assert "trend_score" in alert
                assert "recommended_action" in alert


class TestCurationIntegration:
    """Integration tests for curation functionality"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_curation_workflow(self, mock_db):
        """Test complete curation workflow"""
        service = ContentCurationService(mock_db)
        
        # Mock database operations
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Create collection
        collection_data = CurationCollectionCreate(
            name="Viral Content Ideas",
            collection_type=CurationCollectionType.CONTENT_IDEAS,
            auto_curate_trends=True,
            auto_curate_keywords=["viral", "trending"]
        )
        
        collection = await service.create_collection(collection_data, user_id=1)
        assert collection is not None
        
        # Mock collection exists for subsequent operations
        service.get_collection_by_id = AsyncMock(return_value=MagicMock(id=1, user_id=1))
        
        # Add item to collection
        item_data = CurationItemCreate(
            collection_id=1,
            item_type=CurationItemType.TREND,
            title="AI Technology Trend",
            description="Growing trend in AI content",
            item_data={"volume": 100000, "growth_rate": "+50%"}
        )
        
        item = await service.add_item_to_collection(item_data, user_id=1)
        assert item is not None
        
        # Create trend watch
        watch_data = TrendWatchCreate(
            name="AI Trend Monitor",
            keywords=["AI", "artificial intelligence"],
            platforms=["tiktok", "instagram"],
            auto_save_to_collection_id=1
        )
        
        trend_watch = await service.create_trend_watch(watch_data, user_id=1)
        assert trend_watch is not None
    
    @pytest.mark.asyncio
    async def test_bulk_operations(self, mock_db):
        """Test bulk operations on curation items"""
        service = ContentCurationService(mock_db)
        
        # Mock database queries
        mock_item1 = MagicMock()
        mock_item1.id = 1
        mock_item1.user_tags = ["tag1"]
        
        mock_item2 = MagicMock()
        mock_item2.id = 2
        mock_item2.user_tags = ["tag2"]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_item1, mock_item2]
        
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        
        # Test tag operation
        from app.schemas.curation import BulkItemOperation
        operation = BulkItemOperation(
            item_ids=[1, 2],
            operation="tag",
            tags_to_add=["new_tag"],
            tags_to_remove=["old_tag"]
        )
        
        result = await service.bulk_operation_items(operation, user_id=1)
        
        assert result["success"] is True
        assert result["processed_items"] == 2
        assert result["failed_items"] == 0


# Utility tests
class TestCurationUtilities:
    """Test utility functions and helpers"""
    
    @pytest.mark.asyncio
    async def test_content_metadata_extraction(self):
        """Test content metadata extraction from URLs"""
        service = ContentCurationService(AsyncMock())
        
        tiktok_url = "https://www.tiktok.com/@user/video/123456"
        metadata = await service._extract_content_metadata(tiktok_url)
        
        assert metadata["platform"] == "tiktok"
        assert "title" in metadata
        assert "extracted_at" in metadata
    
    def test_item_type_determination(self):
        """Test item type determination logic"""
        service = ContentCurationService(AsyncMock())
        
        # Test hashtag URL
        hashtag_url = "https://www.tiktok.com/tag/viral"
        extracted_data = {"platform": "tiktok", "content_type": "hashtag"}
        item_type = service._determine_item_type(hashtag_url, extracted_data)
        assert item_type == CurationItemType.HASHTAG
        
        # Test audio URL
        audio_url = "https://www.tiktok.com/music/song-123"
        extracted_data = {"platform": "tiktok", "content_type": "audio"}
        item_type = service._determine_item_type(audio_url, extracted_data)
        assert item_type == CurationItemType.AUDIO_TRACK
        
        # Test general content
        content_url = "https://www.instagram.com/p/abc123"
        extracted_data = {"platform": "instagram", "content_type": "post"}
        item_type = service._determine_item_type(content_url, extracted_data)
        assert item_type == CurationItemType.CONTENT_IDEA


if __name__ == "__main__":
    pytest.main([__file__, "-v"])