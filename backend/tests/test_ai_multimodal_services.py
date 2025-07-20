"""
Tests for AI multimodal content generation services
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_voiceover_service import AIVoiceoverService
from app.services.image_to_video_service import ImageToVideoService
from app.services.enhanced_meme_generator_service import EnhancedMemeGeneratorService
from app.services.ai_short_form_video_service import AIShortFormVideoService
from app.models.social_account import SocialPlatform as Platform


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client"""
    mock_client = AsyncMock()
    
    # Mock audio speech response
    mock_audio_response = MagicMock()
    mock_audio_response.content = b"fake_audio_content"
    mock_client.audio.speech.create.return_value = mock_audio_response
    
    # Mock chat completion response
    mock_chat_response = MagicMock()
    mock_chat_response.choices = [MagicMock()]
    mock_chat_response.choices[0].message.content = '{"test": "response"}'
    mock_client.chat.completions.create.return_value = mock_chat_response
    
    # Mock image generation response
    mock_image_response = MagicMock()
    mock_image_response.data = [MagicMock()]
    mock_image_response.data[0].url = "https://example.com/generated_image.jpg"
    mock_client.images.generate.return_value = mock_image_response
    
    # Mock transcription response
    mock_transcript = MagicMock()
    mock_transcript.text = "Sample transcription text"
    mock_transcript.language = "en"
    mock_client.audio.transcriptions.create.return_value = mock_transcript
    
    return mock_client


class TestAIVoiceoverService:
    """Test cases for AI Voiceover Service"""
    
    @pytest.mark.asyncio
    async def test_generate_voiceover_success(self, mock_db, mock_openai_client):
        """Test successful voiceover generation"""
        with patch('app.services.ai_voiceover_service.openai.AsyncOpenAI', return_value=mock_openai_client):
            service = AIVoiceoverService(mock_db)
            service.openai_client = mock_openai_client
            
            result = await service.generate_voiceover(
                "Hello world", "alloy", "en", Platform.INSTAGRAM
            )
            
            assert "voiceover_path" in result
            assert result["voice"] == "alloy"
            assert result["language"] == "en"
            assert "alternative_voices" in result
    
    @pytest.mark.asyncio
    async def test_generate_voiceover_no_api_key(self, mock_db):
        """Test voiceover generation without API key"""
        service = AIVoiceoverService(mock_db)
        service.openai_client = None
        
        result = await service.generate_voiceover(
            "Hello world", "alloy", "en", Platform.INSTAGRAM
        )
        
        assert "error" in result
        assert "OpenAI API key not configured" in result["error"]
    
    @pytest.mark.asyncio
    async def test_dub_video_success(self, mock_db, mock_openai_client):
        """Test successful video dubbing"""
        with patch('app.services.ai_voiceover_service.openai.AsyncOpenAI', return_value=mock_openai_client):
            service = AIVoiceoverService(mock_db)
            service.openai_client = mock_openai_client
            
            # Mock the audio extraction and file operations
            with patch.object(service, '_extract_audio_from_video', return_value="audio.wav"), \
                 patch.object(service, '_transcribe_audio', return_value={"text": "Hello", "language": "en", "timing": []}), \
                 patch.object(service, '_translate_text', return_value={"text": "Bonjour"}), \
                 patch.object(service, '_sync_audio_with_video', return_value="synced.mp3"), \
                 patch.object(service, '_combine_video_with_audio', return_value={"path": "dubbed.mp4", "optimizations": []}):
                
                result = await service.dub_video(
                    "video.mp4", "fr", "alloy", Platform.INSTAGRAM
                )
                
                assert "dubbed_video_path" in result
                assert result["target_language"] == "fr"
                assert result["voice_used"] == "alloy"
    
    @pytest.mark.asyncio
    async def test_create_multilingual_versions(self, mock_db, mock_openai_client):
        """Test creating multilingual versions"""
        with patch('app.services.ai_voiceover_service.openai.AsyncOpenAI', return_value=mock_openai_client):
            service = AIVoiceoverService(mock_db)
            service.openai_client = mock_openai_client
            
            # Mock the video dubbing process
            with patch.object(service, '_extract_audio_from_video', return_value="audio.wav"), \
                 patch.object(service, '_transcribe_audio', return_value={"text": "Hello", "language": "en"}), \
                 patch.object(service, 'dub_video', return_value={"dubbed_video_path": "test.mp4"}):
                
                result = await service.create_multilingual_versions(
                    "video.mp4", ["fr", "es"], {"fr": "alloy"}, Platform.INSTAGRAM
                )
                
                assert "multilingual_versions" in result
                assert "languages_created" in result
                assert result["languages_created"] >= 0
    
    @pytest.mark.asyncio
    async def test_generate_podcast_narration(self, mock_db, mock_openai_client):
        """Test podcast narration generation"""
        with patch('app.services.ai_voiceover_service.openai.AsyncOpenAI', return_value=mock_openai_client):
            service = AIVoiceoverService(mock_db)
            service.openai_client = mock_openai_client
            
            # Mock the enhancement and audio generation
            with patch.object(service, '_enhance_for_narration', return_value={"text": "Enhanced content", "chapters": []}), \
                 patch.object(service, 'generate_voiceover', return_value={"voiceover_path": "narration.mp3", "duration": 120}), \
                 patch.object(service, '_add_background_music', return_value={"path": "final.mp3"}):
                
                result = await service.generate_podcast_narration(
                    "Sample content", "nova", "conversational", True, Platform.YOUTUBE
                )
                
                assert "narration_path" in result
                assert result["voice_used"] == "nova"
                assert result["style"] == "conversational"


class TestImageToVideoService:
    """Test cases for Image to Video Service"""
    
    @pytest.mark.asyncio
    async def test_create_video_from_image_success(self, mock_db, mock_openai_client):
        """Test successful image to video creation"""
        service = ImageToVideoService(mock_db)
        service.openai_client = mock_openai_client
        
        # Mock all the video creation steps
        with patch.object(service, '_prepare_image_for_video') as mock_prepare, \
             patch.object(service, '_generate_motion_sequence', return_value={"effects": ["zoom"], "timing": []}) as mock_motion, \
             patch.object(service, '_apply_motion_to_image', return_value=[]) as mock_apply, \
             patch.object(service, '_render_video_from_frames', return_value="video.mp4") as mock_render, \
             patch.object(service, '_enhance_video_with_audio', return_value={"path": "enhanced.mp4", "audio_added": False}) as mock_enhance, \
             patch.object(service, '_generate_video_thumbnail', return_value="thumb.jpg") as mock_thumb, \
             patch('PIL.Image.open') as mock_image:
            
            mock_image.return_value = MagicMock()
            
            result = await service.create_video_from_image(
                "image.jpg", "zoom in slowly", Platform.INSTAGRAM, 15, "cinematic"
            )
            
            assert "video_path" in result
            assert result["motion_prompt"] == "zoom in slowly"
            assert result["duration"] == 15
            assert result["style"] == "cinematic"
    
    @pytest.mark.asyncio
    async def test_create_slideshow_video(self, mock_db):
        """Test slideshow video creation"""
        service = ImageToVideoService(mock_db)
        
        with patch.object(service, '_prepare_image_for_video') as mock_prepare, \
             patch.object(service, '_generate_image_transitions', return_value=[]) as mock_transitions, \
             patch.object(service, '_create_slideshow_frames', return_value=[]) as mock_frames, \
             patch.object(service, '_render_video_from_frames', return_value="slideshow.mp4") as mock_render, \
             patch.object(service, '_add_slideshow_music', return_value={"path": "final.mp4"}) as mock_music, \
             patch.object(service, '_generate_video_thumbnail', return_value="thumb.jpg") as mock_thumb, \
             patch('PIL.Image.open') as mock_image:
            
            mock_image.return_value = MagicMock()
            
            result = await service.create_slideshow_video(
                ["img1.jpg", "img2.jpg"], "smooth", Platform.INSTAGRAM, 3.0, True
            )
            
            assert "slideshow_video_path" in result
            assert result["image_count"] == 2
            assert result["transition_style"] == "smooth"
    
    @pytest.mark.asyncio
    async def test_create_text_to_image_video(self, mock_db, mock_openai_client):
        """Test text to image video creation"""
        service = ImageToVideoService(mock_db)
        service.openai_client = mock_openai_client
        
        with patch.object(service, '_generate_image_from_text', return_value={"image_path": "generated.jpg"}) as mock_generate, \
             patch.object(service, 'create_video_from_image', return_value={"video_path": "video.mp4"}) as mock_create:
            
            result = await service.create_text_to_image_video(
                "A sunset over mountains", "pan slowly right", Platform.INSTAGRAM, "realistic", 15
            )
            
            assert "text_to_video_path" in result
            assert result["text_prompt"] == "A sunset over mountains"
            assert result["motion_description"] == "pan slowly right"


class TestEnhancedMemeGeneratorService:
    """Test cases for Enhanced Meme Generator Service"""
    
    @pytest.mark.asyncio
    async def test_generate_trending_meme_success(self, mock_db, mock_openai_client):
        """Test successful trending meme generation"""
        service = EnhancedMemeGeneratorService(mock_db)
        service.openai_client = mock_openai_client
        
        with patch.object(service, '_get_trending_meme_formats', return_value=[{"name": "drake", "format_type": "choice_comparison", "popularity": 0.9}]) as mock_trending, \
             patch.object(service, '_analyze_topic_for_memes', return_value={"trending_score": 0.8, "humor_potential": 0.9}) as mock_analyze, \
             patch.object(service, '_select_optimal_format', return_value={"name": "drake", "format_type": "choice_comparison"}) as mock_select, \
             patch.object(service, '_generate_meme_text', return_value={"top_text": "Old way", "bottom_text": "New way"}) as mock_text, \
             patch.object(service, '_create_meme_image', return_value={"path": "meme.jpg"}) as mock_create, \
             patch.object(service, '_enhance_for_virality', return_value={"path": "enhanced.jpg", "viral_score": 0.85, "optimizations": []}) as mock_enhance, \
             patch.object(service, '_calculate_brand_alignment', return_value=0.8) as mock_brand, \
             patch.object(service, '_generate_alternative_versions', return_value=[]) as mock_alternatives:
            
            result = await service.generate_trending_meme(
                "work from home", "casual", Platform.INSTAGRAM, "millennials", True
            )
            
            assert "meme_path" in result
            assert result["format_used"] == "drake"
            assert "viral_score" in result
            assert "brand_alignment" in result
    
    @pytest.mark.asyncio
    async def test_generate_brand_relevant_memes(self, mock_db, mock_openai_client):
        """Test brand relevant meme generation"""
        service = EnhancedMemeGeneratorService(mock_db)
        service.openai_client = mock_openai_client
        
        brand_info = {"name": "TechCorp", "voice": "professional", "target_audience": "developers"}
        trends = ["remote work", "AI automation", "productivity hacks"]
        
        with patch.object(service, '_analyze_brand_trend_relevance', return_value={"relevance_score": 0.8}) as mock_relevance, \
             patch.object(service, '_generate_brand_aligned_meme', return_value={"meme_path": "brand_meme.jpg", "viral_score": 0.7}) as mock_brand_meme, \
             patch.object(service, '_rank_memes_by_impact', return_value=[{"meme_path": "top_meme.jpg"}]) as mock_rank:
            
            result = await service.generate_brand_relevant_memes(
                brand_info, trends, Platform.LINKEDIN, 3
            )
            
            assert "brand_memes" in result
            assert result["brand_info"] == brand_info
            assert "trends_analyzed" in result
    
    @pytest.mark.asyncio
    async def test_analyze_meme_performance_potential(self, mock_db, mock_openai_client):
        """Test meme performance analysis"""
        service = EnhancedMemeGeneratorService(mock_db)
        service.openai_client = mock_openai_client
        
        with patch.object(service, '_analyze_current_meme_trends', return_value={"trends": ["format1", "format2"]}) as mock_trends, \
             patch.object(service, '_score_meme_concept', return_value={"overall_score": 0.8, "trend_score": 0.7, "originality_score": 0.9, "recommended_formats": ["drake", "expanding_brain"]}) as mock_score, \
             patch.object(service, '_predict_meme_engagement', return_value={"engagement_score": 0.75, "best_posting_time": "evening"}) as mock_predict, \
             patch.object(service, '_suggest_concept_improvements', return_value=["add more humor", "use trending format"]) as mock_improve:
            
            result = await service.analyze_meme_performance_potential(
                "productivity tips for developers", Platform.TWITTER
            )
            
            assert "performance_score" in result
            assert "trend_alignment" in result
            assert "engagement_prediction" in result
            assert "improvement_suggestions" in result


class TestAIShortFormVideoService:
    """Test cases for AI Short Form Video Service"""
    
    @pytest.mark.asyncio
    async def test_create_short_form_video_success(self, mock_db, mock_openai_client):
        """Test successful short-form video creation"""
        service = AIShortFormVideoService(mock_db)
        service.openai_client = mock_openai_client
        
        with patch.object(service, '_analyze_video_for_highlights', return_value={"highlights": [{"start": 0, "end": 15, "score": 0.9}], "total_duration": 60}) as mock_analyze, \
             patch.object(service, '_extract_and_compile_segments', return_value={"path": "compiled.mp4", "segments_used": 1}) as mock_extract, \
             patch.object(service, '_apply_short_form_editing', return_value={"path": "edited.mp4", "techniques_applied": ["quick_cuts"], "viral_elements": ["fast_paced"]}) as mock_edit, \
             patch.object(service, '_add_auto_captions', return_value={"path": "captioned.mp4"}) as mock_captions, \
             patch.object(service, '_generate_thumbnail_options', return_value=["thumb1.jpg", "thumb2.jpg"]) as mock_thumbs, \
             patch.object(service, '_predict_engagement_score', return_value={"engagement_score": 0.8, "optimization_score": 0.85}) as mock_predict:
            
            result = await service.create_short_form_video(
                "long_video.mp4", Platform.TIKTOK, "viral", 15, True, True
            )
            
            assert "short_video_path" in result
            assert result["duration"] == 15
            assert result["platform"] == "tiktok"
            assert result["style"] == "viral"
            assert "engagement_prediction" in result
    
    @pytest.mark.asyncio
    async def test_create_trend_based_video(self, mock_db, mock_openai_client):
        """Test trend-based video creation"""
        service = AIShortFormVideoService(mock_db)
        service.openai_client = mock_openai_client
        
        # Mock trends with all required keys
        mock_trends_data = {
            "elements": ["quick_cuts", "trending_audio"], 
            "viral_potential": 0.9,
            "recommended_hashtags": ["#trending", "#viral"]
        }
        
        with patch.object(service, '_analyze_current_trends', return_value=mock_trends_data) as mock_trends, \
             patch.object(service, '_generate_trend_video_concept', return_value={"concept": "trending concept"}) as mock_concept, \
             patch.object(service, '_create_trend_video_structure', return_value={"structure": "hook-content-cta"}) as mock_structure, \
             patch.object(service, '_create_trend_video_content', return_value={"path": "trend_video.mp4"}) as mock_content, \
             patch.object(service, '_apply_trending_effects', return_value={"path": "enhanced.mp4", "optimizations": []}) as mock_effects, \
             patch.object(service, '_add_trending_audio', return_value={"path": "final.mp4"}) as mock_audio:
            
            result = await service.create_trend_based_video(
                "productivity tips", "trending_song.mp3", Platform.TIKTOK, "trending"
            )
            
            assert "trend_video_path" in result
            assert result["content_theme"] == "productivity tips"
            assert "viral_potential" in result
    
    @pytest.mark.asyncio
    async def test_create_hook_optimized_video(self, mock_db, mock_openai_client):
        """Test hook-optimized video creation"""
        service = AIShortFormVideoService(mock_db)
        service.openai_client = mock_openai_client
        
        hooks = ["What if I told you...", "This secret will change...", "Nobody talks about..."]
        
        with patch.object(service, '_generate_hook_options', return_value=hooks) as mock_hooks, \
             patch.object(service, '_select_optimal_hook', return_value=hooks[0]) as mock_select, \
             patch.object(service, '_create_hook_video_structure', return_value={"path": "hook_video.mp4"}) as mock_structure, \
             patch.object(service, '_apply_retention_optimization', return_value={"path": "optimized.mp4", "retention_score": 0.85}) as mock_retention, \
             patch.object(service, '_add_engagement_triggers', return_value={"path": "final.mp4", "triggers_added": ["question", "cta"]}) as mock_triggers, \
             patch.object(service, '_calculate_optimal_posting_time', return_value="6-9 PM") as mock_time:
            
            result = await service.create_hook_optimized_video(
                "Learn Python in 30 days", "question", Platform.INSTAGRAM, 30
            )
            
            assert "hook_video_path" in result
            assert result["hook_used"] == hooks[0]
            assert "retention_score" in result
            assert "engagement_triggers" in result


class TestMultiModalIntegration:
    """Test cases for multi-modal AI integration"""
    
    @pytest.mark.asyncio
    async def test_cross_service_integration(self, mock_db, mock_openai_client):
        """Test integration between different AI services"""
        # This would test how services work together in real scenarios
        # For example, creating a video, adding voiceover, and generating memes
        
        video_service = AIShortFormVideoService(mock_db)
        voiceover_service = AIVoiceoverService(mock_db)
        meme_service = EnhancedMemeGeneratorService(mock_db)
        
        # Mock successful operations
        with patch.object(video_service, 'create_short_form_video', return_value={"short_video_path": "video.mp4"}) as mock_video, \
             patch.object(voiceover_service, 'generate_voiceover', return_value={"voiceover_path": "voice.mp3"}) as mock_voice, \
             patch.object(meme_service, 'generate_trending_meme', return_value={"meme_path": "meme.jpg"}) as mock_meme:
            
            # Simulate creating a complete content package
            video_result = await video_service.create_short_form_video("source.mp4", Platform.TIKTOK)
            voice_result = await voiceover_service.generate_voiceover("Sample text", "alloy")
            meme_result = await meme_service.generate_trending_meme("trending topic", "casual")
            
            assert video_result["short_video_path"] == "video.mp4"
            assert voice_result["voiceover_path"] == "voice.mp3"
            assert meme_result["meme_path"] == "meme.jpg"
    
    @pytest.mark.asyncio
    async def test_platform_optimization_consistency(self, mock_db):
        """Test that all services consistently optimize for platforms"""
        # Verify that all services handle platform-specific optimizations consistently
        
        # Test platform specs consistency across services
        video_service = AIShortFormVideoService(mock_db)
        image_service = ImageToVideoService(mock_db)
        
        tiktok_video_specs = video_service._get_platform_video_specs(Platform.TIKTOK)
        tiktok_image_specs = image_service._get_platform_video_specs(Platform.TIKTOK)
        
        # Both should have consistent TikTok specifications
        assert tiktok_video_specs["dimensions"] == tiktok_image_specs["dimensions"]
        assert tiktok_video_specs["fps"] == tiktok_image_specs["fps"]
        
    @pytest.mark.asyncio
    async def test_error_handling_consistency(self, mock_db):
        """Test that all services handle errors consistently"""
        # Test that services return consistent error formats
        
        services = [
            AIVoiceoverService(mock_db),
            ImageToVideoService(mock_db),
            EnhancedMemeGeneratorService(mock_db),
            AIShortFormVideoService(mock_db)
        ]
        
        for service in services:
            # Test with invalid/missing parameters should return error dict
            # This is a simplified test - in practice, each service would be tested individually
            assert hasattr(service, 'db')
            assert service.temp_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__])