"""
Redis async client.
Used for session caching, rate limiting, and Celery broker.
"""

from __future__ import annotations

import logging
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get or create the async Redis client."""
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        try:
            await _redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning("Redis not available: %s (will retry on demand)", e)
    return _redis


async def close_redis() -> None:
    """Close the Redis connection on shutdown."""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
        logger.info("Redis connection closed")


# ── Convenience helpers ──────────────────────────────────────────────────

async def cache_get(key: str) -> str | None:
    """Get a value from cache."""
    r = await get_redis()
    return await r.get(key)


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    """Set a value in cache with TTL (default 5 minutes)."""
    r = await get_redis()
    await r.set(key, value, ex=ttl)


async def cache_delete(key: str) -> None:
    """Delete a key from cache."""
    r = await get_redis()
    await r.delete(key)


async def cache_json_get(key: str) -> dict[str, Any] | None:
    """Get a JSON value from cache."""
    import json
    raw = await cache_get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def cache_json_set(key: str, value: dict[str, Any], ttl: int = 300) -> None:
    """Set a JSON value in cache."""
    import json
    await cache_set(key, json.dumps(value, default=str), ttl)
