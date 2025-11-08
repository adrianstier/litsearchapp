"""Tests for rate limiting"""

import pytest
import time
from src.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test RateLimiter class"""

    def test_create_rate_limiter(self):
        """Test creating a rate limiter"""
        limiter = RateLimiter(requests_per_second=10)
        assert limiter.rate == 10
        assert limiter.tokens >= 0

    def test_acquire_within_limit(self):
        """Test acquiring token within rate limit"""
        limiter = RateLimiter(requests_per_second=100)

        # Should succeed immediately
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start

        # Should be nearly instant
        assert elapsed < 0.1

    def test_acquire_multiple_within_limit(self):
        """Test acquiring multiple tokens within limit"""
        limiter = RateLimiter(requests_per_second=100, capacity=10)

        # Acquire 5 tokens quickly
        for _ in range(5):
            limiter.acquire()

    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced"""
        limiter = RateLimiter(requests_per_second=2, capacity=2)

        # Drain the bucket
        limiter.acquire()
        limiter.acquire()

        # Next acquire should be delayed
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start

        # Should be delayed by ~0.5 seconds
        assert elapsed >= 0.4  # Allow some tolerance

    def test_token_refill(self):
        """Test that tokens refill over time"""
        limiter = RateLimiter(requests_per_second=10, capacity=5)

        # Drain tokens
        for _ in range(5):
            limiter.acquire()

        # Wait for refill
        time.sleep(0.6)  # Should refill ~6 tokens

        # Should be able to acquire again
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start

        assert elapsed < 0.1  # Should be fast

    def test_burst_capacity(self):
        """Test burst capacity"""
        limiter = RateLimiter(requests_per_second=1, capacity=5)

        # Should allow burst of 5 requests
        start = time.time()
        for _ in range(5):
            limiter.acquire()
        elapsed = time.time() - start

        # All 5 should be fast
        assert elapsed < 0.5

    def test_zero_capacity(self):
        """Test with capacity of 1 (no burst)"""
        limiter = RateLimiter(requests_per_second=10, capacity=1)

        limiter.acquire()
        limiter.acquire()

        # Should still work

    def test_high_rate_limit(self):
        """Test with very high rate limit"""
        limiter = RateLimiter(requests_per_second=1000)

        # Should handle many rapid requests
        for _ in range(10):
            limiter.acquire()

    def test_low_rate_limit(self):
        """Test with low rate limit"""
        limiter = RateLimiter(requests_per_second=0.5)  # 1 request per 2 seconds

        limiter.acquire()

        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start

        # Should be delayed ~2 seconds
        assert elapsed >= 1.5

    def test_concurrent_access(self):
        """Test rate limiter with concurrent access"""
        import threading

        limiter = RateLimiter(requests_per_second=10)
        results = []

        def worker():
            start = time.time()
            limiter.acquire()
            results.append(time.time() - start)

        threads = [threading.Thread(target=worker) for _ in range(5)]

        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should complete
        assert len(results) == 5

    def test_exact_timing(self):
        """Test timing precision"""
        limiter = RateLimiter(requests_per_second=5, capacity=1)

        times = []
        for _ in range(3):
            start = time.time()
            limiter.acquire()
            times.append(time.time() - start)

        # First should be fast, subsequent should be ~0.2s apart
        assert times[0] < 0.1
        if len(times) > 1:
            assert times[1] >= 0.15  # Allow some tolerance


class TestEdgeCases:
    """Test edge cases for rate limiter"""

    def test_fractional_rate(self):
        """Test fractional rate limit"""
        limiter = RateLimiter(requests_per_second=1.5)
        assert limiter.rate == 1.5

    def test_very_small_rate(self):
        """Test very small rate limit"""
        limiter = RateLimiter(requests_per_second=0.1)  # 1 request per 10 seconds
        assert limiter.rate == 0.1

    def test_large_capacity(self):
        """Test large burst capacity"""
        limiter = RateLimiter(requests_per_second=10, capacity=1000)

        # Should allow large burst
        for _ in range(100):
            limiter.acquire()

    def test_reset_behavior(self):
        """Test that limiter recovers after delay"""
        limiter = RateLimiter(requests_per_second=5, capacity=5)

        # Use up tokens
        for _ in range(5):
            limiter.acquire()

        # Wait for full recovery
        time.sleep(1.5)

        # Should be able to burst again
        start = time.time()
        for _ in range(5):
            limiter.acquire()
        elapsed = time.time() - start

        assert elapsed < 0.5

    def test_max_wait_time(self):
        """Test maximum wait time"""
        limiter = RateLimiter(requests_per_second=1, capacity=1)

        limiter.acquire()

        # Should wait at most ~1 second
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start

        assert elapsed < 1.5  # With tolerance
