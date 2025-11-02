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
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
    async def extract_words_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract words from image using PaddleOCR with detailed metadata
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with words, confidence scores, and timing data
        """
        try:
            start_time = time.time()
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Run OCR
            ocr_start = time.time()
            result = self.ocr.ocr(image, cls=True)
            ocr_time = time.time() - ocr_start
            
            # Extract words from result
            words = []
            word_details = []
            confidences = []
            
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]  # Get the text part
                    confidence = line[1][1]  # Get confidence score
                    bbox = line[0]  # Bounding box coordinates
                    
                    # Only include words with decent confidence
                    if confidence > 0.3:
                        # Split text into individual words and clean them
                        text_words = self._extract_clean_words(text)
                        
                        for word in text_words:
                            words.append(word)
                            confidences.append(confidence)
                            word_details.append({
                                "word": word,
                                "confidence": round(confidence, 3),
                                "bbox": bbox
                            })
            
            # Remove duplicates while preserving order
            unique_words = list(dict.fromkeys(words))
            
            total_time = time.time() - start_time
            
            return {
                "words": unique_words,
                "word_details": word_details,
                "total_words": len(words),
                "unique_words": len(unique_words),
                "average_confidence": round(sum(confidences) / len(confidences), 3) if confidences else 0,
                "timing": {
                    "total_time_ms": round(total_time * 1000, 2),
                    "ocr_time_ms": round(ocr_time * 1000, 2),
                    "processing_time_ms": round((total_time - ocr_time) * 1000, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
    
    async def extract_words_from_base64(self, base64_image: str) -> Dict[str, Any]:
        """
        Extract words from base64 encoded image
        
        Args:
            base64_image: Base64 encoded image string
            
        Returns:
            Dictionary with words, confidence scores, and timing data
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