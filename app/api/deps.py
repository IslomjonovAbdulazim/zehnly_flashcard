from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.repositories.user_repo import UserRepository
from app.repositories.folder_repo import FolderRepository
from app.services.user_service import UserService
from app.services.folder_service import FolderService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

def get_folder_service(db: Session = Depends(get_db)) -> FolderService:
    folder_repo = FolderRepository(db)
    return FolderService(folder_repo)