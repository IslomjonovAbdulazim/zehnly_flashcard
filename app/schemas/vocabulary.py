from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class VocabularyWordBase(BaseModel):
    original_word: str
    translated_word: str
    target_language: str

class VocabularyWordCreate(BaseModel):
    original_word: str  # Just the word user types

class VocabularyWordResponse(VocabularyWordBase):
    id: int
    folder_id: int
    original_language: Optional[str] = None
    audio_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VocabularyWordListResponse(BaseModel):
    words: List[VocabularyWordResponse]
    total: int
    folder_title: str
    folder_target_language: str

class AddWordRequest(BaseModel):
    word: str  # The word user wants to add