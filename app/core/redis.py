"""Redis client configuration."""

import redis.asyncio as redis
from typing import Optional
from .config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client singleton."""
    
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Get Redis client instance."""
        if cls._instance is None:
            cls._instance = await cls.create_client()
        return cls._instance
    
    @classmethod
    async def create_client(cls) -> redis.Redis:
        """Create Redis client."""
        try:
            client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await client.ping()
            logger.info("Redis client connected successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    @classmethod
    async def close(cls):
        """Close Redis client."""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
            logger.info("Redis client closed")
    
    @classmethod
    async def health_check(cls) -> bool:
        """Check Redis health."""
        try:
            client = await cls.get_client()
            result = await client.ping()
            logger.debug(f"Redis health check successful: {result}")
            return True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()