#!/usr/bin/env python3

import asyncio
import sys
import os
import time
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.ocr_service import ocr_service


async def test_with_russian_prompt():
    """Test OCR with explicit Russian language detection"""
    
    image_path = "tests/img.png"  # This should be the image with Russian text
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"🔍 Testing OCR with Russian text detection: {image_path}")
    print("=" * 60)
    
    try:
        # Read image file
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        print(f"📁 Image size: {len(image_data)} bytes")
        
        # Test the current implementation
        print("\n🧪 Testing current OCR implementation...")
        start_time = time.time()
        words = await ocr_service.extract_words_from_image(image_data)
        extraction_time = time.time() - start_time
        
        print(f"✅ Current OCR Results:")
        print(f"📝 Words: {words}")
        print(f"📊 Count: {len(words)}")
        print(f"⏱️  Time: {extraction_time * 1000:.2f} ms")
        
        # Check for Cyrillic characters
        cyrillic_words = []
        for word in words:
            if any(ord(c) >= 1024 and ord(c) <= 1279 for c in word):  # Cyrillic block
                cyrillic_words.append(word)
        
        print(f"\n🇷🇺 Cyrillic words found: {len(cyrillic_words)}")
        if cyrillic_words:
            print(f"Cyrillic words: {cyrillic_words}")
        else:
            print("❌ No Cyrillic characters detected")
            print("This might indicate the image doesn't contain Russian text")
            print("or the OCR is not properly recognizing Cyrillic script")
        
        print("\n📋 All extracted words:")
        for i, word in enumerate(words, 1):
            # Check if word contains Cyrillic
            is_cyrillic = any(ord(c) >= 1024 and ord(c) <= 1279 for c in word)
            flag = "🇷🇺" if is_cyrillic else "🔤"
            print(f"{flag} {i:2d}. '{word}'")
        
    except Exception as e:
        print(f"❌ OCR test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_with_russian_prompt())