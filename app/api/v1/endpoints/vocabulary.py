from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies_microservice import get_current_user
from app.schemas.vocabulary import (
    VocabularyWordResponse, VocabularyWordListResponse, AddWordRequest
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

@router.post("/{folder_id}/words", response_model=VocabularyWordResponse, status_code=status.HTTP_201_CREATED)
async def add_word_to_folder(
    folder_id: int,
    word_data: AddWordRequest,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Add a new word to vocabulary folder"""
    return await vocabulary_service.add_word_to_folder(
        current_user.id, folder_id, word_data.word
    )

@router.get("/{folder_id}/words", response_model=VocabularyWordListResponse)
async def get_folder_words(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Get all words in a folder"""
    result = await vocabulary_service.get_folder_words(
        current_user.id, folder_id
    )
    
    return VocabularyWordListResponse(
        words=result["words"],
        total=result["total"],
        folder_title=result["folder"].title,
        folder_target_language=result["folder"].target_language
    )

@router.delete("/{folder_id}/words/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word(
    folder_id: int,
    word_id: int,
    current_user: User = Depends(get_current_user),
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    """Delete a word from folder"""
    # Verify access to folder
    await vocabulary_service._get_accessible_folder(current_user.id, folder_id)
    
    # Get and delete word
    word = vocabulary_service.word_repo.get_by_id(word_id)
    if not word or word.folder_id != folder_id:
        from app.core.exceptions import APIException
        from app.core.error_codes import ErrorCode
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND
        )
    
    vocabulary_service.word_repo.delete(word_id)