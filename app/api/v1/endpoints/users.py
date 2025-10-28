from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.dependencies_microservice import get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.repositories.user_repo import UserRepository
from app.models.user import User

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user with external_id"""
    return await user_service.create_user(user_data)

@router.get("/check", response_model=UserResponse)
async def check_user_registered(
    current_user: User = Depends(get_current_user)
):
    """Check if user is registered (auto-creates if not exists)"""
    return current_user