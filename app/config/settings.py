from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A scalable FastAPI backend"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # JWT Configuration
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    
    # Database
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # CORS
    ALLOWED_HOSTS: Union[str, List[str]] = ["*"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # External APIs
    NARAKEET: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_BUCKET: Optional[str] = None
    GOOGLE_CLOUD_PRIVATE_KEY_ID: Optional[str] = None
    GOOGLE_CLOUD_PRIVATE_KEY: Optional[str] = None
    GOOGLE_CLOUD_CLIENT_EMAIL: Optional[str] = None
    GOOGLE_CLOUD_CLIENT_ID: Optional[str] = None
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                return json.loads(v)
            elif "," in v:
                return [i.strip() for i in v.split(",")]
            else:
                return [v.strip()]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid ALLOWED_HOSTS format: {v}")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()