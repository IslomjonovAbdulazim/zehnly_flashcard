from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone

from app.models.vocabulary import VocabularyWord, FolderShareCode, FolderFollower
from app.models.folder import VocabularyFolder
from app.repositories.base import BaseRepository

class VocabularyWordRepository(BaseRepository[VocabularyWord]):
    def __init__(self, db: Session):
        super().__init__(VocabularyWord, db)

    def get_by_folder_id(self, folder_id: int) -> List[VocabularyWord]:
        return (self.db.query(VocabularyWord)
                .filter(VocabularyWord.folder_id == folder_id, VocabularyWord.is_active == True)
                .all())

    def get_by_original_word(self, folder_id: int, original_word: str, target_language: str) -> Optional[VocabularyWord]:
        return (self.db.query(VocabularyWord)
                .filter(VocabularyWord.folder_id == folder_id,
                       VocabularyWord.original_word == original_word,
                       VocabularyWord.target_language == target_language,
                       VocabularyWord.is_active == True)
                .first())

    def search_words(self, folder_id: int, search_term: str) -> List[VocabularyWord]:
        return (self.db.query(VocabularyWord)
                .filter(VocabularyWord.folder_id == folder_id,
                       VocabularyWord.is_active == True,
                       VocabularyWord.original_word.contains(search_term))
                .all())

    def count_folder_words(self, folder_id: int) -> int:
        return (self.db.query(VocabularyWord)
                .filter(VocabularyWord.folder_id == folder_id, VocabularyWord.is_active == True)
                .count())

class VocabularyFolderRepository(BaseRepository[VocabularyFolder]):
    def __init__(self, db: Session):
        super().__init__(VocabularyFolder, db)

    def get_by_user_id(self, user_id: int) -> List[VocabularyFolder]:
        return (self.db.query(VocabularyFolder)
                .filter(VocabularyFolder.user_id == user_id, VocabularyFolder.is_active == True)
                .all())

    def get_user_folder_by_id(self, user_id: int, folder_id: int) -> Optional[VocabularyFolder]:
        return (self.db.query(VocabularyFolder)
                .filter(VocabularyFolder.id == folder_id,
                       VocabularyFolder.user_id == user_id,
                       VocabularyFolder.is_active == True)
                .first())

    def count_user_folders(self, user_id: int) -> int:
        return (self.db.query(VocabularyFolder)
                .filter(VocabularyFolder.user_id == user_id, VocabularyFolder.is_active == True)
                .count())

class FolderShareCodeRepository(BaseRepository[FolderShareCode]):
    def __init__(self, db: Session):
        super().__init__(FolderShareCode, db)

    def get_by_share_code(self, share_code: str) -> Optional[FolderShareCode]:
        return (self.db.query(FolderShareCode)
                .filter(FolderShareCode.share_code == share_code,
                       FolderShareCode.is_active == True,
                       FolderShareCode.expires_at > datetime.now(timezone.utc))
                .first())

    def get_by_folder_id(self, folder_id: int) -> Optional[FolderShareCode]:
        return (self.db.query(FolderShareCode)
                .filter(FolderShareCode.folder_id == folder_id,
                       FolderShareCode.is_active == True)
                .first())

    def delete_expired_codes(self) -> int:
        expired_codes = (self.db.query(FolderShareCode)
                        .filter(FolderShareCode.expires_at <= datetime.now(timezone.utc))
                        .all())
        
        count = len(expired_codes)
        for code in expired_codes:
            self.db.delete(code)
        
        self.db.commit()
        return count

class FolderFollowerRepository(BaseRepository[FolderFollower]):
    def __init__(self, db: Session):
        super().__init__(FolderFollower, db)

    def get_by_user_id(self, user_id: int) -> List[FolderFollower]:
        return (self.db.query(FolderFollower)
                .filter(FolderFollower.user_id == user_id, FolderFollower.is_active == True)
                .all())

    def get_by_folder_id(self, folder_id: int) -> List[FolderFollower]:
        return (self.db.query(FolderFollower)
                .filter(FolderFollower.folder_id == folder_id, FolderFollower.is_active == True)
                .all())

    def get_follower(self, user_id: int, folder_id: int) -> Optional[FolderFollower]:
        return (self.db.query(FolderFollower)
                .filter(FolderFollower.user_id == user_id,
                       FolderFollower.folder_id == folder_id,
                       FolderFollower.is_active == True)
                .first())

    def is_following(self, user_id: int, folder_id: int) -> bool:
        return self.get_follower(user_id, folder_id) is not None
    
    def get_by_user_and_folder(self, user_id: int, folder_id: int) -> Optional[FolderFollower]:
        return self.get_follower(user_id, folder_id)