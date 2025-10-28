from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.folder import Folder
from app.repositories.base import BaseRepository

class FolderRepository(BaseRepository[Folder]):
    def __init__(self, db: Session):
        super().__init__(Folder, db)

    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Folder]:
        return (self.db.query(Folder)
                .filter(Folder.user_id == user_id, Folder.is_active == True)
                .offset(skip).limit(limit).all())

    def get_by_user_and_language(self, user_id: int, language: str) -> List[Folder]:
        return (self.db.query(Folder)
                .filter(Folder.user_id == user_id, 
                       Folder.language == language, 
                       Folder.is_active == True)
                .all())

    def get_user_folder_by_id(self, user_id: int, folder_id: int) -> Optional[Folder]:
        return (self.db.query(Folder)
                .filter(Folder.id == folder_id, 
                       Folder.user_id == user_id)
                .first())

    def count_user_folders(self, user_id: int) -> int:
        return (self.db.query(Folder)
                .filter(Folder.user_id == user_id, Folder.is_active == True)
                .count())

    def create_folder(self, folder_data: dict) -> Folder:
        return self.create(folder_data)

    def update_folder(self, folder: Folder, folder_data: dict) -> Folder:
        return self.update(folder, folder_data)

    def delete_folder(self, folder: Folder) -> bool:
        # Soft delete by setting is_active to False
        folder.is_active = False
        self.db.commit()
        return True