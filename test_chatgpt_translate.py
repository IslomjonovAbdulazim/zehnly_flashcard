#!/usr/bin/env python3
"""
Test CURRENT SYSTEM (ChatGPT correction + Google Translate) vs DIRECT Google
Your current flow: User input → ChatGPT validate/correct → Google translate
"""

import asyncio
from dotenv import load_dotenv
from app.services.translation_service import translation_service
from app.services.word_validation_service import word_validation_service

# Load environment variables from .env file
load_dotenv()

async def current_system_flow(text: str, native_lang: str = "uz", target_lang: str = "en"):
    """Simulate your CURRENT system: ChatGPT correction → Google translate"""
    print(f"\n🔄 CURRENT SYSTEM (ChatGPT + Google):")
    print(f"🔤 Input: '{text}'")
    
    try:
        # Step 1: Smart 3-tier validation (your NEW system)
        validation_result = await word_validation_service.validate_and_correct_word_smart(
            text, native_lang, target_lang
        )
        
        corrected_word = validation_result["corrected_word"]
        confidence = validation_result.get("confidence", 0)
        suggestion = validation_result.get("suggestion", "")
        
        detected_lang = validation_result.get("detected_language", "unknown")
        print(f"🤖 Smart Validation: '{corrected_word}' (confidence: {confidence})")
        print(f"🔍 Detected as: {detected_lang}")
        if suggestion:
            print(f"💡 Suggestion: {suggestion}")
        
        # Step 2: Google Translate the corrected word
        translation_result = await translation_service.translate_text(
            corrected_word, target_lang, native_lang
        )
        
        final_translation = translation_result["translated_text"]
        print(f"🔵 Google Translated: '{final_translation}'")
        
        return {
            "original": text,
            "corrected": corrected_word, 
            "translated": final_translation,
            "confidence": confidence
        }
        
    except Exception as e:
        print(f"❌ Current System Error: {e}")
        return None

async def google_translate_simple(text: str):
    """Simple Google Translate"""
    try:
        result = await translation_service.translate_text(
            text=text,
            target_language="en", 
            source_language="uz"
        )
        print(f"🔵 Google: '{result['translated_text']}'")
        return result['translated_text']
        
    except Exception as e:
        print(f"❌ Google Error: {e}")
        return None

async def compare_systems(text: str):
    """Compare CURRENT SYSTEM vs DIRECT Google"""
    print(f"\n" + "="*70)
    print(f"⚔️  SYSTEM COMPARISON FOR: '{text}'")
    print("="*70)
    
    # Get results from both approaches
    direct_google = await google_translate_simple(text)
    current_system = await current_system_flow(text)
    
    # Compare results
    print(f"\n📊 COMPARISON RESULTS:")
    if direct_google and current_system:
        direct_result = direct_google
        system_result = current_system["translated"]
        
        print(f"🔵 Direct Google:    '{direct_result}'")
        print(f"🔄 Current System:   '{system_result}'")
        print(f"🤖 Correction:       '{current_system['original']}' → '{current_system['corrected']}'")
        
        if direct_result.lower().strip() == system_result.lower().strip():
            print(f"✅ SAME RESULT: '{direct_result}'")
        else:
            print(f"⚠️  DIFFERENT RESULTS!")
            print(f"   Which is better? You decide!")
            
    print("-" * 70)

async def main():
    """Test and compare systems"""
    print("=" * 70)
    print("⚔️  CURRENT SYSTEM vs DIRECT GOOGLE TRANSLATE")
    print("=" * 70)
    print("🔄 Current: User → ChatGPT correction → Google translate")
    print("🔵 Direct:  User → Google translate (no correction)")
    print("=" * 70)
    
    # Test words that show 3-tier system
    test_words = [
        "kitob",           # uzbek word (native)
        "book",            # english word (learning) 
        "книга",           # russian word (other)
        "libro",           # spanish word (other)
        "livre",           # french word (other)
        "piyola",          # uzbek tea bowl
        "o'qish",          # uzbek reading
        "hello",           # english hello
        "salom",           # uzbek hello
        "hola"             # spanish hello
    ]
    
    for word in test_words:
        await compare_systems(word)
    
    # Interactive mode
    print("\n" + "=" * 70)
    print("🎮 INTERACTIVE SYSTEM COMPARISON")  
    print("Test any words to see how correction affects translation!")
    print("Type 'quit' to exit")
    print("=" * 70)
    
    while True:
        try:
            user_input = input("\nTest word: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if user_input:
                await compare_systems(user_input)
                
        except KeyboardInterrupt:
            break
    
    print("\n👋 System comparison complete!")

if __name__ == "__main__":
    asyncio.run(main())