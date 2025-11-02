#!/usr/bin/env python3

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.ocr_service import ocr_service


async def test_ocr_with_image():
    """Test OCR service with the test image"""
    
    image_path = "tests/img.png"
    
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
        
        # Run OCR
        result = await ocr_service.extract_words_from_image(image_data)
        
        # Display results
        print("\n🎯 OCR RESULTS:")
        print("=" * 30)
        
        print(f"📝 Words found: {result['words']}")
        print(f"📊 Total words: {result['total_words']}")
        print(f"🔄 Unique words: {result['unique_words']}")
        print(f"⭐ Average confidence: {result['average_confidence']}")
        
        print("\n⏱️  TIMING:")
        print("=" * 20)
        timing = result['timing']
        print(f"🕐 Total time: {timing['total_time_ms']} ms")
        print(f"🔍 OCR time: {timing['ocr_time_ms']} ms")
        print(f"⚙️  Processing time: {timing['processing_time_ms']} ms")
        
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