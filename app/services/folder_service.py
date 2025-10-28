from typing import List, Optional
from fastapi import status

from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.repositories.folder_repo import FolderRepository
from app.schemas.folder import FolderCreate, FolderUpdate, FolderListResponse
from app.models.folder import Folder

class FolderService:
    def __init__(self, folder_repo: FolderRepository):
        self.folder_repo = folder_repo

    async def create_folder(self, user_id: int, folder_data: FolderCreate) -> Folder:
        """Create a new folder for user"""
        folder_dict = folder_data.dict()
        folder_dict["user_id"] = user_id
        return self.folder_repo.create_folder(folder_dict)

    async def get_user_folders(self, user_id: int, skip: int = 0, limit: int = 100) -> FolderListResponse:
        """Get all folders for user"""
        folders = self.folder_repo.get_by_user_id(user_id, skip=skip, limit=limit)
        total = self.folder_repo.count_user_folders(user_id)
        
        return FolderListResponse(
            folders=folders,
            total=total
        )

    async def get_folders_by_language(self, user_id: int, language: str) -> List[Folder]:
        """Get user folders by language"""
        return self.folder_repo.get_by_user_and_language(user_id, language)

    async def get_folder_by_id(self, user_id: int, folder_id: int) -> Optional[Folder]:
        """Get specific folder for user"""
        return self.folder_repo.get_user_folder_by_id(user_id, folder_id)

    async def update_folder(self, user_id: int, folder_id: int, folder_data: FolderUpdate) -> Folder:
        """Update folder for user"""
        folder = self.folder_repo.get_user_folder_by_id(user_id, folder_id)
        if not folder:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.NOT_FOUND,
                detail="Folder not found"
            )

        update_data = folder_data.dict(exclude_unset=True)
        return self.folder_repo.update_folder(folder, update_data)

    async def delete_folder(self, user_id: int, folder_id: int) -> bool:
        """Delete folder for user"""
        folder = self.folder_repo.get_user_folder_by_id(user_id, folder_id)
        if not folder:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.NOT_FOUND,
                detail="Folder not found"
            )

        return self.folder_repo.delete_folder(folder)