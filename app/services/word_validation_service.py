import openai
from typing import Optional, Dict
from app.config.settings import settings

class WordValidationService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def validate_and_correct_word_smart(self, word: str, native_language: str, learning_language: str) -> Dict[str, any]:
        """
        3-Tier Smart Validation: Always normalizes to native language
        
        Tier 1: Try as native language
        Tier 2: Try as learning language → translate to native
        Tier 3: Try as any language → translate to native
        
        Returns:
        {
            "is_valid": bool,
            "corrected_word": str,  # Always in native language
            "confidence": float,
            "suggestion": str,
            "detected_language": str  # "native", "learning", or "other"
        }
        """
        if not settings.OPENAI_API_KEY:
            return {
                "is_valid": True,
                "corrected_word": word.strip(),
                "confidence": 0.5,
                "suggestion": None,
                "detected_language": "native"
            }
        
        try:
            cleaned_word = self._clean_input(word)
            
            if not cleaned_word:
                return {
                    "is_valid": False,
                    "corrected_word": word,
                    "confidence": 0.0,
                    "suggestion": "Input appears to be empty or invalid",
                    "detected_language": "native"
                }
            
            # Use the new 3-tier validation
            result = await self._validate_3_tier(cleaned_word, native_language, learning_language)
            return result
                
        except Exception as e:
            print(f"Smart word validation error: {str(e)}")
            return {
                "is_valid": True,
                "corrected_word": self._clean_input(word),
                "confidence": 0.5,
                "suggestion": None,
                "detected_language": "native"
            }

    async def _validate_3_tier(self, word: str, native_language: str, learning_language: str) -> Dict[str, any]:
        """3-Tier validation that always returns native language word"""
        
        # Create smart prompt for 3-tier validation
        prompt = self._create_smart_validation_prompt(word, native_language, learning_language)
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a smart language validator. Always return words in the user's native language. Respond only with JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        result = self._parse_openai_response(response.choices[0].message.content)
        
        return {
            "is_valid": result.get("is_valid", True),
            "corrected_word": result.get("corrected_word", word),
            "confidence": result.get("confidence", 0.8),
            "suggestion": result.get("suggestion"),
            "detected_language": result.get("detected_language", "native")
        }

    async def _validate_for_language(self, word: str, language: str) -> Dict[str, any]:
        """Validate word for a specific language"""
        prompt = self._create_validation_prompt(word, language)
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a word validation assistant. Your job is to check if a word is valid and correct common typos. Respond only with JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=150
        )
        
        result = self._parse_openai_response(response.choices[0].message.content)
        final_word = result.get("corrected_word", word)
        
        return {
            "is_valid": result.get("is_valid", True),
            "corrected_word": final_word,
            "confidence": result.get("confidence", 0.8),
            "suggestion": result.get("suggestion")
        }

    async def validate_and_correct_word(self, word: str, native_language: str = "uz") -> Dict[str, any]:
        """
        Validate and correct a word using OpenAI
        
        Returns:
        {
            "is_valid": bool,
            "corrected_word": str,
            "confidence": float,
            "suggestion": str (if correction was made)
        }
        """
        if not settings.OPENAI_API_KEY:
            # Fallback: return original word if OpenAI not configured
            return {
                "is_valid": True,
                "corrected_word": word.strip(),
                "confidence": 0.5,
                "suggestion": None
            }
        
        try:
            # Clean input - remove extra spaces, numbers, special chars
            cleaned_word = self._clean_input(word)
            
            if not cleaned_word:
                return {
                    "is_valid": False,
                    "corrected_word": word,
                    "confidence": 0.0,
                    "suggestion": "Input appears to be empty or invalid"
                }
            
            # Check if word needs correction
            prompt = self._create_validation_prompt(cleaned_word, native_language)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a word validation assistant. Your job is to check if a word is valid and correct common typos. Respond only with JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            # Parse OpenAI response
            result = self._parse_openai_response(response.choices[0].message.content)
            
            # If OpenAI suggests a correction, use it; otherwise use cleaned word
            final_word = result.get("corrected_word", cleaned_word)
            
            return {
                "is_valid": result.get("is_valid", True),
                "corrected_word": final_word,
                "confidence": result.get("confidence", 0.8),
                "suggestion": result.get("suggestion")
            }
            
        except Exception as e:
            print(f"Word validation error: {str(e)}")
            # Fallback: return cleaned word
            return {
                "is_valid": True,
                "corrected_word": self._clean_input(word),
                "confidence": 0.5,
                "suggestion": None
            }
    
    def _clean_input(self, word: str) -> str:
        """Clean input word - remove numbers, extra spaces, basic cleanup"""
        if not word or not isinstance(word, str):
            return ""
        
        # Remove extra whitespace
        cleaned = word.strip()
        
        # Remove numbers and special characters, keep Unicode letters (all languages)
        import re
        # Keep all Unicode letters + spaces + hyphens + apostrophes
        # This includes Latin, Cyrillic, Arabic, Chinese, etc.
        cleaned = re.sub(r'[^\w\s\'-]', '', cleaned, flags=re.UNICODE)
        
        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Limit length to reasonable word size
        if len(cleaned) > 50:
            cleaned = cleaned[:50]
            
        return cleaned.strip()
    
    def _create_smart_validation_prompt(self, word: str, native_language: str, learning_language: str) -> str:
        """Create 3-tier smart validation prompt"""
        # Language mappings
        language_examples = {
            "uz": "kitob, uy, salom, ona, ota, bola, dost, maktab, ish",
            "en": "book, house, hello, mother, father, child, friend, school, work",
            "ru": "книга, дом, привет, мама, папа, ребёнок, друг, школа, работа",
            "es": "libro, casa, hola, madre, padre, niño, amigo, escuela, trabajo",
            "fr": "livre, maison, salut, mère, père, enfant, ami, école, travail",
            "de": "Buch, Haus, hallo, Mutter, Vater, Kind, Freund, Schule, Arbeit"
        }
        
        native_examples = language_examples.get(native_language, "word, example")
        learning_examples = language_examples.get(learning_language, "word, example")
        
        return f"""
Analyze this input: "{word}"

CONTEXT:
- User's NATIVE language: {native_language.upper()} (examples: {native_examples})
- User's LEARNING language: {learning_language.upper()} (examples: {learning_examples})

TASK: Return the word in {native_language.upper()} language ALWAYS.

3-TIER LOGIC:
1. If word is in {native_language.upper()}: Keep it, fix typos if needed
2. If word is in {learning_language.upper()}: Translate to {native_language.upper()}  
3. If word is in OTHER language (Russian, Spanish, French, etc.): Translate to {native_language.upper()}
4. If word is GIBBERISH/INVALID: Provide random {native_language.upper()} vocabulary word for practice

LANGUAGE RECOGNITION HINTS:
- {native_language.upper()}: {native_examples}
- {learning_language.upper()}: {learning_examples}
- Russian: книга, дом, привет, мама (Cyrillic script)
- Spanish: libro, casa, hola, madre (Latin with ñ, accents)
- French: livre, maison, bonjour, mère (Latin with accents)

CRITICAL: Always normalize to {native_language.upper()} regardless of input language!

Respond in JSON:
{{
    "is_valid": true,
    "corrected_word": "word_in_{native_language}",
    "confidence": 0.0-1.0,
    "detected_language": "native|learning|other",
    "suggestion": "explanation of what you did"
}}

SPECIFIC EXAMPLES:

NATIVE ({native_language.upper()}) words:
- {native_examples.split(', ')[0]} → {{"corrected_word": "{native_examples.split(', ')[0]}", "detected_language": "native", "suggestion": "Valid {native_language.upper()} word"}}

LEARNING ({learning_language.upper()}) words:
- {learning_examples.split(', ')[0]} → {{"corrected_word": "[translate_to_{native_language}]", "detected_language": "learning", "suggestion": "Translated {learning_language.upper()} to {native_language.upper()}"}}

OTHER languages:
- "книга" (Russian) → {{"corrected_word": "[translate_to_{native_language}]", "detected_language": "other", "suggestion": "Translated Russian to {native_language.upper()}"}}
- "libro" (Spanish) → {{"corrected_word": "[translate_to_{native_language}]", "detected_language": "other", "suggestion": "Translated Spanish to {native_language.upper()}"}}
- "livre" (French) → {{"corrected_word": "[translate_to_{native_language}]", "detected_language": "other", "suggestion": "Translated French to {native_language.upper()}"}}

GIBBERISH/INVALID:
- "fnweoifbweof" → {{"corrected_word": "{native_examples.split(', ')[0]}", "detected_language": "other", "confidence": 0.3, "suggestion": "Random {native_language.upper()} word for practice"}}
- "123456" → {{"corrected_word": "{native_examples.split(', ')[1]}", "detected_language": "other", "confidence": 0.3, "suggestion": "Random {native_language.upper()} word for practice"}}
- "!@#$%" → {{"corrected_word": "{native_examples.split(', ')[2]}", "detected_language": "other", "confidence": 0.3, "suggestion": "Random {native_language.upper()} word for practice"}}

BE CAREFUL: 
- "{native_examples.split(', ')[0]}" is {native_language.upper()}, not English!
- "piyola" is {native_language.upper()}, not foreign!
- Don't confuse similar-looking words between languages!
- For gibberish, ALWAYS return a valid {native_language.upper()} word from the examples list!
"""
    
    def _create_validation_prompt(self, word: str, native_language: str) -> str:
        """Create prompt for OpenAI validation"""
        # Language mappings for better prompts
        language_examples = {
            "uz": "kitob, uy, salom, ona, ota, bola, dost, maktab, ish",
            "en": "book, house, hello, mother, father, child, friend, school, work",
            "ru": "книга, дом, привет, мама, папа, ребёнок, друг, школа, работа",
            "es": "libro, casa, hola, madre, padre, niño, amigo, escuela, trabajo",
            "fr": "livre, maison, salut, mère, père, enfant, ami, école, travail",
            "de": "Buch, Haus, hallo, Mutter, Vater, Kind, Freund, Schule, Arbeit"
        }
        
        native_examples = language_examples.get(native_language, "word, example, vocabulary")
        
        return f"""
Extract and correct a single meaningful word from this input: "{word}"

IMPORTANT: User's native language is {native_language.upper()}. Validate for this language context.

Rules:
1. ASSUME NATIVE LANGUAGE: Treat input as {native_language.upper()} unless clearly another language
2. CORRECT TYPOS: Fix spelling errors in the native language
3. TRANSLATE IF FOREIGN: If input is clearly a foreign word, translate it to {native_language.upper()}
4. Common {native_language.upper()} words: {native_examples}
5. If it's a sentence, extract the MOST IMPORTANT single word
6. If it has numbers/symbols, remove them but keep the corrected word
7. Only if clearly gibberish, provide a random {native_language.upper()} vocabulary word

Respond in JSON format:
{{
    "is_valid": true,
    "corrected_word": "single extracted/corrected word",
    "confidence": 0.0-1.0,
    "suggestion": "explanation of what you did"
}}

Examples for {native_language.upper()} native speakers:
- Native word: → {{"is_valid": true, "corrected_word": "native_word", "confidence": 0.9, "suggestion": "Valid {native_language.upper()} word"}}
- Foreign word: → {{"is_valid": true, "corrected_word": "translated_to_{native_language}", "confidence": 0.8, "suggestion": "Translated foreign word to {native_language.upper()}"}}
- Typo: → {{"is_valid": true, "corrected_word": "corrected_word", "confidence": 0.8, "suggestion": "Fixed {native_language.upper()} typo"}}
- Gibberish: → {{"is_valid": true, "corrected_word": "random_{native_language}_word", "confidence": 0.5, "suggestion": "Random {native_language.upper()} word for practice"}}
"""
    
    def _parse_openai_response(self, response_text: str) -> Dict:
        """Parse OpenAI JSON response with fallback"""
        try:
            import json
            
            # Extract JSON from response (sometimes OpenAI adds extra text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"Failed to parse OpenAI response: {e}")
            # Fallback response
            return {
                "is_valid": True,
                "corrected_word": response_text.strip() if response_text else "",
                "confidence": 0.5,
                "suggestion": None
            }

# Global instance
word_validation_service = WordValidationService()