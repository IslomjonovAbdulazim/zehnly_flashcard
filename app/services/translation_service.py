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

    async def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of input text
        Returns: language code (e.g., 'en', 'es') or None if detection fails
        """
        try:
            result = self.client.detect_language(text)
            detected_lang = result['language']
            
            # Only return if it's one of our supported languages
            if detected_lang in self.supported_languages:
                return detected_lang
            return None
            
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
            # If source language not provided, detect it
            if not source_language:
                source_language = await self.detect_language(text)
            
            # Perform translation
            result = self.client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            
            return {
                "translated_text": result['translatedText'],
                "detected_language": result.get('detectedSourceLanguage', source_language),
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