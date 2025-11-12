from typing import List, Optional, Dict
from datetime import datetime, timedelta, timezone
from fastapi import status

from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.core.constants import SHARE_CODE_DURATIONS, MAX_WORDS_PER_FOLDER, MAX_FOLDERS_SYSTEM, MAX_FOLDERS_FREE, MAX_FOLDERS_PREMIUM, WORD_VALIDATION_ENABLED, WORD_VALIDATION_MIN_CONFIDENCE
from app.repositories.vocabulary_repo import (
    VocabularyWordRepository, 
    VocabularyFolderRepository,
    FolderShareCodeRepository,
    FolderFollowerRepository
)
from app.services.translation_service import translation_service
from app.services.tts_service import tts_service
from app.services.cloud_storage import cloud_storage
from app.services.share_code_cleanup import share_cleanup
from app.services.word_validation_service import word_validation_service
from app.models.vocabulary import VocabularyWord, FolderShareCode, FolderFollower
from app.models.folder import VocabularyFolder
from app.services.cache_service import cache_service

class VocabularyService:
    def __init__(
        self, 
        word_repo: VocabularyWordRepository,
        folder_repo: VocabularyFolderRepository,
        share_repo: FolderShareCodeRepository,
        follower_repo: FolderFollowerRepository
    ):
        self.word_repo = word_repo
        self.folder_repo = folder_repo
        self.share_repo = share_repo
        self.follower_repo = follower_repo
    
    def _check_folder_limit(self, user_id: int, is_premium: bool) -> None:
        """Check if user can create/join more folders"""
        owned_count = len(self.folder_repo.get_by_user_id(user_id))
        followed_count = len(self.follower_repo.get_by_user_id(user_id))
        total_folders = owned_count + followed_count
        
        # Check system limit first (hard limit for all users)
        if total_folders >= MAX_FOLDERS_SYSTEM:
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.SYSTEM_LIMIT_EXCEEDED,
                detail=f"System folder limit ({MAX_FOLDERS_SYSTEM}) exceeded"
            )
        
        # Check plan limit (can upgrade to bypass this)
        plan_limit = MAX_FOLDERS_PREMIUM if is_premium else MAX_FOLDERS_FREE
        if total_folders >= plan_limit:
            account_type = "premium" if is_premium else "free"
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.PLAN_LIMIT_EXCEEDED,
                detail=f"Plan folder limit ({plan_limit}) exceeded for {account_type} account"
            )

    async def add_word_to_folder(self, user_id: int, folder_id: int, original_word: str) -> VocabularyWord:
        """Add a new word to user's vocabulary folder"""
        
        # Verify user owns the folder or follows it
        folder = await self._get_accessible_folder(user_id, folder_id)
        
        # Check word limit (system limit - applies to all users)
        current_word_count = self.word_repo.count_folder_words(folder_id)
        if current_word_count >= MAX_WORDS_PER_FOLDER:
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.SYSTEM_LIMIT_EXCEEDED,
                detail=f"System word limit ({MAX_WORDS_PER_FOLDER}) exceeded for this folder"
            )
        
        # Step 1: Validate and correct the word using AI (if enabled)
        validated_word = original_word
        validation_suggestion = None
        
        if WORD_VALIDATION_ENABLED:
            try:
                validation_result = await word_validation_service.validate_and_correct_word_smart(
                    original_word, folder.native_language, folder.target_language
                )
                
                # AI now always returns valid=true and provides a useful word
                # No need to reject anymore - AI will extract/correct anything into a useful word
                
                # Smart validation always returns native language word
                validated_word = validation_result["corrected_word"]  # Already in native language
                validation_suggestion = validation_result.get("suggestion")
                detected_language = validation_result.get("detected_language", "native")
                
            except APIException:
                # Re-raise API exceptions (invalid word)
                raise
            except Exception as e:
                # For other errors, log and continue with original word
                print(f"Word validation failed, continuing with original word: {str(e)}")
                validated_word = original_word
        else:
            # If validation disabled, use original word
            validated_word = original_word
        
        # Step 2: Simple translation - native word to target language
        try:
            # validated_word is always in native language (thanks to smart validation)
            translation_result = await translation_service.translate_text(
                validated_word, folder.target_language, folder.native_language
            )
            
            # Simple storage: native word → target translation
            final_original_word = validated_word  # native word
            final_translated_word = translation_result["translated_text"]  # target word
            final_original_language = folder.native_language
                
        except Exception as e:
            raise APIException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                detail=f"Translation failed: {str(e)}"
            )
        
        # Check if word already exists in folder (using final original word)
        existing_word = self.word_repo.get_by_original_word(
            folder_id, final_original_word, folder.target_language
        )
        if existing_word:
            # Return existing word instead of throwing error
            return existing_word
        
        # Generate audio for the translated word - ensure we always have audio
        audio_url, audio_path = await self._ensure_audio_for_word(final_translated_word, folder.target_language)

        # Create vocabulary word record
        word_data = {
            "folder_id": folder_id,
            "original_word": final_original_word,  # Either validated word or Uzbek translation
            "original_language": final_original_language,  # Either detected lang or "uz"
            "translated_word": final_translated_word,  # Either translation or validated word
            "target_language": folder.target_language,
            "audio_url": audio_url,
            "audio_path": audio_path
        }
        
        return self.word_repo.create(word_data)
    
    async def create_folder(self, user_id: int, folder_data: dict, is_premium: bool) -> VocabularyFolder:
        """Create a new vocabulary folder"""
        
        # Check folder limit
        self._check_folder_limit(user_id, is_premium)
        
        # Add user_id to folder data
        folder_data["user_id"] = user_id
        
        return self.folder_repo.create(folder_data)

    async def _ensure_audio_for_word(self, word: str, target_language: str) -> tuple[str, str]:
        """Ensure audio exists for a word, generate if needed. Returns (audio_url, audio_path)"""
        try:
            # Check if audio already exists
            audio_path = cloud_storage.generate_audio_path(word, target_language)
            
            if cloud_storage.file_exists(audio_path):
                # Use existing audio
                audio_url = cloud_storage.get_public_url(audio_path)
                return audio_url, audio_path
            
            # Generate new audio
            audio_data = await tts_service.generate_audio(word, target_language)
            audio_path, audio_url = cloud_storage.upload_audio_file(
                audio_data, word, target_language
            )
            return audio_url, audio_path
            
        except Exception as e:
            print(f"Audio generation failed for '{word}': {str(e)}")
            return None, None

    async def get_folder_words(self, user_id: int, folder_id: int) -> Dict:
        """Get all words in a folder, ensuring all have audio"""
        
        # Verify access
        folder = await self._get_accessible_folder(user_id, folder_id)
        
        words = self.word_repo.get_by_folder_id(folder_id)
        
        # Ensure all words have audio URLs
        updated_words = []
        for word in words:
            if not word.audio_url:
                # Generate audio for words that don't have it
                audio_url, audio_path = await self._ensure_audio_for_word(
                    word.translated_word, word.target_language
                )
                if audio_url:
                    # Update the word in database
                    update_data = {"audio_url": audio_url, "audio_path": audio_path}
                    word = self.word_repo.update(word, update_data)
            updated_words.append(word)
        
        return {
            "words": updated_words,
            "total": len(updated_words),
            "folder": folder
        }

    async def create_share_code(self, user_id: int, folder_id: int, duration: str) -> Dict:
        """Create share code for folder"""
        
        # Verify user owns the folder
        folder = self.folder_repo.get_user_folder_by_id(user_id, folder_id)
        if not folder:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.NOT_FOUND,
                detail="Folder not found"
            )

        # Validate duration
        if duration not in SHARE_CODE_DURATIONS:
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.BAD_REQUEST,
                detail="Invalid duration. Use: 10m, 1h, 24h, 72h"
            )

        # Calculate expiration
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=SHARE_CODE_DURATIONS[duration])

        # Delete existing share code for this folder (if any)
        existing_code = self.share_repo.get_by_folder_id(folder_id)
        if existing_code:
            self.share_repo.delete(existing_code.id)

        # Create new share code
        share_id, share_code = share_cleanup.create_share_code_with_id(
            self.share_repo.db, folder_id, user_id, duration, expires_at
        )

        return {
            "share_code": share_code,
            "expires_at": expires_at,
            "duration": duration
        }

    async def delete_share_code(self, user_id: int, folder_id: int) -> None:
        """Delete share code for folder"""
        
        # Verify user owns the folder
        folder = self.folder_repo.get_user_folder_by_id(user_id, folder_id)
        if not folder:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.NOT_FOUND,
                detail="Folder not found"
            )

        # Find and delete existing share code
        existing_code = self.share_repo.get_by_folder_id(folder_id)
        if not existing_code:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.NOT_FOUND,
                detail="No share code found for this folder"
            )

        self.share_repo.delete(existing_code.id)

    async def join_folder_by_code(self, user_id: int, share_code: str, is_premium: bool) -> VocabularyFolder:
        """Join a folder using share code"""
        
        # Find active share code
        code_record = self.share_repo.get_by_share_code(share_code)
        if not code_record:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.NOT_FOUND,
                detail="Invalid or expired share code"
            )

        folder_id = code_record.folder_id
        
        # Check if user already follows this folder
        if self.follower_repo.is_following(user_id, folder_id):
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.DUPLICATE_OPERATION,
                detail="You are already following this folder"
            )

        # Check if user owns this folder
        folder = self.folder_repo.get_user_folder_by_id(user_id, folder_id)
        if folder:
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.DUPLICATE_OPERATION,
                detail="You cannot follow your own folder"
            )

        # Check folder limit before joining
        self._check_folder_limit(user_id, is_premium)

        # Create follower record
        follower_data = {
            "folder_id": folder_id,
            "user_id": user_id,
            "joined_via_code": share_code
        }
        self.follower_repo.create(follower_data)

        # Return the folder
        return self.folder_repo.get_by_id(folder_id)
    
    async def unfollow_folder(self, user_id: int, folder_id: int) -> None:
        """Unfollow a folder"""
        
        # Check if user is following this folder
        if not self.follower_repo.is_following(user_id, folder_id):
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.NOT_FOUND,
                detail="You are not following this folder"
            )
        
        # Remove follower record
        follower_record = self.follower_repo.get_by_user_and_folder(user_id, folder_id)
        if follower_record:
            self.follower_repo.delete(follower_record.id)

    def get_user_folders(self, user_id: int) -> Dict:
        """Get all folders for user (owned + followed) with word counts"""
        
        # Get owned folders
        owned_folders = self.folder_repo.get_by_user_id(user_id)
        
        # Add word count to each owned folder
        for folder in owned_folders:
            folder.word_count = self.word_repo.count_folder_words(folder.id)
        
        # Get followed folders with JOIN to avoid N+1 queries
        followed_folders = self.follower_repo.get_user_followed_folders_with_details(user_id)
        
        # Add word count to each followed folder
        for folder_data in followed_folders:
            folder_data["folder"].word_count = self.word_repo.count_folder_words(folder_data["folder"].id)

        return {
            "owned_folders": owned_folders,
            "followed_folders": followed_folders
        }

    async def _get_accessible_folder(self, user_id: int, folder_id: int) -> VocabularyFolder:
        """Get folder if user has access (owns or follows)"""
        
        # Check if user owns the folder
        folder = self.folder_repo.get_user_folder_by_id(user_id, folder_id)
        if folder:
            return folder
        
        # Check if user follows the folder
        if self.follower_repo.is_following(user_id, folder_id):
            folder = self.folder_repo.get_by_id(folder_id)
            if folder and folder.is_active:
                return folder
        
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND,
            detail="Folder not found or access denied"
        )