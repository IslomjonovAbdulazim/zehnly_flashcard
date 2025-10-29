from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies_microservice import get_current_user
from app.schemas.folder import (
    VocabularyFolderCreate, VocabularyFolderResponse, VocabularyFolderUpdate, 
    FolderListResponse, ShareCodeCreate, ShareCodeResponse, JoinFolderRequest
)
from app.repositories.vocabulary_repo import (
    VocabularyFolderRepository, FolderShareCodeRepository, 
    FolderFollowerRepository, VocabularyWordRepository
)
from app.services.vocabulary_service import VocabularyService
from app.config.database import get_db
from app.models.user import User

router = APIRouter()

def get_vocabulary_service(db: Session = Depends(get_db)) -> VocabularyService:
    word_repo = VocabularyWordRepository(db)
    folder_repo = VocabularyFolderRepository(db)
    share_repo = FolderShareCodeRepository(db)
    follower_repo = FolderFollowerRepository(db)
    return VocabularyService(word_repo, folder_repo, share_repo, follower_repo)

@router.post("/", response_model=VocabularyFolderResponse, status_code=status.HTTP_201_CREATED)
async def create_vocabulary_folder(
    folder_data: VocabularyFolderCreate,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Create a new vocabulary folder"""
    folder_dict = folder_data.dict()
    is_premium = folder_dict.pop("is_premium", False)
    
    folder = await vocabulary_service.create_folder(current_user.id, folder_dict, is_premium)
    return folder

@router.get("/", response_model=FolderListResponse)
def get_user_folders(
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Get all folders for current user (owned + followed)"""
    return vocabulary_service.get_user_folders(current_user.id)

@router.get("/{folder_id}", response_model=VocabularyFolderResponse)
async def get_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Get specific folder"""
    folder = await vocabulary_service._get_accessible_folder(current_user.id, folder_id)
    return folder

@router.put("/{folder_id}", response_model=VocabularyFolderResponse)
async def update_folder(
    folder_id: int,
    folder_data: VocabularyFolderUpdate,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Update folder"""
    folder = vocabulary_service.folder_repo.get_user_folder_by_id(current_user.id, folder_id)
    if not folder:
        from app.core.exceptions import APIException
        from app.core.error_codes import ErrorCode
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND
        )
    
    update_data = folder_data.dict(exclude_unset=True)
    return vocabulary_service.folder_repo.update(folder, update_data)

@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Delete folder"""
    folder = vocabulary_service.folder_repo.get_user_folder_by_id(current_user.id, folder_id)
    if not folder:
        from app.core.exceptions import APIException
        from app.core.error_codes import ErrorCode
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND
        )
    
    vocabulary_service.folder_repo.delete(folder_id)

@router.post("/{folder_id}/share", response_model=ShareCodeResponse)
async def create_share_code(
    folder_id: int,
    share_data: ShareCodeCreate,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Create share code for folder"""
    return await vocabulary_service.create_share_code(current_user.id, folder_id, share_data.duration)

@router.delete("/{folder_id}/share", status_code=status.HTTP_204_NO_CONTENT)
async def delete_share_code(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Delete share code for folder"""
    await vocabulary_service.delete_share_code(current_user.id, folder_id)

@router.post("/join", response_model=VocabularyFolderResponse)
async def join_folder(
    join_data: JoinFolderRequest,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Join folder using share code"""
    is_premium = join_data.dict().get("is_premium", False)
    return await vocabulary_service.join_folder_by_code(current_user.id, join_data.share_code, is_premium)

@router.delete("/{folder_id}/unfollow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Unfollow a folder"""
    await vocabulary_service.unfollow_folder(current_user.id, folder_id)