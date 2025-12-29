"""In-memory caching with TTL support"""

import time
import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
from threading import Lock
from dataclasses import dataclass
from .logging_config import get_logger

logger = get_logger("utils.cache")


@dataclass
class CacheEntry:
    """A single cache entry with value and expiration time"""
    value: Any
    expires_at: float


class Cache:
    """Thread-safe in-memory cache with TTL support"""

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds (default 5 minutes)
            max_size: Maximum number of items in cache
        """
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            if time.time() > entry.expires_at:
                # Entry expired, remove it
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache expired: {key[:16]}...")
                return None

            self._hits += 1
            logger.debug(f"Cache hit: {key[:16]}...")
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        with self._lock:
            # Cleanup if cache is full
            if len(self._cache) >= self.max_size:
                self._cleanup_expired()

                # If still full, remove oldest entries
                if len(self._cache) >= self.max_size:
                    self._evict_oldest(self.max_size // 4)

            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
            logger.debug(f"Cache set: {key[:16]}... (TTL: {ttl}s)")

    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")

    def _cleanup_expired(self) -> int:
        """Remove expired entries. Must be called with lock held."""
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if v.expires_at < now]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    def _evict_oldest(self, count: int) -> None:
        """Evict oldest entries. Must be called with lock held."""
        sorted_entries = sorted(self._cache.items(), key=lambda x: x[1].expires_at)
        for key, _ in sorted_entries[:count]:
            del self._cache[key]

    def stats(self) -> dict:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%"
            }


# Global cache instance
_cache = Cache(default_ttl=300, max_size=1000)


def get_cache() -> Cache:
    """Get the global cache instance"""
    return _cache


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key

    Usage:
        @cached(ttl=60, key_prefix="search")
        def expensive_function(arg1, arg2):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            arg_key = cache._generate_key(*args, **kwargs)
            cache_key = f"{func_key}:{arg_key}"

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator


def cached_async(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache async function results.

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            arg_key = cache._generate_key(*args, **kwargs)
            cache_key = f"{func_key}:{arg_key}"

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
