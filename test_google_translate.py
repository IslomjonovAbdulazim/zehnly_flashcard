#!/usr/bin/env python3
"""
Test Google Translate directly - UZ to EN
No ChatGPT, just raw translation
"""

import asyncio
from dotenv import load_dotenv
from app.services.translation_service import translation_service

# Load environment variables from .env file
load_dotenv()

async def test_translation(text: str):
    """Test direct Google Translate"""
    print(f"\n🔤 Input: '{text}'")
    
    try:
        # Direct Google Translate: Uzbek → English
        result = await translation_service.translate_text(
            text=text,
            target_language="en",
            source_language="uz"
        )
        
        print(f"✅ Translated: '{result['translated_text']}'")
        print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
        print(f"🔍 Detected: {result.get('detected_language', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Test various Uzbek words"""
    print("=" * 50)
    print("🇺🇿 GOOGLE TRANSLATE TEST (UZ → EN)")
    print("=" * 50)
    
    # Test words
    test_words = [
        "kitob",           # book
        "uy",              # house  
        "salom",           # hello
        "o'qish",          # reading (standard apostrophe)
        "oʻqish",          # reading (okina character)
        "ko'cha",          # street
        "koʻcha",          # street (okina)
        "piyola",          # tea bowl
        "non",             # bread
        "suv"              # water
    ]
    
    for word in test_words:
        await test_translation(word)
    
    # Interactive mode
    print("\n" + "=" * 50)
    print("🎮 INTERACTIVE MODE")
    print("Type Uzbek words to translate (or 'quit' to exit)")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nUZ word: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if user_input:
                await test_translation(user_input)
                
        except KeyboardInterrupt:
            break
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())