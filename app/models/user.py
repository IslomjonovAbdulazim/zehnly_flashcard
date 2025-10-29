from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)  # MongoDB ObjectId from main server
    contact = Column(String, unique=True, index=True, nullable=True)  # Phone number or email
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owned_folders = relationship("VocabularyFolder", back_populates="owner", cascade="all, delete-orphan")
    followed_folders = relationship("FolderFollower", back_populates="user", cascade="all, delete-orphan")