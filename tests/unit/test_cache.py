"""Tests for the caching module"""

import pytest
import time
from src.utils.cache import Cache, get_cache, cached


class TestCache:
    """Test suite for Cache class"""

    def test_cache_init(self):
        """Test cache initialization"""
        cache = Cache(default_ttl=60, max_size=100)
        assert cache.default_ttl == 60
        assert cache.max_size == 100

    def test_cache_set_and_get(self):
        """Test setting and getting cache values"""
        cache = Cache()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_get_nonexistent(self):
        """Test getting a key that doesn't exist"""
        cache = Cache()
        assert cache.get("nonexistent") is None

    def test_cache_expiration(self):
        """Test that cache entries expire correctly"""
        cache = Cache(default_ttl=1)

        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"

        time.sleep(1.5)
        assert cache.get("key1") is None

    def test_cache_delete(self):
        """Test deleting cache entries"""
        cache = Cache()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        result = cache.delete("key1")
        assert result is True
        assert cache.get("key1") is None

    def test_cache_delete_nonexistent(self):
        """Test deleting a key that doesn't exist"""
        cache = Cache()
        result = cache.delete("nonexistent")
        assert result is False

    def test_cache_clear(self):
        """Test clearing all cache entries"""
        cache = Cache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = Cache(max_size=100)

        # Initially empty
        stats = cache.stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

        # Add some entries and access them
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.stats()
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == "50.0%"

    def test_cache_max_size_eviction(self):
        """Test that cache evicts entries when max size is reached"""
        cache = Cache(max_size=5)

        # Fill the cache
        for i in range(10):
            cache.set(f"key{i}", f"value{i}")

        # Check size doesn't exceed max
        stats = cache.stats()
        assert stats["size"] <= cache.max_size

    def test_cache_different_value_types(self):
        """Test caching different data types"""
        cache = Cache()

        # String
        cache.set("string", "hello")
        assert cache.get("string") == "hello"

        # Integer
        cache.set("int", 42)
        assert cache.get("int") == 42

        # List
        cache.set("list", [1, 2, 3])
        assert cache.get("list") == [1, 2, 3]

        # Dict
        cache.set("dict", {"a": 1, "b": 2})
        assert cache.get("dict") == {"a": 1, "b": 2}

        # None
        cache.set("none", None)
        # Note: None is a valid value, but our get returns None for missing
        # So we need to check if key exists differently

    def test_cache_custom_ttl(self):
        """Test setting custom TTL per entry"""
        cache = Cache(default_ttl=60)

        # Short TTL
        cache.set("short", "value", ttl=1)
        # Long TTL
        cache.set("long", "value", ttl=10)

        time.sleep(1.5)

        assert cache.get("short") is None
        assert cache.get("long") == "value"


class TestCachedDecorator:
    """Test suite for cached decorator"""

    def test_cached_function(self):
        """Test that cached decorator caches results"""
        call_count = 0

        @cached(ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # First call - should execute function
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Second call with same args - should use cache
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Not incremented

        # Different args - should execute function
        result3 = expensive_function(3, 4)
        assert result3 == 7
        assert call_count == 2

    def test_cached_with_key_prefix(self):
        """Test cached decorator with key prefix"""
        @cached(ttl=60, key_prefix="test")
        def my_function(x):
            return x * 2

        result = my_function(5)
        assert result == 10

    def test_cached_expiration(self):
        """Test that cached results expire"""
        call_count = 0

        @cached(ttl=1)
        def expiring_function():
            nonlocal call_count
            call_count += 1
            return "result"

        result1 = expiring_function()
        assert call_count == 1

        # Wait for expiration
        time.sleep(1.5)

        # Should call function again
        result2 = expiring_function()
        assert call_count == 2


class TestGlobalCache:
    """Test suite for global cache instance"""

    def test_get_cache_singleton(self):
        """Test that get_cache returns the same instance"""
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2

    def test_global_cache_operations(self):
        """Test operations on global cache"""
        cache = get_cache()

        # Clear first to ensure clean state
        cache.clear()

        cache.set("global_test", "value")
        assert cache.get("global_test") == "value"

        # Clean up
        cache.delete("global_test")
