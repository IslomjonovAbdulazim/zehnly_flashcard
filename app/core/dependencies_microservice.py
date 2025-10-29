from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.repositories.user_repo import UserRepository
from app.models.user import User
from app.services.cache_service import cache_service

def get_user_id_from_request(request: Request) -> str:
    """Extract user_id from request headers (set by main server)"""
    user_id = request.state.user_id
    if not user_id:
        raise APIException(
            status_code=401,
            error_code=ErrorCode.UNAUTHORIZED,
            detail="User ID not provided in request headers"
        )
    return user_id

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Get user from database using external_id from headers"""
    external_id = get_user_id_from_request(request)
    
    # Check if user is already cached in request state
    if hasattr(request.state, 'current_user'):
        return request.state.current_user
    
    # Query database directly - removed Redis caching to avoid serialization overhead
    user_repo = UserRepository(db)
    user = user_repo.get_by_external_id(external_id)
    
    if not user:
        # Create user if not exists (first time from main server)
        user_data = {
            "external_id": external_id,
            "is_active": True
        }
        user = user_repo.create_user(user_data)
    
    # Cache user in request state to avoid multiple DB calls
    request.state.current_user = user
    return user

def get_optional_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User | None:
    """Get user if user_id is provided, otherwise return None"""
    try:
        return get_current_user(request, db)
    except APIException:
        return None