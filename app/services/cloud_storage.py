import hashlib
import os
from typing import Optional
from google.cloud import storage
from google.oauth2 import service_account
import json

from app.config.settings import settings
from app.core.constants import AUDIO_STORAGE_FOLDER

class GoogleCloudStorageService:
    def __init__(self):
        self.bucket_name = settings.GOOGLE_CLOUD_BUCKET
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.client = self._get_client()
        self.bucket = self.client.bucket(self.bucket_name)

    def _get_client(self) -> storage.Client:
        """Initialize Google Cloud Storage client with service account credentials"""
        credentials_info = {
            "type": "service_account",
            "project_id": settings.GOOGLE_CLOUD_PROJECT,
            "private_key_id": settings.GOOGLE_CLOUD_PRIVATE_KEY_ID,
            "private_key": settings.GOOGLE_CLOUD_PRIVATE_KEY.replace('\\n', '\n'),
            "client_email": settings.GOOGLE_CLOUD_CLIENT_EMAIL,
            "client_id": settings.GOOGLE_CLOUD_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.GOOGLE_CLOUD_CLIENT_EMAIL}"
        }
        
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        return storage.Client(credentials=credentials, project=settings.GOOGLE_CLOUD_PROJECT)

    def generate_audio_path(self, word: str, language: str) -> str:
        """Generate consistent storage path for audio files"""
        # Create hash of word + language for unique filename
        word_hash = hashlib.md5(f"{word.lower()}_{language}".encode()).hexdigest()
        return f"{AUDIO_STORAGE_FOLDER}/{language}/{word_hash}.mp3"

    def upload_audio_file(self, audio_data: bytes, word: str, language: str) -> tuple[str, str]:
        """
        Upload audio file to Google Cloud Storage
        Returns: (storage_path, public_url)
        """
        storage_path = self.generate_audio_path(word, language)
        
        try:
            blob = self.bucket.blob(storage_path)
            blob.upload_from_string(
                audio_data,
                content_type='audio/mpeg'
            )
            
            # Make the blob publicly readable
            blob.make_public()
            
            public_url = blob.public_url
            return storage_path, public_url
            
        except Exception as e:
            raise Exception(f"Failed to upload audio to Google Cloud: {str(e)}")

    def file_exists(self, storage_path: str) -> bool:
        """Check if file exists in storage"""
        try:
            blob = self.bucket.blob(storage_path)
            return blob.exists()
        except Exception:
            return False

    def get_public_url(self, storage_path: str) -> Optional[str]:
        """Get public URL for existing file"""
        try:
            blob = self.bucket.blob(storage_path)
            if blob.exists():
                return blob.public_url
            return None
        except Exception:
            return None

    def delete_audio_file(self, storage_path: str) -> bool:
        """Delete audio file from storage"""
        try:
            blob = self.bucket.blob(storage_path)
            if blob.exists():
                blob.delete()
                return True
            return False
        except Exception:
            return False

# Global instance
cloud_storage = GoogleCloudStorageService()