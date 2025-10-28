"""
Share code cleanup service for expired codes
Handles automatic cleanup and overflow management
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.config.database import SessionLocal
from app.models.vocabulary import FolderShareCode
from app.utils.share_code_generator import ShareCodeGenerator

class ShareCodeCleanupService:
    
    @staticmethod
    def cleanup_expired_codes(db: Session) -> int:
        """
        Delete expired share codes from database
        Returns: number of codes deleted
        """
        now = datetime.now(timezone.utc)
        
        # Find and delete expired codes
        expired_codes = db.query(FolderShareCode).filter(
            or_(
                FolderShareCode.expires_at <= now,
                FolderShareCode.is_active == False
            )
        ).all()
        
        count = len(expired_codes)
        
        for code in expired_codes:
            db.delete(code)
        
        db.commit()
        return count
    
    @staticmethod
    def get_next_available_id(db: Session) -> int:
        """
        Get the next available ID for share code generation
        Handles overflow by cycling back to beginning
        """
        # Get the current maximum ID
        max_id_result = db.query(db.func.max(FolderShareCode.id)).scalar()
        current_max_id = max_id_result if max_id_result else 0
        
        # Handle overflow using the generator's logic
        next_id = ShareCodeGenerator.get_next_id_for_overflow(current_max_id)
        
        # If we're cycling back, check if that ID is available (not expired)
        if next_id <= current_max_id:
            # We're in overflow mode, find the first available ID
            existing_code = db.query(FolderShareCode).filter(
                FolderShareCode.id == next_id,
                FolderShareCode.is_active == True,
                FolderShareCode.expires_at > datetime.now(timezone.utc)
            ).first()
            
            # If the slot is occupied by a non-expired code, find next available
            if existing_code:
                # Find first available ID in range 1 to MAX_CODES
                for test_id in range(1, ShareCodeGenerator.MAX_CODES + 1):
                    test_code = db.query(FolderShareCode).filter(
                        FolderShareCode.id == test_id,
                        FolderShareCode.is_active == True,
                        FolderShareCode.expires_at > datetime.now(timezone.utc)
                    ).first()
                    
                    if not test_code:
                        return test_id
                
                # If all slots are full (highly unlikely), clean expired and try again
                ShareCodeCleanupService.cleanup_expired_codes(db)
                return ShareCodeCleanupService.get_next_available_id(db)
        
        return next_id
    
    @staticmethod
    def create_share_code_with_id(db: Session, folder_id: int, user_id: int, duration_type: str, expires_at: datetime) -> tuple[int, str]:
        """
        Create a new share code with proper ID management
        Returns: (id, share_code)
        """
        # Clean up expired codes first
        ShareCodeCleanupService.cleanup_expired_codes(db)
        
        # Get next available ID
        next_id = ShareCodeCleanupService.get_next_available_id(db)
        
        # Generate the share code
        share_code = ShareCodeGenerator.id_to_code(next_id)
        
        # If there's an existing code with this ID, delete it first (it must be expired)
        existing = db.query(FolderShareCode).filter(FolderShareCode.id == next_id).first()
        if existing:
            db.delete(existing)
            db.flush()  # Ensure deletion is committed before insert
        
        # Create new share code entry
        new_code = FolderShareCode(
            id=next_id,
            folder_id=folder_id,
            share_code=share_code,
            expires_at=expires_at,
            duration_type=duration_type,
            created_by=user_id,
            is_active=True
        )
        
        db.add(new_code)
        db.commit()
        db.refresh(new_code)
        
        return next_id, share_code
    
    @staticmethod
    def run_periodic_cleanup():
        """
        Run periodic cleanup of expired codes
        This can be called by a background task/scheduler
        """
        db = SessionLocal()
        try:
            cleaned_count = ShareCodeCleanupService.cleanup_expired_codes(db)
            if cleaned_count > 0:
                print(f"Cleaned up {cleaned_count} expired share codes")
        finally:
            db.close()

# Global instance
share_cleanup = ShareCodeCleanupService()