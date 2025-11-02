import io
import base64
import time
from typing import List, Dict, Any
from PIL import Image
from paddleocr import PaddleOCR
from fastapi import HTTPException
import logging
import re

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', use_space_char=True)
        
    async def extract_words_from_image(self, image_data: bytes) -> List[str]:
        """
        Extract words from image using PaddleOCR
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            List of words extracted from image
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Run OCR
            result = self.ocr.ocr(image)
            
            # Extract words from result
            words = []
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]  # Get the text part
                    confidence = line[1][1]  # Get confidence score
                    
                    # Only include words with decent confidence
                    if confidence > 0.5:
                        # Split text into individual words and clean them
                        text_words = self._extract_clean_words(text)
                        words.extend(text_words)
            
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
        
        # Remove special characters but keep letters, numbers, and basic punctuation
        cleaned_text = re.sub(r'[^\w\s\'-]', ' ', text)
        
        # Split into words
        words = cleaned_text.split()
        
        # Filter words
        clean_words = []
        for word in words:
            word = word.strip("'-")  # Remove leading/trailing quotes and hyphens
            
            # Keep words that:
            # - Are at least 2 characters
            # - Contain at least one letter
            if len(word) >= 2 and any(c.isalpha() for c in word):
                clean_words.append(word.lower())
        
        return clean_words


# Global instance
ocr_service = OCRService()