"""
Caching Middleware for FastAPI

Provides decorators and utilities for response caching:
- @cached() decorator for read endpoints
- @invalidates_cache() decorator for write endpoints
- Automatic cache key generation from request
"""

from functools import wraps
from typing import Optional, Callable, List
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from api.services.cache_service import get_cache_service
from api.logging_config import get_logger

logger = get_logger(__name__)


def cached(
    cache_type: str = "default",
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    include_user: bool = False
):
    """
    Decorator to cache GET endpoint responses

    Usage:
        @router.get("/characters/")
        @cached(cache_type="list", include_user=True)
        async def list_characters(request: Request, limit: int = 50):
            ...

    Args:
        cache_type: Cache type (list, detail, static, default) for TTL lookup
        ttl: Optional explicit TTL in seconds (overrides cache_type)
        key_prefix: Optional key prefix (defaults to endpoint path)
        include_user: Include user ID in cache key (for user-specific data)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request: Optional[Request] = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None and "request" in kwargs:
                request = kwargs["request"]

            if not request:
                # No request object, can't cache
                logger.warning(f"No request object found for {func.__name__}, skipping cache")
                return await func(*args, **kwargs)

            # Get cache service
            cache = get_cache_service()
            if not cache.redis:
                # Redis not available, skip caching
                return await func(*args, **kwargs)

            # Generate cache key
            endpoint = key_prefix or request.url.path
            params = dict(request.query_params)
            user_id = None

            if include_user:
                # Try to get user from request state (set by auth middleware)
                user_id = getattr(request.state, "user_id", None)

            cache_key = cache.generate_cache_key(endpoint, params, user_id)

            # Try to get from cache
            cached_response = await cache.get(cache_key)
            if cached_response is not None:
                logger.info(f"Cache HIT for {endpoint} (key: {cache_key})")
                return JSONResponse(content=cached_response)

            logger.info(f"Cache MISS for {endpoint} (key: {cache_key})")

            # Execute endpoint
            result = await func(*args, **kwargs)

            # Cache the result if it's a successful response
            try:
                if isinstance(result, (dict, list)):
                    # Direct dict/list response
                    await cache.set(cache_key, result, ttl=ttl, cache_type=cache_type)
                elif isinstance(result, JSONResponse):
                    # JSONResponse object
                    import json
                    content = json.loads(result.body.decode())
                    await cache.set(cache_key, content, ttl=ttl, cache_type=cache_type)
                elif hasattr(result, 'model_dump'):
                    # Pydantic v2 model
                    content = result.model_dump()
                    await cache.set(cache_key, content, ttl=ttl, cache_type=cache_type)
                    logger.info(f"Cached Pydantic v2 model for {endpoint} (ttl: {ttl or cache.ttl_config.get(cache_type, 'default')}s)")
                elif hasattr(result, 'dict'):
                    # Pydantic v1 model
                    content = result.dict()
                    await cache.set(cache_key, content, ttl=ttl, cache_type=cache_type)
                    logger.info(f"Cached Pydantic v1 model for {endpoint} (ttl: {ttl or cache.ttl_config.get(cache_type, 'default')}s)")
                else:
                    logger.warning(f"Response type {type(result).__name__} not cacheable for {endpoint}")
            except Exception as e:
                logger.error(f"Failed to cache response for {endpoint}: {e}")

            return result

        return wrapper
    return decorator


def invalidates_cache(
    entity_types: Optional[List[str]] = None,
    endpoints: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None
):
    """
    Decorator to invalidate caches after write operations

    Usage:
        @router.post("/characters/")
        @invalidates_cache(entity_types=["characters"])
        async def create_character(character: CharacterCreate):
            ...

        @router.put("/characters/{character_id}")
        @invalidates_cache(entity_types=["characters"], endpoints=["/api/characters/{character_id}"])
        async def update_character(character_id: str, updates: CharacterUpdate):
            ...

    Args:
        entity_types: List of entity types to invalidate (e.g., ["characters", "stories"])
        endpoints: List of specific endpoints to invalidate
        patterns: List of Redis key patterns to delete
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute the endpoint first
            result = await func(*args, **kwargs)

            # Invalidate caches after successful execution
            cache = get_cache_service()
            if cache.redis:
                try:
                    # Invalidate by entity type
                    if entity_types:
                        for entity_type in entity_types:
                            await cache.invalidate_entity_type(entity_type)
                            logger.info(f"Invalidated cache for entity type: {entity_type}")

                    # Invalidate specific endpoints
                    if endpoints:
                        for endpoint in endpoints:
                            await cache.invalidate_endpoint(endpoint)
                            logger.info(f"Invalidated cache for endpoint: {endpoint}")

                    # Invalidate by pattern
                    if patterns:
                        for pattern in patterns:
                            await cache.delete_pattern(pattern)
                            logger.info(f"Invalidated cache by pattern: {pattern}")
                except Exception as e:
                    logger.error(f"Cache invalidation error: {e}")

            return result

        return wrapper
    return decorator


async def invalidate_user_cache(user_id: str, entity_type: Optional[str] = None):
    """
    Helper to invalidate all caches for a specific user

    Args:
        user_id: User ID
        entity_type: Optional entity type to limit invalidation
    """
    cache = get_cache_service()
    if cache.redis:
        if entity_type:
            endpoint_path = entity_type.replace("_", "-")
            pattern = f"{cache.prefix}/api/{endpoint_path}:user:{user_id}:*"
        else:
            pattern = f"{cache.prefix}*:user:{user_id}:*"

        await cache.delete_pattern(pattern)
        logger.info(f"Invalidated all cache for user: {user_id}")


async def get_cache_stats():
    """Get cache statistics (for monitoring endpoint)"""
    cache = get_cache_service()
    return cache.get_stats()
