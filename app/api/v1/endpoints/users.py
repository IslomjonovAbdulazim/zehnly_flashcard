from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.dependencies_microservice import get_current_user
from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.repositories.user_repo import UserRepository
from app.models.user import User

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

@router.post("/register")
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Register new user or update existing user information"""
    existing_user = user_service.get_user_by_external_id(user_data.external_id)
    
    if existing_user:
        # Update existing user
        updated_user = await user_service.update_user_by_external_id(
            user_data.external_id, 
            user_data
        )
        return {
            "id": updated_user.id,
            "external_id": updated_user.external_id,
            "contact": updated_user.contact,
            "is_active": updated_user.is_active,
            "created_at": updated_user.created_at,
            "updated_at": updated_user.updated_at
        }
    else:
        # Create new user
        new_user = await user_service.create_user(user_data)
        return {
            "id": new_user.id,
            "external_id": new_user.external_id,
            "contact": new_user.contact,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at,
            "updated_at": new_user.updated_at
        }

@router.get("/check/{external_id}", response_model=UserResponse)
def check_user_registered(
    external_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Check if user is registered by external_id"""
    user = user_service.get_user_by_external_id(external_id)
    if not user:
        raise APIException(
            status_code=404,
            error_code=ErrorCode.USER_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information from X-User-Id header"""
    return current_user