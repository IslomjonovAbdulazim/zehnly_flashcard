import json
import redis
from typing import Optional, Any
from app.config.settings import settings

class CacheService:
    def __init__(self):
        self.redis_client = None
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                # Test connection
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}")
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (default 1 hour)"""
        if not self.redis_client:
            return False
        try:
            return self.redis_client.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self.redis_client is not None

# Global cache instance
cache_service = CacheService()