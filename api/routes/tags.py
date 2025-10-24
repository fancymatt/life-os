"""
Tag Routes

Endpoints for managing tags and entity-tag relationships.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.requests import TagCreate, TagUpdate, EntityTagRequest, SetEntityTagsRequest
from api.models.responses import (
    TagInfo,
    TagListResponse,
    EntityTagsResponse,
    TagStatisticsResponse,
    TagAutocompleteResponse
)
from api.services.tag_service import TagService
from api.database import get_db
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from api.logging_config import get_logger
from api.middleware.cache import cached, invalidates_cache

router = APIRouter()
logger = get_logger(__name__)


# ============================================================================
# Tag CRUD Endpoints
# ============================================================================

@router.get("/", response_model=TagListResponse)
@cached(cache_type="list", include_user=True)
async def list_tags(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search tag names"),
    limit: int = Query(100, le=1000, description="Maximum number of tags to return"),
    offset: int = Query(0, ge=0, description="Number of tags to skip"),
    order_by: str = Query("usage_count", description="Sort order: usage_count, name, created_at"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all tags with optional filtering and sorting.

    **Filtering**:
    - category: Filter tags by category (material, style, season, etc.)
    - search: Search for tags by partial name match

    **Sorting**:
    - usage_count (default): Sort by most used tags first
    - name: Sort alphabetically
    - created_at: Sort by creation date (newest first)

    **Cached**: 60 seconds (user-specific)
    """
    service = TagService()
    user_id = current_user.id if current_user else None

    tags = await service.list_tags(
        category=category,
        user_id=user_id,
        search=search,
        limit=limit,
        offset=offset
    )

    tag_infos = [
        TagInfo(
            tag_id=tag.tag_id,
            name=tag.name,
            category=tag.category,
            color=tag.color,
            usage_count=tag.usage_count,
            created_at=tag.created_at.isoformat() if tag.created_at else None,
            updated_at=tag.updated_at.isoformat() if tag.updated_at else None
        )
        for tag in tags
    ]

    return TagListResponse(
        count=len(tag_infos),
        tags=tag_infos
    )


@router.post("/", response_model=TagInfo)
@invalidates_cache(entity_types=["tags"])
async def create_tag(
    request: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new tag.

    If a tag with the same name already exists, returns the existing tag.

    **Validation**:
    - Name is normalized (lowercase, trimmed, spaces collapsed)
    - Category is validated against known categories
    - Color must be valid hex format (#RRGGBB)

    **Cache Invalidation**: Clears all tag list caches
    """
    service = TagService()
    user_id = current_user.id if current_user else None

    tag = await service.create_tag(
        name=request.name,
        category=request.category,
        color=request.color,
        user_id=user_id
    )

    return TagInfo(
        tag_id=tag.tag_id,
        name=tag.name,
        category=tag.category,
        color=tag.color,
        usage_count=tag.usage_count,
        created_at=tag.created_at.isoformat() if tag.created_at else None,
        updated_at=tag.updated_at.isoformat() if tag.updated_at else None
    )


@router.get("/{tag_id}", response_model=TagInfo)
@cached(cache_type="detail", include_user=True)
async def get_tag(
    request: Request,
    tag_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a tag by ID.

    **Cached**: 5 minutes (user-specific)
    """
    service = TagService()
    tag = await service.repository.get_tag_by_id(tag_id)

    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")

    return TagInfo(
        tag_id=tag.tag_id,
        name=tag.name,
        category=tag.category,
        color=tag.color,
        usage_count=tag.usage_count,
        created_at=tag.created_at.isoformat() if tag.created_at else None,
        updated_at=tag.updated_at.isoformat() if tag.updated_at else None
    )


@router.put("/{tag_id}", response_model=TagInfo)
@invalidates_cache(entity_types=["tags"])
async def update_tag(
    tag_id: str,
    request: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update a tag.

    Only provided fields will be updated.

    **Cache Invalidation**: Clears all tag caches
    """
    service = TagService()

    tag = await service.update_tag(
        tag_id=tag_id,
        name=request.name,
        category=request.category,
        color=request.color
    )

    return TagInfo(
        tag_id=tag.tag_id,
        name=tag.name,
        category=tag.category,
        color=tag.color,
        usage_count=tag.usage_count,
        created_at=tag.created_at.isoformat() if tag.created_at else None,
        updated_at=tag.updated_at.isoformat() if tag.updated_at else None
    )


@router.delete("/{tag_id}")
@invalidates_cache(entity_types=["tags"])
async def delete_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a tag and all its relationships.

    **Warning**: This permanently deletes the tag and removes it from all tagged entities.

    **Cache Invalidation**: Clears all tag caches
    """
    service = TagService()
    success = await service.delete_tag(tag_id)

    return {"message": f"Tag {tag_id} deleted successfully"}


# ============================================================================
# Tag Search & Discovery
# ============================================================================

@router.get("/autocomplete/search", response_model=TagAutocompleteResponse)
async def autocomplete_tags(
    query: str = Query(..., min_length=1, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, le=50, description="Maximum number of suggestions"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Autocomplete tag search.

    Returns tags matching the query, ordered by usage count.
    Used for tag input autocomplete in the UI.

    **No caching** - real-time search
    """
    service = TagService()
    user_id = current_user.id if current_user else None

    suggestions = await service.autocomplete(
        query=query,
        category=category,
        user_id=user_id,
        limit=limit
    )

    tag_infos = [
        TagInfo(
            tag_id=tag["tag_id"],
            name=tag["name"],
            category=tag.get("category"),
            color=tag.get("color"),
            usage_count=tag.get("usage_count", 0)
        )
        for tag in suggestions
    ]

    return TagAutocompleteResponse(
        query=query,
        suggestions=tag_infos
    )


@router.get("/statistics/usage", response_model=TagStatisticsResponse)
@cached(cache_type="list", include_user=False)
async def get_tag_statistics(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get tag usage statistics.

    Returns:
    - Total tags count
    - Total entity-tag relationships
    - Top 20 most used tags
    - Tag count by category

    **Cached**: 60 seconds (global)
    """
    service = TagService()
    stats = await service.get_statistics()

    return TagStatisticsResponse(
        total_tags=stats["total_tags"],
        total_relationships=stats["total_relationships"],
        top_tags=stats["top_tags"],
        tags_by_category=stats["tags_by_category"]
    )


# ============================================================================
# Entity Tagging Endpoints
# ============================================================================

@router.get("/entity/{entity_type}/{entity_id}", response_model=EntityTagsResponse)
@cached(cache_type="detail", include_user=True)
async def get_entity_tags(
    request: Request,
    entity_type: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tags for an entity.

    **Cached**: 5 minutes (user-specific)
    """
    service = TagService()
    tags = await service.get_entity_tags(entity_type, entity_id)

    tag_infos = [
        TagInfo(
            tag_id=tag.tag_id,
            name=tag.name,
            category=tag.category,
            color=tag.color,
            usage_count=tag.usage_count,
            created_at=tag.created_at.isoformat() if tag.created_at else None,
            updated_at=tag.updated_at.isoformat() if tag.updated_at else None
        )
        for tag in tags
    ]

    return EntityTagsResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        tags=tag_infos
    )


@router.post("/entity/{entity_type}/{entity_id}", response_model=EntityTagsResponse)
@invalidates_cache(entity_types=["tags"])
async def tag_entity(
    entity_type: str,
    entity_id: str,
    request: EntityTagRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Add tags to an entity.

    Tags that don't exist will be auto-created if auto_create=True.
    Tags that already exist on the entity will be skipped.

    **Cache Invalidation**: Clears all tag caches and entity caches
    """
    service = TagService()
    user_id = current_user.id if current_user else None

    tags = await service.tag_entity(
        entity_type=entity_type,
        entity_id=entity_id,
        tag_names=request.tag_names,
        user_id=user_id,
        auto_create=request.auto_create
    )

    tag_infos = [
        TagInfo(
            tag_id=tag.tag_id,
            name=tag.name,
            category=tag.category,
            color=tag.color,
            usage_count=tag.usage_count,
            created_at=tag.created_at.isoformat() if tag.created_at else None,
            updated_at=tag.updated_at.isoformat() if tag.updated_at else None
        )
        for tag in tags
    ]

    return EntityTagsResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        tags=tag_infos
    )


@router.put("/entity/{entity_type}/{entity_id}", response_model=EntityTagsResponse)
@invalidates_cache(entity_types=["tags"])
async def set_entity_tags(
    entity_type: str,
    entity_id: str,
    request: SetEntityTagsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Set all tags for an entity (replaces existing tags).

    This is the preferred method for updating entity tags from the UI,
    as it handles additions and removals in a single operation.

    Tags that don't exist will be auto-created.

    **Cache Invalidation**: Clears all tag caches and entity caches
    """
    service = TagService()
    user_id = current_user.id if current_user else None

    tags = await service.set_entity_tags(
        entity_type=entity_type,
        entity_id=entity_id,
        tag_names=request.tag_names,
        user_id=user_id
    )

    tag_infos = [
        TagInfo(
            tag_id=tag.tag_id,
            name=tag.name,
            category=tag.category,
            color=tag.color,
            usage_count=tag.usage_count,
            created_at=tag.created_at.isoformat() if tag.created_at else None,
            updated_at=tag.updated_at.isoformat() if tag.updated_at else None
        )
        for tag in tags
    ]

    return EntityTagsResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        tags=tag_infos
    )


@router.delete("/entity/{entity_type}/{entity_id}/{tag_id}")
@invalidates_cache(entity_types=["tags"])
async def untag_entity(
    entity_type: str,
    entity_id: str,
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Remove a tag from an entity.

    **Cache Invalidation**: Clears all tag caches and entity caches
    """
    service = TagService()

    # Get tag to find its name
    tag = await service.repository.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")

    removed_count = await service.untag_entity(
        entity_type=entity_type,
        entity_id=entity_id,
        tag_names=[tag.name]
    )

    if removed_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Tag {tag_id} not found on {entity_type} {entity_id}"
        )

    return {"message": f"Tag {tag.name} removed from {entity_type} {entity_id}"}
