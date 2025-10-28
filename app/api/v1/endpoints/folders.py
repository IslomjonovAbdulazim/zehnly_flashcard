from typing import Optional
from fastapi import APIRouter, Depends, status, Request

from app.core.dependencies_microservice import get_current_user
from app.schemas.folder import FolderCreate, FolderResponse, FolderUpdate, FolderListResponse
from app.services.folder_service import FolderService
from app.repositories.folder_repo import FolderRepository
from app.config.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session

router = APIRouter()

def get_folder_service(db: Session = Depends(get_db)) -> FolderService:
    folder_repo = FolderRepository(db)
    return FolderService(folder_repo)

@router.post("/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderCreate,
    current_user: User = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service)
):
    """Create a new folder"""
    return await folder_service.create_folder(current_user.id, folder_data)

@router.get("/", response_model=FolderListResponse)
async def get_folders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service)
):
    """Get all folders for current user"""
    return await folder_service.get_user_folders(current_user.id, skip=skip, limit=limit)

@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service)
):
    """Get specific folder"""
    folder = await folder_service.get_folder_by_id(current_user.id, folder_id)
    if not folder:
        from app.core.exceptions import APIException
        from app.core.error_codes import ErrorCode
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND
        )
    return folder

@router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: int,
    folder_data: FolderUpdate,
    current_user: User = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service)
):
    """Update folder"""
    return await folder_service.update_folder(current_user.id, folder_id, folder_data)

@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service)
):
    """Delete folder"""
    await folder_service.delete_folder(current_user.id, folder_id)