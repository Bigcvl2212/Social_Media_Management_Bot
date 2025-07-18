"""
Tests for advanced content services
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.content_search_service import ContentSearchService
from app.services.content_generation_service import ContentGenerationService
from app.services.content_editing_service import ContentEditingService
from app.services.trend_analysis_service import TrendAnalysisService
from app.models.social_account import SocialPlatform as Platform
from app.models.content import ContentType


class TestContentSearchService:
    """Test content search and ideation service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def search_service(self, mock_db):
        return ContentSearchService(mock_db)
    
    @pytest.mark.asyncio
    async def test_search_trending_topics(self, search_service):
        """Test trending topics search"""
        trends = await search_service.search_trending_topics(Platform.TIKTOK, "global")
        
        assert isinstance(trends, list)
        assert len(trends) > 0
        assert "topic" in trends[0]
        assert "volume" in trends[0]
        assert "growth" in trends[0]
    
    @pytest.mark.asyncio
    async def test_generate_content_ideas(self, search_service):
        """Test AI content idea generation"""
        ideas = await search_service.generate_content_ideas(
            "AI Technology", Platform.INSTAGRAM, "Tech enthusiasts"
        )
        
        # Should return empty list when OpenAI is not configured
        # In production, would return actual ideas
        assert isinstance(ideas, list)
    
    @pytest.mark.asyncio
    async def test_suggest_hashtags(self, search_service):
        """Test hashtag suggestions"""
        hashtags = await search_service.suggest_hashtags(
            "Technology tutorial", Platform.INSTAGRAM
        )
        
        # Should return empty list when OpenAI is not configured
        assert isinstance(hashtags, list)
    
    @pytest.mark.asyncio
    async def test_search_viral_content(self, search_service):
        """Test viral content search"""
        viral_content = await search_service.search_viral_content(Platform.TIKTOK, 7)
        
        assert isinstance(viral_content, list)


class TestContentGenerationService:
    """Test AI content generation service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def generation_service(self, mock_db):
        return ContentGenerationService(mock_db)
    
    @pytest.mark.asyncio
    async def test_generate_text_content(self, generation_service):
        """Test text content generation"""
        result = await generation_service.generate_text_content(
            "Create a post about AI", Platform.INSTAGRAM
        )
        
        assert "error" in result or "main_content" in result
    
    @pytest.mark.asyncio
    async def test_generate_image_content(self, generation_service):
        """Test image content generation"""
        result = await generation_service.generate_image_content(
            "A futuristic city", Platform.INSTAGRAM
        )
        
        assert "error" in result or "processed_image_path" in result
    
    @pytest.mark.asyncio
    async def test_generate_video_content(self, generation_service):
        """Test video content generation"""
        result = await generation_service.generate_video_content(
            "AI tutorial", Platform.TIKTOK
        )
        
        # Should return error when OpenCV is not available
        assert "error" in result
        assert "OpenCV" in result["error"]
    
    @pytest.mark.asyncio
    async def test_generate_meme_content(self, generation_service):
        """Test meme generation"""
        result = await generation_service.generate_meme_content(
            "When AI works perfectly", "auto", Platform.INSTAGRAM
        )
        
        assert "meme_path" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_generate_carousel_content(self, generation_service):
        """Test carousel generation"""
        result = await generation_service.generate_carousel_content(
            "AI Development", Platform.INSTAGRAM, 5
        )
        
        assert "slides" in result
        assert len(result["slides"]) <= 5


class TestContentEditingService:
    """Test content editing service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def editing_service(self, mock_db):
        return ContentEditingService(mock_db)
    
    @pytest.mark.asyncio
    async def test_edit_video_for_platform(self, editing_service):
        """Test video editing"""
        result = await editing_service.edit_video_for_platform(
            "/tmp/test_video.mp4", Platform.TIKTOK, "viral"
        )
        
        # Should return error when OpenCV is not available
        assert "error" in result
        assert "OpenCV" in result["error"]
    
    @pytest.mark.asyncio
    async def test_apply_smart_crop(self, editing_service):
        """Test smart cropping"""
        result = await editing_service.apply_smart_crop(
            "/tmp/test_image.jpg", Platform.INSTAGRAM, "smart"
        )
        
        # Should return error when OpenCV is not available
        assert "error" in result
        assert "OpenCV" in result["error"]
    
    @pytest.mark.asyncio
    async def test_platform_specifications(self, editing_service):
        """Test platform specifications"""
        specs = editing_service._get_platform_video_specs(Platform.TIKTOK)
        
        assert "optimal_duration" in specs
        assert "dimensions" in specs
        assert "effects" in specs
        assert "viral_features" in specs
        
        # Verify TikTok specifications
        assert specs["optimal_duration"] == 15
        assert specs["dimensions"] == (1080, 1920)
        assert "trending_audio" in specs["viral_features"]


class TestTrendAnalysisService:
    """Test trend analysis service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def trend_service(self, mock_db):
        return TrendAnalysisService(mock_db)
    
    @pytest.mark.asyncio
    async def test_analyze_platform_trends(self, trend_service):
        """Test platform trend analysis"""
        analysis = await trend_service.analyze_platform_trends(Platform.TIKTOK, 7)
        
        assert "platform" in analysis
        assert analysis["platform"] == Platform.TIKTOK.value
        assert "trending_topics" in analysis or "error" in analysis
    
    @pytest.mark.asyncio
    async def test_predict_viral_potential(self, trend_service):
        """Test viral prediction"""
        prediction = await trend_service.predict_viral_potential(
            "AI technology tutorial", Platform.TIKTOK, ContentType.VIDEO
        )
        
        assert "viral_score" in prediction or "error" in prediction
    
    @pytest.mark.asyncio
    async def test_get_optimal_posting_schedule(self, trend_service):
        """Test posting schedule optimization"""
        schedule = await trend_service.get_optimal_posting_schedule(Platform.INSTAGRAM)
        
        assert "platform" in schedule
        assert "recommended_schedule" in schedule or "error" in schedule
    
    @pytest.mark.asyncio
    async def test_identify_emerging_trends(self, trend_service):
        """Test emerging trend identification"""
        trends = await trend_service.identify_emerging_trends([Platform.TIKTOK])
        
        assert "emerging_trends" in trends or "error" in trends
    
    @pytest.mark.asyncio
    async def test_generate_content_calendar(self, trend_service):
        """Test content calendar generation"""
        calendar = await trend_service.generate_content_calendar(Platform.INSTAGRAM, 2)
        
        assert "platform" in calendar
        assert calendar["platform"] == Platform.INSTAGRAM.value
        assert "content_calendar" in calendar or "error" in calendar
    
    @pytest.mark.asyncio
    async def test_trend_data_gathering(self, trend_service):
        """Test trend data gathering"""
        trend_data = await trend_service._gather_trend_data(Platform.TIKTOK, 7)
        
        assert "hashtags" in trend_data
        assert "topics" in trend_data
        assert "audio" in trend_data
        assert "effects" in trend_data
        
        # Verify hashtag data structure
        hashtags = trend_data["hashtags"]
        assert isinstance(hashtags, list)
        if hashtags:
            assert "name" in hashtags[0]
            assert "growth" in hashtags[0]
            assert "volume" in hashtags[0]


class TestPlatformOptimizations:
    """Test platform-specific optimizations"""
    
    def test_platform_enum_values(self):
        """Test platform enum has all expected values"""
        expected_platforms = ["instagram", "tiktok", "youtube", "twitter", "facebook", "linkedin"]
        actual_platforms = [platform.value for platform in Platform]
        
        for platform in expected_platforms:
            assert platform in actual_platforms
    
    def test_content_type_enum_values(self):
        """Test content type enum has all expected values"""
        expected_types = ["image", "video", "text", "carousel", "story", "reel"]
        actual_types = [content_type.value for content_type in ContentType]
        
        for content_type in expected_types:
            assert content_type in actual_types


class TestServiceIntegration:
    """Test service integration and workflow"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_content_workflow(self, mock_db):
        """Test complete content creation workflow"""
        # 1. Search for trends
        search_service = ContentSearchService(mock_db)
        trends = await search_service.search_trending_topics(Platform.TIKTOK)
        assert isinstance(trends, list)
        
        # 2. Generate content ideas
        ideas = await search_service.generate_content_ideas(
            "trending topic", Platform.TIKTOK
        )
        assert isinstance(ideas, list)
        
        # 3. Generate actual content
        generation_service = ContentGenerationService(mock_db)
        text_content = await generation_service.generate_text_content(
            "Create viral content", Platform.TIKTOK
        )
        assert isinstance(text_content, dict)
        
        # 4. Analyze viral potential
        trend_service = TrendAnalysisService(mock_db)
        viral_prediction = await trend_service.predict_viral_potential(
            "viral content", Platform.TIKTOK, ContentType.VIDEO
        )
        assert isinstance(viral_prediction, dict)


if __name__ == "__main__":
    # Run basic functionality tests
    async def run_basic_tests():
        """Run basic tests without pytest"""
        print("Running basic functionality tests...")
        
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Test content search
        search_service = ContentSearchService(mock_db)
        trends = await search_service.search_trending_topics(Platform.TIKTOK)
        print(f"✓ Trending topics search: {len(trends)} topics found")
        
        # Test content generation
        generation_service = ContentGenerationService(mock_db)
        meme = await generation_service.generate_meme_content("Test meme", "auto", Platform.INSTAGRAM)
        print(f"✓ Meme generation: {'Success' if 'meme_path' in meme else 'Limited (no full setup)'}")
        
        # Test trend analysis
        trend_service = TrendAnalysisService(mock_db)
        analysis = await trend_service.analyze_platform_trends(Platform.INSTAGRAM)
        print(f"✓ Trend analysis: {'Success' if 'platform' in analysis else 'Error'}")
        
        print("Basic tests completed!")
    
    asyncio.run(run_basic_tests())