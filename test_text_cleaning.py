#!/usr/bin/env python3

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.ocr_service import OCRService

def test_russian_text_cleaning():
    """Test the text cleaning with Russian text"""
    
    ocr = OCRService()
    
    # Test with the garbled text from your output
    test_text = "MO EHb / MY DAY  p      36. ó  n a .  r .  e y   . o   . Ha  .  n  aBtó6ychyo octaóbky. A éAy Ha pa6óty."
    
    print("🔍 Testing text cleaning with Russian-like text:")
    print("=" * 50)
    print(f"Original text: {test_text}")
    
    words = ocr._extract_clean_words(test_text)
    print(f"\nCleaned words: {words}")
    print(f"Count: {len(words)}")
    
    # Test with proper Russian text
    proper_russian = "Мой день. Я встаю. Иду на работу. Автобусная остановка."
    print(f"\n\nTesting with proper Russian text:")
    print(f"Text: {proper_russian}")
    
    russian_words = ocr._extract_clean_words(proper_russian)
    print(f"Russian words: {russian_words}")
    print(f"Count: {len(russian_words)}")

if __name__ == "__main__":
    test_russian_text_cleaning()