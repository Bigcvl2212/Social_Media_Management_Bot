"""
Internationalization service for backend
Provides multi-language support for API responses and content generation
"""

from typing import Dict, Optional, Any
import json
from pathlib import Path
from enum import Enum
import os


class SupportedLanguage(Enum):
    """Supported languages"""
    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    IT = "it"
    PT = "pt"
    ZH = "zh"
    JA = "ja"
    KO = "ko"
    AR = "ar"


class I18nService:
    """Service for internationalization support"""
    
    def __init__(self):
        self.default_language = SupportedLanguage.EN
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files"""
        base_path = Path(__file__).parent.parent / "locales"
        
        # Create locales directory if it doesn't exist
        base_path.mkdir(exist_ok=True)
        
        # Load translations for each supported language
        for lang in SupportedLanguage:
            lang_file = base_path / f"{lang.value}.json"
            if lang_file.exists():
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang.value] = json.load(f)
                except Exception as e:
                    print(f"Error loading translations for {lang.value}: {e}")
                    self.translations[lang.value] = {}
            else:
                # Create default translation file if it doesn't exist
                self.translations[lang.value] = self._get_default_translations(lang.value)
                self._save_translation_file(lang.value)
    
    def _get_default_translations(self, language: str) -> Dict[str, str]:
        """Get default translations for a language"""
        if language == "en":
            return {
                "errors.validation_failed": "Validation failed",
                "errors.unauthorized": "Unauthorized access",
                "errors.not_found": "Resource not found",
                "errors.server_error": "Internal server error",
                "success.created": "Successfully created",
                "success.updated": "Successfully updated",
                "success.deleted": "Successfully deleted",
                "accessibility.check_completed": "Accessibility check completed",
                "accessibility.excellent_score": "Excellent accessibility score!",
                "accessibility.good_score": "Good accessibility score",
                "accessibility.needs_improvement": "Accessibility needs improvement",
                "accessibility.poor_score": "Poor accessibility score",
                "content.generated": "Content generated successfully",
                "content.alt_text_suggestion": "Consider adding descriptive alt text",
                "content.contrast_warning": "Color contrast may be too low",
                "content.readability_complex": "Text may be too complex for some readers",
                "content.subtitles_missing": "Consider adding subtitles for video content"
            }
        elif language == "es":
            return {
                "errors.validation_failed": "Error de validación",
                "errors.unauthorized": "Acceso no autorizado",
                "errors.not_found": "Recurso no encontrado",
                "errors.server_error": "Error interno del servidor",
                "success.created": "Creado exitosamente",
                "success.updated": "Actualizado exitosamente",
                "success.deleted": "Eliminado exitosamente",
                "accessibility.check_completed": "Verificación de accesibilidad completada",
                "accessibility.excellent_score": "¡Excelente puntuación de accesibilidad!",
                "accessibility.good_score": "Buena puntuación de accesibilidad",
                "accessibility.needs_improvement": "La accesibilidad necesita mejoras",
                "accessibility.poor_score": "Puntuación de accesibilidad pobre",
                "content.generated": "Contenido generado exitosamente",
                "content.alt_text_suggestion": "Considera agregar texto alternativo descriptivo",
                "content.contrast_warning": "El contraste de color puede ser muy bajo",
                "content.readability_complex": "El texto puede ser muy complejo para algunos lectores",
                "content.subtitles_missing": "Considera agregar subtítulos para el contenido de video"
            }
        elif language == "fr":
            return {
                "errors.validation_failed": "Échec de validation",
                "errors.unauthorized": "Accès non autorisé",
                "errors.not_found": "Ressource non trouvée",
                "errors.server_error": "Erreur interne du serveur",
                "success.created": "Créé avec succès",
                "success.updated": "Mis à jour avec succès",
                "success.deleted": "Supprimé avec succès",
                "accessibility.check_completed": "Vérification d'accessibilité terminée",
                "accessibility.excellent_score": "Excellent score d'accessibilité!",
                "accessibility.good_score": "Bon score d'accessibilité",
                "accessibility.needs_improvement": "L'accessibilité a besoin d'améliorations",
                "accessibility.poor_score": "Score d'accessibilité médiocre",
                "content.generated": "Contenu généré avec succès",
                "content.alt_text_suggestion": "Considérez ajouter un texte alternatif descriptif",
                "content.contrast_warning": "Le contraste des couleurs peut être trop faible",
                "content.readability_complex": "Le texte peut être trop complexe pour certains lecteurs",
                "content.subtitles_missing": "Considérez ajouter des sous-titres pour le contenu vidéo"
            }
        else:
            # For other languages, return English as fallback
            return self._get_default_translations("en")
    
    def _save_translation_file(self, language: str):
        """Save translation file"""
        base_path = Path(__file__).parent.parent / "locales"
        lang_file = base_path / f"{language}.json"
        
        try:
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations[language], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving translations for {language}: {e}")
    
    def translate(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Translate a key to the specified language
        
        Args:
            key: Translation key (e.g., 'errors.validation_failed')
            language: Target language code (defaults to English)
            **kwargs: Variables for string formatting
            
        Returns:
            Translated string
        """
        if language is None:
            language = self.default_language.value
        
        # Validate language
        if language not in [lang.value for lang in SupportedLanguage]:
            language = self.default_language.value
        
        # Get translation
        translation = self.translations.get(language, {}).get(key)
        
        # Fallback to English if translation not found
        if translation is None:
            translation = self.translations.get(self.default_language.value, {}).get(key, key)
        
        # Format string with variables
        try:
            return translation.format(**kwargs) if kwargs else translation
        except (KeyError, ValueError):
            return translation
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return [{"code": lang.value, "name": self._get_language_name(lang.value)} for lang in SupportedLanguage]
    
    def _get_language_name(self, code: str) -> str:
        """Get language name from code"""
        names = {
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "pt": "Português",
            "zh": "中文",
            "ja": "日本語",
            "ko": "한국어",
            "ar": "العربية"
        }
        return names.get(code, code)
    
    def is_rtl_language(self, language: str) -> bool:
        """Check if language is right-to-left"""
        rtl_languages = ["ar"]
        return language in rtl_languages
    
    def get_accessibility_level_text(self, level: str, language: Optional[str] = None) -> str:
        """Get localized accessibility level text"""
        key_map = {
            "excellent": "accessibility.excellent_score",
            "good": "accessibility.good_score", 
            "needs_improvement": "accessibility.needs_improvement",
            "poor": "accessibility.poor_score"
        }
        
        key = key_map.get(level, "accessibility.needs_improvement")
        return self.translate(key, language)


# Global instance
i18n_service = I18nService()


def t(key: str, language: Optional[str] = None, **kwargs) -> str:
    """Convenience function for translation"""
    return i18n_service.translate(key, language, **kwargs)


def get_user_language(request_headers: Dict[str, str]) -> str:
    """
    Extract user's preferred language from request headers
    
    Args:
        request_headers: Request headers dictionary
        
    Returns:
        Language code
    """
    # Check Accept-Language header
    accept_language = request_headers.get('accept-language', '')
    
    # Parse Accept-Language header (simplified)
    if accept_language:
        # Take the first language from the header
        preferred = accept_language.split(',')[0].split('-')[0].strip().lower()
        
        # Check if it's supported
        supported_codes = [lang.value for lang in SupportedLanguage]
        if preferred in supported_codes:
            return preferred
    
    # Default to English
    return SupportedLanguage.EN.value