from typing import Optional, Any
from pydantic import BaseModel

from app.core.error_codes import ErrorCode

class ErrorResponse(BaseModel):
    error_code: ErrorCode
    message: Optional[str] = None
    details: Optional[Any] = None

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int