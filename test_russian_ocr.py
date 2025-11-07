#!/usr/bin/env python3

import asyncio
import sys
import os
import time
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.ocr_service import ocr_service


async def test_russian_ocr():
    """Test OCR service with Russian text image"""
    
    image_path = "tests/img.png"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"🔍 Testing Russian OCR with: {image_path}")
    print("=" * 50)
    
    try:
        # Read image file
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        print(f"📁 Image size: {len(image_data)} bytes")
        
        # Extract words using updated OCR service
        start_time = time.time()
        words = await ocr_service.extract_words_from_image(image_data)
        extraction_time = time.time() - start_time
        
        print(f"\n✅ RUSSIAN WORDS EXTRACTED:")
        print("=" * 35)
        print(f"📝 Words: {words}")
        print(f"📊 Count: {len(words)}")
        print(f"⏱️  Extraction time: {extraction_time * 1000:.2f} ms")
        
        print("\n📋 INDIVIDUAL WORDS:")
        print("=" * 25)
        for i, word in enumerate(words, 1):
            print(f"{i:2d}. '{word}'")
        
        # Check for Russian characters
        russian_words = [word for word in words if any(ord(c) >= 1040 and ord(c) <= 1103 for c in word)]
        print(f"\n🇷🇺 Russian words detected: {len(russian_words)}")
        if russian_words:
            print("Russian words:", russian_words)
        
        print(f"\n✅ Russian OCR test completed!")
        
    except Exception as e:
        print(f"❌ OCR test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_russian_ocr())