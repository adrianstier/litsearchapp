"""Rate limiting utilities for API calls"""

import time
import asyncio
from typing import Optional
from collections import defaultdict
from datetime import datetime, timedelta


class RateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, calls_per_second: float = 1.0):
        """
        Initialize rate limiter

        Args:
            calls_per_second: Maximum number of calls per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second if calls_per_second > 0 else 0
        self.last_call = defaultdict(float)

    def wait_if_needed(self, key: str = "default"):
        """
        Wait if necessary to respect rate limit (synchronous)

        Args:
            key: Identifier for the rate limit bucket
        """
        if self.min_interval <= 0:
            return

        current_time = time.time()
        time_since_last_call = current_time - self.last_call[key]

        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            time.sleep(sleep_time)

        self.last_call[key] = time.time()

    async def async_wait_if_needed(self, key: str = "default"):
        """
        Wait if necessary to respect rate limit (asynchronous)

        Args:
            key: Identifier for the rate limit bucket
        """
        if self.min_interval <= 0:
            return

        current_time = time.time()
        time_since_last_call = current_time - self.last_call[key]

        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            await asyncio.sleep(sleep_time)

        self.last_call[key] = time.time()


class TokenBucket:
    """Token bucket rate limiter for more sophisticated rate limiting"""

    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket

        Args:
            rate: Tokens added per second
            capacity: Maximum number of tokens
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens from the bucket

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens were acquired, False otherwise
        """
        async with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_update
            self.last_update = current_time

            # Add new tokens based on elapsed time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    async def wait_and_acquire(self, tokens: int = 1):
        """
        Wait until tokens are available and acquire them

        Args:
            tokens: Number of tokens to acquire
        """
        while not await self.acquire(tokens):
            # Calculate wait time
            needed = tokens - self.tokens
            wait_time = needed / self.rate
            await asyncio.sleep(wait_time)