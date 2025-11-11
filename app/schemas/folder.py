from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class VocabularyFolderBase(BaseModel):
    title: str
    target_language: str  # Language user wants to learn
    native_language: str = "uz"  # User's native language, defaults to Uzbek

class VocabularyFolderCreate(VocabularyFolderBase):
    is_premium: bool

class VocabularyFolderUpdate(BaseModel):
    title: Optional[str] = None
    target_language: Optional[str] = None
    native_language: Optional[str] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None

class VocabularyFolderResponse(VocabularyFolderBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    word_count: Optional[int] = None  # Number of words in folder
    has_share_code: Optional[bool] = None  # Whether folder has active share code

    class Config:
        orm_mode = True

class ShareCodeResponse(BaseModel):
    share_code: str
    expires_at: datetime
    duration: str

class ShareCodeCreate(BaseModel):
    duration: str  # "10m", "1h", "24h", "72h"

class JoinFolderRequest(BaseModel):
    share_code: str
    is_premium: bool

class FolderListResponse(BaseModel):
    owned_folders: List[VocabularyFolderResponse]
    followed_folders: List[dict]  # Contains folder + join info