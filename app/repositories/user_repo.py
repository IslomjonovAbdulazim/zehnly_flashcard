from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_external_id(self, external_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.external_id == external_id).first()

    def get_by_contact(self, contact: str) -> Optional[User]:
        return self.db.query(User).filter(User.contact == contact).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_active_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def create_user(self, user_data: dict) -> User:
        return self.create(user_data)

    def update_user(self, user: User, user_data: dict) -> User:
        return self.update(user, user_data)

    def get_user_stats(self) -> dict:
        """Get overall user statistics"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users
        }