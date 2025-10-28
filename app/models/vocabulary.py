from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base

class VocabularyWord(Base):
    __tablename__ = "vocabulary_words"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("vocabulary_folders.id"), nullable=False, index=True)
    
    # Original word (what user typed)
    original_word = Column(String, nullable=False)
    original_language = Column(String, nullable=True)  # Auto-detected or provided
    
    # Translated word (in target language)
    translated_word = Column(String, nullable=False)
    target_language = Column(String, nullable=False)  # Same as folder's target_language usually
    
    # Audio file path in Google Cloud
    audio_url = Column(String, nullable=True)  # Full URL to audio file
    audio_path = Column(String, nullable=True)  # Storage path for reference
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    folder = relationship("VocabularyFolder", back_populates="words")
    
    # Ensure unique words per folder
    __table_args__ = (
        UniqueConstraint('folder_id', 'original_word', 'target_language', name='unique_word_per_folder'),
    )

class FolderShareCode(Base):
    __tablename__ = "folder_share_codes"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("vocabulary_folders.id"), nullable=False, unique=True, index=True)  # One code per folder
    share_code = Column(String(5), unique=True, nullable=False, index=True)  # LLNNN format
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    duration_type = Column(String, nullable=False)  # "10m", "1h", "24h", "72h"
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    folder = relationship("VocabularyFolder", back_populates="share_code", uselist=False)  # One-to-one
    creator = relationship("User")

class FolderFollower(Base):
    __tablename__ = "folder_followers"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("vocabulary_folders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # How they found the folder
    joined_via_code = Column(String(5), nullable=True)  # Share code used
    
    is_active = Column(Boolean, default=True)
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    folder = relationship("VocabularyFolder", back_populates="followers")
    user = relationship("User", back_populates="followed_folders")
    
    # Ensure unique follower per folder
    __table_args__ = (
        UniqueConstraint('folder_id', 'user_id', name='unique_follower_per_folder'),
    )