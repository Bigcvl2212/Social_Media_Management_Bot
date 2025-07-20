"""
Test accessibility and i18n features
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json

from app.services.accessibility_service import AccessibilityService, AccessibilityLevel
from app.services.i18n_service import I18nService, t, get_user_language


class TestAccessibilityService:
    """Test accessibility checking functionality"""
    
    @pytest.fixture
    def accessibility_service(self):
        return AccessibilityService()
    
    @pytest.mark.asyncio
    async def test_text_readability_analysis(self, accessibility_service):
        """Test text readability analysis"""
        simple_text = "This is a simple text. It is easy to read. Short sentences are good."
        complex_text = "This extraordinarily convoluted sentence demonstrates the utilization of unnecessarily complex vocabulary and excessively lengthy sentence structures that may potentially impede comprehension for individuals with varying levels of educational attainment and reading proficiency."
        
        # Test simple text
        score, issues = await accessibility_service._analyze_text_readability(simple_text)
        assert score > 70, "Simple text should have high readability score"
        
        # Test complex text
        score, issues = await accessibility_service._analyze_text_readability(complex_text)
        assert len(issues) > 0, "Complex text should have readability issues"
    
    @pytest.mark.asyncio
    async def test_alt_text_analysis(self, accessibility_service):
        """Test alt text analysis"""
        # Test missing alt text
        score, issues = await accessibility_service._analyze_image_accessibility("test.jpg", "")
        assert score == 0.0, "Missing alt text should result in zero score"
        assert any(issue.type == "alt_text" for issue in issues), "Should have alt text issue"
        
        # Test good alt text
        score, issues = await accessibility_service._analyze_image_accessibility(
            "test.jpg", "A cat sitting on a window sill"
        )
        assert score > 70, "Good alt text should have high score"
        
        # Test poor alt text
        score, issues = await accessibility_service._analyze_image_accessibility(
            "test.jpg", "image of cat"
        )
        assert any("redundant phrase" in issue.message for issue in issues), "Should detect redundant phrases"
    
    def test_contrast_ratio_calculation(self, accessibility_service):
        """Test color contrast ratio calculation"""
        # Black text on white background (perfect contrast)
        ratio = accessibility_service._calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
        assert ratio == 21.0, "Black on white should have contrast ratio of 21"
        
        # Same colors (no contrast)
        ratio = accessibility_service._calculate_contrast_ratio((128, 128, 128), (128, 128, 128))
        assert ratio == 1.0, "Same colors should have contrast ratio of 1"
    
    def test_accessibility_level_determination(self, accessibility_service):
        """Test accessibility level determination"""
        assert accessibility_service._determine_accessibility_level(95) == AccessibilityLevel.EXCELLENT
        assert accessibility_service._determine_accessibility_level(80) == AccessibilityLevel.GOOD
        assert accessibility_service._determine_accessibility_level(60) == AccessibilityLevel.NEEDS_IMPROVEMENT
        assert accessibility_service._determine_accessibility_level(30) == AccessibilityLevel.POOR


class TestI18nService:
    """Test internationalization functionality"""
    
    @pytest.fixture
    def i18n_service(self):
        return I18nService()
    
    def test_translation_basic(self, i18n_service):
        """Test basic translation functionality"""
        # Test English (default)
        text = i18n_service.translate("errors.validation_failed", "en")
        assert text == "Validation failed"
        
        # Test Spanish
        text = i18n_service.translate("errors.validation_failed", "es")
        assert text == "Error de validación"
        
        # Test French
        text = i18n_service.translate("errors.validation_failed", "fr")
        assert text == "Échec de validation"
    
    def test_translation_fallback(self, i18n_service):
        """Test translation fallback to English"""
        # Test unsupported language falls back to English
        text = i18n_service.translate("errors.validation_failed", "unsupported")
        assert text == "Validation failed"
        
        # Test missing key returns the key itself
        text = i18n_service.translate("missing.key", "en")
        assert text == "missing.key"
    
    def test_supported_languages(self, i18n_service):
        """Test supported languages list"""
        languages = i18n_service.get_supported_languages()
        assert len(languages) == 10, "Should support 10 languages"
        
        # Check if English is included
        assert any(lang['code'] == 'en' for lang in languages)
        assert any(lang['code'] == 'es' for lang in languages)
    
    def test_rtl_language_detection(self, i18n_service):
        """Test RTL language detection"""
        assert i18n_service.is_rtl_language("ar") == True
        assert i18n_service.is_rtl_language("en") == False
        assert i18n_service.is_rtl_language("es") == False
    
    def test_accessibility_level_localization(self, i18n_service):
        """Test accessibility level text localization"""
        # Test English
        text = i18n_service.get_accessibility_level_text("excellent", "en")
        assert "Excellent" in text
        
        # Test Spanish
        text = i18n_service.get_accessibility_level_text("excellent", "es")
        assert "Excelente" in text
    
    def test_convenience_function(self):
        """Test convenience translation function"""
        text = t("errors.validation_failed", "en")
        assert text == "Validation failed"
    
    def test_user_language_detection(self):
        """Test user language detection from headers"""
        # Test English
        headers = {"accept-language": "en-US,en;q=0.9"}
        lang = get_user_language(headers)
        assert lang == "en"
        
        # Test Spanish
        headers = {"accept-language": "es-ES,es;q=0.9,en;q=0.8"}
        lang = get_user_language(headers)
        assert lang == "es"
        
        # Test unsupported language fallback
        headers = {"accept-language": "xx-XX,xx;q=0.9"}
        lang = get_user_language(headers)
        assert lang == "en"
        
        # Test no header
        headers = {}
        lang = get_user_language(headers)
        assert lang == "en"


@pytest.mark.asyncio
async def test_integration_accessibility_check():
    """Integration test for accessibility checking"""
    service = AccessibilityService()
    
    content_data = {
        'title': 'Test Post',
        'caption': 'This is a simple test post with good readability.',
        'alt_text': 'A screenshot of the social media management dashboard',
        'subtitles': 'Hello everyone, welcome to our platform demo'
    }
    
    # Test without media files
    score = await service.analyze_content_accessibility(content_data)
    
    assert score.overall_score > 0, "Should have non-zero overall score"
    assert score.text_readability_score > 0, "Should have readability score"
    assert isinstance(score.issues, list), "Issues should be a list"
    assert hasattr(score.level, 'value'), "Level should be an enum"


if __name__ == "__main__":
    # Run basic tests
    print("Running basic tests...")
    
    # Test i18n service
    i18n = I18nService()
    print(f"English: {i18n.translate('errors.validation_failed', 'en')}")
    print(f"Spanish: {i18n.translate('errors.validation_failed', 'es')}")
    print(f"French: {i18n.translate('errors.validation_failed', 'fr')}")
    
    # Test convenience function
    print(f"Convenience: {t('accessibility.excellent_score', 'en')}")
    
    # Test accessibility service
    async def test_accessibility():
        service = AccessibilityService()
        content = {
            'caption': 'This is a test caption for accessibility analysis.',
            'alt_text': 'A beautiful sunset over the mountains'
        }
        score = await service.analyze_content_accessibility(content)
        print(f"Accessibility Score: {score.overall_score:.1f}")
        print(f"Level: {score.level.value}")
        print(f"Issues: {len(score.issues)}")
    
    asyncio.run(test_accessibility())
    print("Basic tests completed successfully!")