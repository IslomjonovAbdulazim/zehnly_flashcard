"""
Language and voice constants for the vocabulary system
"""

SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "it", "name": "Italian"},
    {"code": "zh", "name": "Chinese"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "ru", "name": "Russian"},
    {"code": "ar", "name": "Arabic"},
    {"code": "nl", "name": "Dutch"},
    {"code": "tr", "name": "Turkish"},
    {"code": "pl", "name": "Polish"},
    {"code": "vi", "name": "Vietnamese"}
]

DEFAULT_VOICES = {
    "en": "Betty",      # English
    "es": "Paloma",     # Spanish
    "fr": "Victor",     # French
    "de": "Martina",    # German
    "ja": "Tomoka",     # Japanese
    "ko": "Ji-sung",    # Korean
    "it": "Giulio",     # Italian
    "zh": "Yifei",      # Chinese
    "pt": "Margarida",  # Portuguese
    "ru": "Vladimir",   # Russian
    "ar": "Farah",      # Arabic
    "nl": "Lotte",      # Dutch
    "tr": "Murat",      # Turkish
    "pl": "Tadeusz",    # Polish
    "vi": "Nga"         # Vietnamese
}

# For share code generation: 24² × 8³ = 294,912 combinations
SHARE_CODE_LETTERS = "ABCDEFGHJKMNPQRSTVWXYZ"  # 24 letters (No I, O to avoid confusion)
SHARE_CODE_NUMBERS = "23456789"  # 8 numbers (No 0, 1 to avoid confusion)

# Share code expiration options (in minutes)
SHARE_CODE_DURATIONS = {
    "10m": 10,
    "1h": 60,
    "24h": 1440,
    "72h": 4320
}

# Google Cloud storage paths
AUDIO_STORAGE_FOLDER = "word_pronunciations"

# Narakeet TTS settings
TTS_SPEED = 0.8

# System limits (hard limits for all users)
MAX_WORDS_PER_FOLDER = 50  # System limit
MAX_FOLDERS_SYSTEM = 50    # System limit for all users

# Plan limits (different for free vs premium)
MAX_FOLDERS_FREE = 2       # Plan limit for free users
MAX_FOLDERS_PREMIUM = 50   # Plan limit for premium users (same as system limit)