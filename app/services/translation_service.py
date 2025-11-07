import httpx
from typing import Optional, Dict
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

from app.config.settings import settings
from app.core.constants import SUPPORTED_LANGUAGES

class GoogleTranslationService:
    def __init__(self):
        self.client = self._get_client()
        self.supported_languages = {lang["code"]: lang["name"] for lang in SUPPORTED_LANGUAGES}
        # Frontend to Google Translate language code mapping
        self.frontend_to_google_mapping = {
            "gb": "en",  # Great Britain -> English
            "jp": "ja",  # Japan -> Japanese
            "kr": "ko",  # Korea -> Korean
            "cn": "zh",  # China -> Chinese
            "sa": "ar",  # Saudi Arabia -> Arabic
            "in": "hi",  # India -> Hindi (or could be 'en' for English)
            # Direct mappings (same codes)
            "es": "es", "fr": "fr", "de": "de", "it": "it", 
            "pt": "pt", "ru": "ru", "tr": "tr", "pl": "pl", "nl": "nl"
        }

    def _get_client(self) -> translate.Client:
        """Initialize Google Translate client with service account credentials"""
        credentials_info = {
            "type": "service_account",
            "project_id": settings.GOOGLE_CLOUD_PROJECT,
            "private_key_id": settings.GOOGLE_CLOUD_PRIVATE_KEY_ID,
            "private_key": settings.GOOGLE_CLOUD_PRIVATE_KEY.replace('\\n', '\n'),
            "client_email": settings.GOOGLE_CLOUD_CLIENT_EMAIL,
            "client_id": settings.GOOGLE_CLOUD_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.GOOGLE_CLOUD_CLIENT_EMAIL}"
        }
        
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        return translate.Client(credentials=credentials)

    def _normalize_language_code(self, language_code: str) -> str:
        """Convert frontend language codes to Google Translate codes with fallback to English"""
        if not language_code or not isinstance(language_code, str):
            return "en"  # Fallback to English
            
        # Clean the language code (remove any weird characters)
        clean_code = language_code.lower().strip()
        
        # Map frontend codes to Google codes
        normalized = self.frontend_to_google_mapping.get(clean_code, clean_code)
        
        # Validate the normalized code exists in our supported languages
        if normalized in self.supported_languages:
            return normalized
            
        # If invalid, fallback to English
        return "en"

    async def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of input text
        Returns: language code (e.g., 'en', 'es') or None if detection fails
        """
        try:
            result = self.client.detect_language(text)
            detected_lang = result['language']
            
            # Return any language detected by Google Translate (not restricted to our 15 supported languages)
            return detected_lang
            
        except Exception as e:
            print(f"Language detection error: {str(e)}")
            return None

    async def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> Dict[str, str]:
        """
        Translate text to target language
        Returns: {
            "translated_text": str,
            "detected_language": str,
            "confidence": float
        }
        """
        try:
            # Normalize target language code for Google Translate
            normalized_target = self._normalize_language_code(target_language)
            
            # If source language not provided, detect it
            detected_source = source_language
            if not detected_source:
                detected_source = await self.detect_language(text)
            
            # Don't normalize source language - keep original detected language (like "uz" for Uzbek)
            # This allows Google Translate to work with 100+ languages including Uzbek
                
            # If source and target are the same, no translation needed
            if detected_source == normalized_target:
                return {
                    "translated_text": text,  # Return original text
                    "detected_language": detected_source,
                    "confidence": 1.0
                }
            
            # Perform direct translation from detected language to target
            # Don't go through English - translate directly (e.g., Uzbek → Russian)
            result = self.client.translate(
                text,
                target_language=normalized_target,
                source_language=detected_source  # Use raw detected language (uz, hy, etc.)
            )
            
            return {
                "translated_text": result['translatedText'],
                "detected_language": detected_source,  # Keep original detected language
                "confidence": 0.95  # Google Translate doesn't provide confidence scores
            }
            
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")

    async def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.supported_languages

    def get_language_name(self, language_code: str) -> Optional[str]:
        """Get human-readable language name"""
        return self.supported_languages.get(language_code)

    async def get_word_definition(self, word: str, language: str) -> Optional[str]:
        """
        Get definition of a word (basic implementation)
        Note: This is a simple implementation. You might want to use a dictionary API
        """
        try:
            # For now, we'll translate to English and back to get context
            if language != 'en':
                en_result = await self.translate_text(word, 'en', language)
                definition = f"English equivalent: {en_result['translated_text']}"
                return definition
            return None
        except Exception:
            return None

# Global instance
translation_service = GoogleTranslationService()