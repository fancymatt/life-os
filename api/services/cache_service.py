"""
Response Caching Service

Provides Redis-based caching for API responses with:
- Automatic cache key generation
- TTL configuration per endpoint type
- Cache invalidation patterns
- Hit/miss metrics tracking
"""

import json
import hashlib
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
from api.logging_config import get_logger

logger = get_logger(__name__)


class CacheService:
    """Redis-based response caching service"""

    def __init__(self, redis_url: str = "redis://redis:6379/0", prefix: str = "cache:"):
        """
        Initialize cache service

        Args:
            redis_url: Redis connection URL
            prefix: Key prefix for cache entries
        """
        self.prefix = prefix
        self.redis_url = redis_url
        self.redis = None
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0,
        }

        # TTL configuration (in seconds)
        self.ttl_config = {
            "list": 60,          # 1 minute for list endpoints
            "detail": 300,       # 5 minutes for detail endpoints
            "static": 3600,      # 1 hour for static data (configs, etc.)
            "default": 120,      # 2 minutes default
        }

        self._connect()

    def _connect(self):
        """Connect to Redis"""
        try:
            import redis
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            self.redis.ping()
            logger.info(f"✅ Cache service connected to Redis: {self.redis_url}")
        except ImportError:
            logger.error("❌ Redis package not installed. Install with: pip install redis")
            self.redis = None
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis = None

    def _make_key(self, key_parts: List[str]) -> str:
        """
        Create cache key from parts

        Args:
            key_parts: List of key components (endpoint, params, etc.)

        Returns:
            Full cache key with prefix
        """
        # Join parts and hash if too long
        key_str = ":".join(str(p) for p in key_parts)

        # Hash if key is too long (Redis max key length is 512MB, but keep reasonable)
        if len(key_str) > 200:
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            return f"{self.prefix}{key_hash}"

        return f"{self.prefix}{key_str}"

    def generate_cache_key(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate cache key for an endpoint

        Args:
            endpoint: API endpoint path (e.g., "/api/characters")
            params: Query parameters and filters
            user_id: Optional user ID for user-specific caching

        Returns:
            Cache key
        """
        key_parts = [endpoint]

        if user_id:
            key_parts.append(f"user:{user_id}")

        if params:
            # Sort params for consistent keys
            sorted_params = sorted(params.items())
            for k, v in sorted_params:
                # Skip None values
                if v is not None:
                    key_parts.append(f"{k}={v}")

        return self._make_key(key_parts)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get cached value

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not self.redis:
            return None

        try:
            value = self.redis.get(key)
            if value:
                self._stats["hits"] += 1
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            else:
                self._stats["misses"] += 1
                logger.debug(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        cache_type: str = "default"
    ) -> bool:
        """
        Set cached value

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Optional TTL in seconds (overrides cache_type)
            cache_type: Cache type for TTL lookup (list, detail, static, default)

        Returns:
            True if cached successfully
        """
        if not self.redis:
            return False

        try:
            # Determine TTL
            ttl_seconds = ttl if ttl is not None else self.ttl_config.get(cache_type, self.ttl_config["default"])

            # Serialize and store
            serialized = json.dumps(value, default=str)  # default=str handles datetime
            self.redis.setex(key, ttl_seconds, serialized)

            self._stats["sets"] += 1
            logger.debug(f"Cache SET: {key} (TTL: {ttl_seconds}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete cached value

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        if not self.redis:
            return False

        try:
            deleted = self.redis.delete(key)
            if deleted:
                self._stats["invalidations"] += 1
                logger.debug(f"Cache DELETE: {key}")
            return deleted > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Key pattern (e.g., "cache:characters:*")

        Returns:
            Number of keys deleted
        """
        if not self.redis:
            return 0

        try:
            # Get all matching keys
            keys = self.redis.keys(pattern)
            if keys:
                deleted = self.redis.delete(*keys)
                self._stats["invalidations"] += deleted
                logger.info(f"Cache DELETE PATTERN: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    async def invalidate_endpoint(self, endpoint: str, user_id: Optional[str] = None):
        """
        Invalidate all cache entries for an endpoint

        Args:
            endpoint: API endpoint path
            user_id: Optional user ID to invalidate only user-specific caches
        """
        if user_id:
            pattern = f"{self.prefix}{endpoint}:user:{user_id}:*"
        else:
            pattern = f"{self.prefix}{endpoint}:*"

        await self.delete_pattern(pattern)

    async def invalidate_entity_type(self, entity_type: str):
        """
        Invalidate all caches for an entity type

        Examples:
            - invalidate_entity_type("characters") -> invalidates /characters/*
            - invalidate_entity_type("clothing_items") -> invalidates /clothing-items/*
            - invalidate_entity_type("visualization_configs") -> invalidates /visualization-configs/*

        Args:
            entity_type: Entity type (characters, stories, etc.)
        """
        # Convert entity_type to endpoint path
        # characters -> /characters
        # clothing_items -> /clothing-items
        # visualization_configs -> /visualization-configs
        endpoint_path = entity_type.replace("_", "-")
        pattern = f"{self.prefix}/{endpoint_path}*"
        await self.delete_pattern(pattern)

    async def clear_all(self):
        """Clear all cache entries (dangerous!)"""
        if not self.redis:
            return

        try:
            pattern = f"{self.prefix}*"
            keys = self.redis.keys(pattern)
            if keys:
                deleted = self.redis.delete(*keys)
                logger.warning(f"Cache CLEAR ALL: {deleted} keys deleted")
                self._stats["invalidations"] += deleted
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dict with hit/miss ratio, counts, etc.
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "sets": self._stats["sets"],
            "invalidations": self._stats["invalidations"],
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "connected": self.redis is not None,
        }

    def reset_stats(self):
        """Reset statistics counters"""
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0,
        }


# Global singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or initialize the global cache service"""
    global _cache_service

    if _cache_service is None:
        from api.config import settings
        _cache_service = CacheService(redis_url=settings.redis_url)

    return _cache_service
