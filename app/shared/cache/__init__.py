"""Cache module with Redis support."""

from .service import cache_service, cached, cache_invalidate_pattern, cache_key

__all__ = ["cache_service", "cached", "cache_invalidate_pattern", "cache_key"]