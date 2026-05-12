"""Unit tests for rate limiter."""

import asyncio
import time

import pytest

from telegram_crawler.rate_limiter import TokenBucketRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_burst():
    limiter = TokenBucketRateLimiter(rate=100.0, burst=10)
    start = time.monotonic()
    for _ in range(10):
        await limiter.acquire()
    elapsed = time.monotonic() - start
    # 10 tokens should be available immediately (burst)
    assert elapsed < 0.2


@pytest.mark.asyncio
async def test_rate_limiter_blocks_when_exhausted():
    limiter = TokenBucketRateLimiter(rate=10.0, burst=5)
    # Use up burst tokens
    for _ in range(5):
        await limiter.acquire()
    # 6th acquire should wait
    start = time.monotonic()
    await limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed > 0.05  # At least some wait


@pytest.mark.asyncio
async def test_rate_limiter_refills_over_time():
    limiter = TokenBucketRateLimiter(rate=1000.0, burst=2)
    # Use burst
    await limiter.acquire()
    await limiter.acquire()
    # Wait for refill
    await asyncio.sleep(0.05)
    start = time.monotonic()
    await limiter.acquire()
    elapsed = time.monotonic() - start
    # Should refill quickly at 1000/sec rate
    assert elapsed < 0.1