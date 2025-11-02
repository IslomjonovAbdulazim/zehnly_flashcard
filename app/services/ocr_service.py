import io
import base64
import time
from typing import List, Dict, Any
from PIL import Image
from fastapi import HTTPException
import logging
import re

# Optional OCR import to prevent server crash when dependencies are missing
try:
    from paddleocr import PaddleOCR
    PADDLE_OCR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  PaddleOCR not available: {e}")
    PADDLE_OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        if not PADDLE_OCR_AVAILABLE:
            print("⚠️  OCR service disabled - PaddleOCR dependencies not available")
            self.ocr = None
        else:
            try:
                self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
                print("✅ OCR service initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize OCR: {e}")
                self.ocr = None
        
    async def extract_words_from_image(self, image_data: bytes) -> List[str]:
        """
        Extract words from image using PaddleOCR
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            List of words extracted from image
        """
        if self.ocr is None:
            raise HTTPException(
                status_code=503, 
                detail="OCR service unavailable - missing system dependencies. Please contact support."
            )
            
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert PIL image to numpy array for PaddleOCR
            import numpy as np
            image_array = np.array(image)
            
            # Run OCR
            result = self.ocr.ocr(image_array)
            
            # Extract words from result - handle new PaddleOCR format
            words = []
            if result and len(result) > 0:
                result_data = result[0]
                if isinstance(result_data, dict) and 'rec_texts' in result_data and 'rec_scores' in result_data:
                    # New format with rec_texts and rec_scores
                    rec_texts = result_data['rec_texts']
                    rec_scores = result_data['rec_scores']
                    
                    for i, text in enumerate(rec_texts):
                        confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                        
                        # Only include words with decent confidence
                        if confidence > 0.3:
                            # Split text into individual words and clean them
                            text_words = self._extract_clean_words(text)
                            words.extend(text_words)
                else:
                    # Old format - fallback
                    for line in result_data:
                        if isinstance(line, list) and len(line) >= 2:
                            text = line[1][0]  # Get the text part
                            confidence = line[1][1]  # Get confidence score
                            
                            # Only include words with decent confidence
                            if confidence > 0.3:
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
        if self.ocr is None:
            raise HTTPException(
                status_code=503, 
                detail="OCR service unavailable - missing system dependencies. Please contact support."
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
        
        # Remove ALL punctuation and special characters, keep only letters and spaces
        cleaned_text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Split into words
        words = cleaned_text.split()
        
        # Filter words
        clean_words = []
        for word in words:
            word = word.strip().lower()
            
            # Keep words that:
            # - Are at least 2 characters
            # - Contain only letters
            if len(word) >= 2 and word.isalpha():
                clean_words.append(word)
        
        return clean_words


# Global instance
ocr_service = OCRService()