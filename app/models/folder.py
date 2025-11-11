from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base

class VocabularyFolder(Base):
    __tablename__ = "vocabulary_folders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    target_language = Column(String, nullable=False)  # Language user wants to learn
    native_language = Column(String, nullable=False, default="uz")  # User's native language
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_folders")
    words = relationship("VocabularyWord", back_populates="folder", cascade="all, delete-orphan")
    share_code = relationship("FolderShareCode", back_populates="folder", cascade="all, delete-orphan", uselist=False)  # One-to-one
    followers = relationship("FolderFollower", back_populates="folder", cascade="all, delete-orphan")