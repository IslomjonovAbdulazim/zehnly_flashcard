#!/usr/bin/env python3

import asyncio
import sys
import os
import io
import time
from pathlib import Path


async def test_ocr_with_image():
    """Test OCR service with the test image"""
    
    image_path = "tests/img_1.png"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"🔍 Testing OCR with image: {image_path}")
    print("=" * 50)
    
    try:
        # Read image file
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        print(f"📁 Image size: {len(image_data)} bytes")
        
        # Run OCR - debug version
        import numpy as np
        from PIL import Image
        from paddleocr import PaddleOCR
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL image to numpy array for PaddleOCR
        image_array = np.array(image)
        
        # Initialize PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
        # Run OCR
        print("🔍 Running OCR...")
        raw_result = ocr.ocr(image_array)
        print(f"📊 Raw OCR result: {raw_result}")
        
        # Extract words manually - new format
        words = []
        word_details = []
        confidences = []
        start_time = time.time()
        
        if raw_result and len(raw_result) > 0:
            result_data = raw_result[0]
            if 'rec_texts' in result_data and 'rec_scores' in result_data:
                rec_texts = result_data['rec_texts']
                rec_scores = result_data['rec_scores']
                rec_polys = result_data.get('rec_polys', [])
                
                for i, text in enumerate(rec_texts):
                    confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                    bbox = rec_polys[i] if i < len(rec_polys) else []
                    
                    print(f"Text: '{text}', Confidence: {confidence:.3f}")
                    
                    # Only include words with decent confidence
                    if confidence > 0.3:
                        # Split text into individual words
                        text_words = text.lower().split()
                        for word in text_words:
                            if len(word) >= 2 and any(c.isalpha() for c in word):
                                words.append(word)
                                confidences.append(confidence)
                                word_details.append({
                                    "word": word,
                                    "confidence": round(confidence, 3),
                                    "bbox": bbox.tolist() if hasattr(bbox, 'tolist') else bbox
                                })
        
        processing_time = time.time() - start_time
        
        # Remove duplicates while preserving order
        unique_words = list(dict.fromkeys(words))
        
        # Create result manually
        result = {
            'words': unique_words,
            'word_details': word_details,
            'total_words': len(words),
            'unique_words': len(unique_words),
            'average_confidence': round(sum(confidences) / len(confidences), 3) if confidences else 0,
            'processing_time_ms': round(processing_time * 1000, 2)
        }
        
        # Display results
        print("\n🎯 OCR RESULTS:")
        print("=" * 30)
        
        print(f"📝 Words found: {result['words']}")
        print(f"📊 Total words: {result['total_words']}")
        print(f"🔄 Unique words: {result['unique_words']}")
        print(f"⭐ Average confidence: {result['average_confidence']}")
        print(f"⏱️  Processing time: {result['processing_time_ms']} ms")
        
        print("\n📋 WORD DETAILS:")
        print("=" * 25)
        for i, detail in enumerate(result['word_details'], 1):
            print(f"{i}. '{detail['word']}' (confidence: {detail['confidence']})")
        
        print("\n✅ OCR test completed successfully!")
        
    except Exception as e:
        print(f"❌ OCR test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ocr_with_image())