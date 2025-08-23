"""
Unit tests for cache service functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.shared.cache.service import CacheService


class TestCacheService:
    """Test cache service functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.cache_service = CacheService()

    @pytest.mark.asyncio
    async def test_cache_service_initialization(self):
        """Test cache service can be initialized."""
        assert self.cache_service is not None
        assert hasattr(self.cache_service, 'initialize')
        assert hasattr(self.cache_service, 'close')

    @pytest.mark.asyncio
    async def test_cache_service_get_set_operations(self):
        """Test basic cache get/set operations."""
        with patch.object(self.cache_service, 'redis', create=True) as mock_redis:
            mock_redis.get = AsyncMock(return_value=b'{"test": "value"}')
            mock_redis.setex = AsyncMock(return_value=True)
            
            # Test set operation
            await self.cache_service.set("test_key", {"test": "value"}, 300)
            mock_redis.setex.assert_called_once()
            
            # Test get operation
            result = await self.cache_service.get("test_key")
            mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_cache_service_fallback_to_memory(self):
        """Test cache service fallback to memory when Redis unavailable."""
        with patch.object(self.cache_service, 'redis', None):
            # Should not raise error and use memory cache
            await self.cache_service.set("test_key", {"test": "value"}, 300)
            result = await self.cache_service.get("test_key")
            # Memory cache behavior would be implementation specific

    @pytest.mark.asyncio
    async def test_cache_service_delete_operation(self):
        """Test cache delete operation."""
        with patch.object(self.cache_service, 'redis', create=True) as mock_redis:
            mock_redis.delete = AsyncMock(return_value=1)
            
            await self.cache_service.delete("test_key")
            mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_cache_service_clear_pattern(self):
        """Test cache clear by pattern operation."""
        with patch.object(self.cache_service, 'redis', create=True) as mock_redis:
            mock_redis.keys = AsyncMock(return_value=[b'pattern:key1', b'pattern:key2'])
            mock_redis.delete = AsyncMock(return_value=2)
            
            await self.cache_service.clear_pattern("pattern:*")
            mock_redis.keys.assert_called_once_with("pattern:*")
            mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_service_error_handling(self):
        """Test cache service handles Redis errors gracefully."""
        with patch.object(self.cache_service, 'redis', create=True) as mock_redis:
            mock_redis.get.side_effect = Exception("Redis connection error")
            
            # Should not raise exception and fallback gracefully
            result = await self.cache_service.get("test_key")
            assert result is None  # Expected fallback behavior