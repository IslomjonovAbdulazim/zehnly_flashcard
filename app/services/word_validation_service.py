import openai
from typing import Optional, Dict
from app.config.settings import settings

class WordValidationService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def validate_and_correct_word(self, word: str) -> Dict[str, any]:
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
            prompt = self._create_validation_prompt(cleaned_word)
            
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
        
        # Remove numbers and special characters, keep only letters, spaces, hyphens, apostrophes
        import re
        cleaned = re.sub(r'[^a-zA-ZÀ-ÿ\s\'-]', '', cleaned)
        
        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Limit length to reasonable word size
        if len(cleaned) > 50:
            cleaned = cleaned[:50]
            
        return cleaned.strip()
    
    def _create_validation_prompt(self, word: str) -> str:
        """Create prompt for OpenAI validation"""
        return f"""
Check if this word is valid and correct any typos: "{word}"

Rules:
1. If it's a valid word in any language, mark as valid
2. If it's a typo, provide the corrected spelling
3. If it's nonsense or gibberish, mark as invalid
4. If it contains multiple words, keep the main word only

Respond in JSON format:
{{
    "is_valid": true/false,
    "corrected_word": "corrected version or original",
    "confidence": 0.0-1.0,
    "suggestion": "explanation if corrected or null"
}}

Examples:
- "bookk" → {{"is_valid": true, "corrected_word": "book", "confidence": 0.9, "suggestion": "Fixed typo"}}
- "book 2" → {{"is_valid": true, "corrected_word": "book", "confidence": 0.8, "suggestion": "Removed number"}}
- "xyzabc123" → {{"is_valid": false, "corrected_word": "xyzabc123", "confidence": 0.1, "suggestion": "Not a valid word"}}
- "hello" → {{"is_valid": true, "corrected_word": "hello", "confidence": 1.0, "suggestion": null}}
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