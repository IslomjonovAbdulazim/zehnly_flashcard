from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    external_id: str  # MongoDB ObjectId from main server
    contact: Optional[str] = None  # Phone number or email
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    contact: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserStatsResponse(BaseModel):
    total_users: int
    active_users: int