from typing import List
from fastapi import APIRouter, Depends, status

from app.api.deps import get_user_service
from app.core.dependencies import get_current_user
from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserLogin, Token
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_data)

@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.authenticate_user(login_data)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    return await user_service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.USER_NOT_FOUND
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    return await user_service.update_user(user_id, user_data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    await user_service.delete_user(user_id)