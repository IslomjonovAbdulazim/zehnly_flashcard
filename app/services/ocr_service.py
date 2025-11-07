import io
import base64
import time
from typing import List, Dict, Any
from fastapi import HTTPException
import logging
import re
import os

# OpenAI Vision API import
try:
    from openai import OpenAI
    OCR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  OpenAI not available: {e}")
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        if not OCR_AVAILABLE:
            print("⚠️  OCR service disabled - OpenAI not available")
            self.client = None
        else:
            try:
                # Initialize OpenAI client with API key from environment
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("❌ OPENAI_API_KEY not found in environment variables")
                    self.client = None
                    return
                    
                self.client = OpenAI(api_key=api_key)
                print("✅ OCR service initialized successfully with OpenAI Vision API")
            except Exception as e:
                print(f"❌ Failed to initialize OCR: {e}")
                self.client = None
        
    async def extract_words_from_image(self, image_data: bytes) -> List[str]:
        """
        Extract words from image using OpenAI Vision API
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            List of words extracted from image
        """
        if self.client is None:
            raise HTTPException(
                status_code=503, 
                detail="OCR service unavailable - OpenAI API not initialized. Please contact support."
            )
            
        try:
            # Convert bytes to base64 for OpenAI API
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this image. Return only the words separated by spaces, no formatting or explanations."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Extract text from response
            extracted_text = response.choices[0].message.content.strip()
            
            # Split into words and clean them
            words = self._extract_clean_words(extracted_text)
            
            # Remove duplicates while preserving order
            unique_words = list(dict.fromkeys(words))
            
            return unique_words
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
    
    async def extract_words_from_base64(self, base64_image: str) -> List[str]:
        """
        Extract words from base64 encoded image
        
        Args:
            base64_image: Base64 encoded image string
            
        Returns:
            List of words extracted from image
        """
        if self.client is None:
            raise HTTPException(
                status_code=503, 
                detail="OCR service unavailable - OpenAI API not initialized. Please contact support."
            )
            
        try:
            # Remove data URL prefix if present
            if base64_image.startswith('data:image'):
                base64_image = base64_image.split(',')[1]
            
            # Decode base64 to bytes
            image_data = base64.b64decode(base64_image)
            
            return await self.extract_words_from_image(image_data)
            
        except Exception as e:
            logger.error(f"Base64 OCR extraction failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")
    
    def _extract_clean_words(self, text: str) -> List[str]:
        """Extract and clean individual words from text"""
        if not text:
            return []
        
        # Remove punctuation but keep ALL language characters (Unicode letters)
        # Keep: Latin, Cyrillic, Arabic, Chinese, Japanese, Korean, etc.
        cleaned_text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
        
        # Split into words
        words = cleaned_text.split()
        
        # Filter words
        clean_words = []
        for word in words:
            word = word.strip()
            
            # Keep words that:
            # - Are at least 2 characters
            # - Contain letters from any language (not just English)
            # - Are not pure numbers
            if len(word) >= 2 and not word.isdigit() and any(c.isalpha() for c in word):
                clean_words.append(word)
        
        return clean_words


# Global instance
ocr_service = OCRService()