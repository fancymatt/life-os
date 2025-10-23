"""
Cache Management Routes

Provides endpoints for cache statistics and management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.middleware.cache import get_cache_stats
from api.services.cache_service import get_cache_service
from api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/cache", tags=["cache"])


class CacheStats(BaseModel):
    """Cache statistics response"""
    hits: int
    misses: int
    sets: int
    invalidations: int
    total_requests: int
    hit_rate_percent: float
    connected: bool


class CacheInvalidateRequest(BaseModel):
    """Cache invalidation request"""
    entity_type: Optional[str] = None
    endpoint: Optional[str] = None
    pattern: Optional[str] = None


@router.get("/stats", response_model=CacheStats)
async def cache_statistics():
    """
    Get cache statistics

    Returns hit/miss counts, hit rate, and connection status.
    """
    stats = await get_cache_stats()
    return CacheStats(**stats)


@router.post("/invalidate")
async def invalidate_cache(request: CacheInvalidateRequest):
    """
    Manually invalidate cache entries

    Supports invalidation by:
    - entity_type: Invalidate all caches for an entity (e.g., "characters")
    - endpoint: Invalidate specific endpoint (e.g., "/api/characters/")
    - pattern: Invalidate by Redis key pattern (e.g., "cache:characters:*")
    """
    cache = get_cache_service()

    if not cache.redis:
        raise HTTPException(status_code=503, detail="Cache service not available")

    invalidated_count = 0

    try:
        if request.entity_type:
            await cache.invalidate_entity_type(request.entity_type)
            logger.info(f"Invalidated cache for entity type: {request.entity_type}")
            invalidated_count += 1

        if request.endpoint:
            await cache.invalidate_endpoint(request.endpoint)
            logger.info(f"Invalidated cache for endpoint: {request.endpoint}")
            invalidated_count += 1

        if request.pattern:
            count = await cache.delete_pattern(request.pattern)
            logger.info(f"Invalidated {count} cache entries by pattern: {request.pattern}")
            invalidated_count += count

        return {
            "status": "success",
            "invalidated_count": invalidated_count,
            "message": f"Invalidated {invalidated_count} cache entries"
        }
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")


@router.post("/clear")
async def clear_cache():
    """
    Clear all cache entries (dangerous!)

    Use with caution - this removes ALL cached responses.
    """
    cache = get_cache_service()

    if not cache.redis:
        raise HTTPException(status_code=503, detail="Cache service not available")

    try:
        await cache.clear_all()
        logger.warning("Cache cleared by admin")
        return {
            "status": "success",
            "message": "All cache entries cleared"
        }
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")


@router.post("/reset-stats")
async def reset_cache_stats():
    """Reset cache statistics counters"""
    cache = get_cache_service()
    cache.reset_stats()
    logger.info("Cache statistics reset")
    return {
        "status": "success",
        "message": "Cache statistics reset"
    }
