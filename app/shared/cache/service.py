"""
Cache service with Redis backend and optional fallback.
Provides a flexible caching layer that can be enabled/disabled via environment variables.
"""

import json
import logging
from typing import Any, Optional, Union, Dict
from functools import wraps
import asyncio
from datetime import datetime, timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    Async cache service with Redis backend and optional in-memory fallback.
    Gracefully handles Redis unavailability and can be disabled via config.
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.enabled = settings.REDIS_ENABLED
        self.redis_available = False
        
    async def initialize(self):
        """Initialize Redis connection if enabled and available."""
        if not self.enabled:
            logger.info("Cache is disabled via configuration")
            return
            
        if not REDIS_AVAILABLE:
            logger.warning("Redis package not available, falling back to memory cache")
            return
            
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            await self.redis_client.ping()
            self.redis_available = True
            logger.info(f"Redis cache initialized successfully: {settings.REDIS_URL}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Using memory cache fallback.")
            self.redis_client = None
            self.redis_available = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
            
        try:
            if self.redis_available and self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Memory cache fallback
                cache_entry = self.memory_cache.get(key)
                if cache_entry:
                    if datetime.now() < cache_entry['expires']:
                        return cache_entry['value']
                    else:
                        # Expired, remove from cache
                        del self.memory_cache[key]
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL."""
        if not self.enabled:
            return False
            
        if ttl is None:
            ttl = settings.REDIS_TTL_DEFAULT
            
        try:
            if self.redis_available and self.redis_client:
                serialized_value = json.dumps(value, default=str)
                await self.redis_client.setex(key, ttl, serialized_value)
                return True
            else:
                # Memory cache fallback
                self.memory_cache[key] = {
                    'value': value,
                    'expires': datetime.now() + timedelta(seconds=ttl)
                }
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.enabled:
            return False
            
        try:
            if self.redis_available and self.redis_client:
                await self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> bool:
        """Clear all keys matching pattern."""
        if not self.enabled:
            return False
            
        try:
            if self.redis_available and self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                # Memory cache pattern matching
                keys_to_delete = [key for key in self.memory_cache.keys() 
                                if pattern.replace('*', '') in key]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return False
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


# Global cache instance
cache_service = CacheService()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = []
    for arg in args:
        if isinstance(arg, (str, int, float)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)


def cached(ttl: int = None, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cache_service.enabled:
                return await func(*args, **kwargs)
            
            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            cache_key_str = cache_key(key_prefix, func_name, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key_str)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key_str}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key_str, result, ttl)
            logger.debug(f"Cache miss for {cache_key_str}, result cached")
            
            return result
        return wrapper
    return decorator


def cache_invalidate_pattern(pattern: str):
    """
    Decorator to invalidate cache patterns after function execution.
    Useful for functions that modify data.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await cache_service.clear_pattern(pattern)
            logger.debug(f"Cache invalidated for pattern: {pattern}")
            return result
        return wrapper
    return decorator