from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class FolderBase(BaseModel):
    title: str
    language: str  # ISO language code like "en", "es", "fr", "ar"

class FolderCreate(FolderBase):
    pass

class FolderUpdate(BaseModel):
    title: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None

class FolderResponse(FolderBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class FolderListResponse(BaseModel):
    folders: list[FolderResponse]
    total: int