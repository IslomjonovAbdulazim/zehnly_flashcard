from typing import List, Optional
from fastapi import status

from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserStatsResponse
from app.models.user import User

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_data: UserCreate) -> User:
        # Check if user already exists by external_id
        existing_user = self.user_repo.get_by_external_id(user_data.external_id)
        if existing_user:
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.EMAIL_ALREADY_EXISTS,
                detail="User with this external_id already exists"
            )
        
        user_dict = user_data.dict()
        return self.user_repo.create_user(user_dict)

    def get_user_by_external_id(self, external_id: str) -> Optional[User]:
        return self.user_repo.get_by_external_id(external_id)

    async def get_or_create_user(self, external_id: str, user_data: dict = None) -> User:
        """Get existing user or create new one if not exists"""
        user = self.user_repo.get_by_external_id(external_id)
        if not user:
            create_data = {"external_id": external_id}
            if user_data:
                create_data.update(user_data)
            user = self.user_repo.create_user(create_data)
        return user

    async def get_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        return self.user_repo.get_all(skip=skip, limit=limit)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)

    async def update_user(self, user: User, user_data: UserUpdate) -> User:
        update_data = user_data.dict(exclude_unset=True)
        return self.user_repo.update_user(user, update_data)

    async def update_user_by_external_id(self, external_id: str, user_data: UserUpdate) -> User:
        user = self.user_repo.get_by_external_id(external_id)
        if not user:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.USER_NOT_FOUND
            )
        return await self.update_user(user, user_data)

    async def delete_user(self, user_id: int) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.USER_NOT_FOUND
            )
        return self.user_repo.delete(user_id)

    async def get_user_stats(self) -> UserStatsResponse:
        """Get overall user statistics"""
        stats = self.user_repo.get_user_stats()
        return UserStatsResponse(**stats)