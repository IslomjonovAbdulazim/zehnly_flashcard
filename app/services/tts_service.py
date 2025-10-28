import httpx
from typing import Optional

from app.config.settings import settings
from app.core.constants import DEFAULT_VOICES, TTS_SPEED

class NarakeetTTSService:
    def __init__(self):
        self.api_key = settings.NARAKEET
        self.base_url = "https://api.narakeet.com"
        
    async def generate_audio(self, text: str, language: str, voice: Optional[str] = None, speed: float = TTS_SPEED) -> bytes:
        """
        Generate audio using Narakeet TTS API
        Returns: audio data as bytes
        """
        if not voice:
            voice = DEFAULT_VOICES.get(language, "Betty")  # Default to English Betty if language not found
        
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
        return language in DEFAULT_VOICES

    def get_voice_for_language(self, language: str) -> str:
        """Get the default voice for a language"""
        return DEFAULT_VOICES.get(language, "Betty")

# Global instance
tts_service = NarakeetTTSService()