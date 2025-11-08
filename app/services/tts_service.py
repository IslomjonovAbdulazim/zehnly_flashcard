import httpx
from typing import Optional

from app.config.settings import settings
from app.core.constants import DEFAULT_VOICES, TTS_SPEED

class NarakeetTTSService:
    def __init__(self):
        self.api_key = settings.NARAKEET
        self.base_url = "https://api.narakeet.com"
        # Frontend to standard language code mapping
        self.frontend_to_standard_mapping = {
            "gb": "en",  # Great Britain -> English
            "jp": "ja",  # Japan -> Japanese
            "kr": "ko",  # Korea -> Korean
            "cn": "zh",  # China -> Chinese
            "sa": "ar",  # Saudi Arabia -> Arabic
            "in": "hi",  # India -> Hindi
            # Direct mappings (same codes)
            "es": "es", "fr": "fr", "de": "de", "it": "it", 
            "pt": "pt", "ru": "ru", "tr": "tr", "pl": "pl", "nl": "nl"
        }

    def _normalize_language_code(self, language_code: str) -> str:
        """Convert frontend language codes to standard codes with fallback to English"""
        if not language_code or not isinstance(language_code, str):
            return "en"  # Fallback to English
            
        # Clean the language code (remove any weird characters)
        clean_code = language_code.lower().strip()
        
        # Map frontend codes to standard codes
        normalized = self.frontend_to_standard_mapping.get(clean_code, clean_code)
        
        # Validate the normalized code exists in our voice mapping
        if normalized in DEFAULT_VOICES:
            return normalized
            
        # If invalid, fallback to English
        return "en"
        
    async def generate_audio(self, text: str, language: str, voice: Optional[str] = None, speed: float = TTS_SPEED) -> bytes:
        """
        Generate audio using Narakeet TTS API
        Returns: audio data as bytes
        """
        # Normalize language code
        normalized_language = self._normalize_language_code(language)
        
        # Use slower speed for Chinese
        if normalized_language == "zh":
            speed = 0.6
        
        if not voice:
            voice = DEFAULT_VOICES.get(normalized_language, "Betty")  # Default to English Betty if language not found
        
        url = f"{self.base_url}/text-to-speech/mp3"
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "text/plain",
            "Accept": "application/octet-stream"
        }
        
        params = {
            "voice": voice,
            "speed": speed
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    params=params,
                    content=text,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    raise Exception(f"Narakeet API error: {response.status_code} - {response.text}")
                    
        except httpx.TimeoutException:
            raise Exception("Narakeet API timeout")
        except Exception as e:
            raise Exception(f"Failed to generate audio: {str(e)}")

    async def is_language_supported(self, language: str) -> bool:
        """Check if language is supported by checking if we have a default voice for it"""
        normalized_language = self._normalize_language_code(language)
        return normalized_language in DEFAULT_VOICES

    def get_voice_for_language(self, language: str) -> str:
        """Get the default voice for a language"""
        normalized_language = self._normalize_language_code(language)
        return DEFAULT_VOICES.get(normalized_language, "Betty")

# Global instance
tts_service = NarakeetTTSService()