"""
Story Routes

Endpoints for listing and managing generated stories.
Stories are created by workflows, these routes are for retrieval and management.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from api.services.story_service_db import StoryServiceDB
from api.services.tag_service import TagService
from api.database import get_db
from api.models.auth import User
from api.models.responses import TagInfo
from api.dependencies.auth import get_current_active_user
from api.logging_config import get_logger
from api.middleware.cache import cached, invalidates_cache

router = APIRouter()
logger = get_logger(__name__)


class StoryInfo(BaseModel):
    """Story information response"""
    story_id: str
    title: str
    content: str
    character_id: Optional[str] = None
    theme: Optional[str] = None
    story_type: Optional[str] = None
    word_count: int
    metadata: dict
    tags: List[TagInfo] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    archived: bool = False
    archived_at: Optional[str] = None
    scenes: list = []


class StoryListResponse(BaseModel):
    """Story list response"""
    count: int
    stories: list[StoryInfo]


# Helper Functions
async def get_entity_tags_info(
    db: AsyncSession,
    entity_type: str,
    entity_id: str
) -> List[TagInfo]:
    """
    Helper function to fetch tags for an entity and convert to TagInfo response objects.
    """
    tag_service = TagService(db_session=db)
    tags = await tag_service.get_entity_tags(entity_type, entity_id)

    return [
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


@router.get("/", response_model=StoryListResponse)
@cached(cache_type="list", include_user=True)
async def list_stories(
    request: Request,
    limit: Optional[int] = Query(None, description="Maximum number of stories to return"),
    offset: int = Query(0, description="Number of stories to skip"),
    include_archived: bool = Query(False, description="Include archived stories"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all stories

    Returns a list of generated stories with their metadata.
    Supports pagination via limit/offset parameters.

    **Cached**: 60 seconds (user-specific)
    """
    service = StoryServiceDB(db, user_id=current_user.id if current_user else None)

    # Get both stories and total count
    stories = await service.list_stories(limit=limit, offset=offset, include_archived=include_archived)
    total_count = await service.count_stories(include_archived=include_archived)

    # Fetch tags for each story
    story_infos = []
    for story in stories:
        tags_info = await get_entity_tags_info(db, "story", story['story_id'])
        story_infos.append(
            StoryInfo(
                story_id=story['story_id'],
                title=story['title'],
                content=story['content'],
                character_id=story.get('character_id'),
                theme=story.get('theme'),
                story_type=story.get('story_type'),
                word_count=story['word_count'],
                metadata=story.get('metadata', {}),
                tags=tags_info,
                created_at=story.get('created_at'),
                updated_at=story.get('updated_at'),
                archived=story.get('archived', False),
                archived_at=story.get('archived_at'),
                scenes=story.get('scenes', [])
            )
        )

    return StoryListResponse(
        count=total_count,
        stories=story_infos
    )


@router.get("/{story_id}", response_model=StoryInfo)
@cached(cache_type="detail", include_user=True)
async def get_story(
    request: Request,
    story_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a story by ID

    Returns full story data including all scenes and illustrations.

    **Cached**: 5 minutes (user-specific)
    """
    service = StoryServiceDB(db, user_id=current_user.id if current_user else None)
    story_data = await service.get_story(story_id)

    if not story_data:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

    tags_info = await get_entity_tags_info(db, "story", story_id)

    return StoryInfo(
        story_id=story_data['story_id'],
        title=story_data['title'],
        content=story_data['content'],
        character_id=story_data.get('character_id'),
        theme=story_data.get('theme'),
        story_type=story_data.get('story_type'),
        word_count=story_data['word_count'],
        metadata=story_data.get('metadata', {}),
        tags=tags_info,
        created_at=story_data.get('created_at'),
        updated_at=story_data.get('updated_at'),
        archived=story_data.get('archived', False),
        archived_at=story_data.get('archived_at'),
        scenes=story_data.get('scenes', [])
    )


@router.post("/{story_id}/archive")
@invalidates_cache(entity_types=["stories"])
async def archive_story(
    story_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Archive a story

    Hides the story from default listings. Archived stories can be restored later.

    **Cache Invalidation**: Clears all story caches
    """
    service = StoryServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.archive_story(story_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

    return {"message": f"Story {story_id} archived successfully", "archived": True}


@router.post("/{story_id}/unarchive")
@invalidates_cache(entity_types=["stories"])
async def unarchive_story(
    story_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Unarchive a story

    Restores an archived story to active status.

    **Cache Invalidation**: Clears all story caches
    """
    service = StoryServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.unarchive_story(story_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

    return {"message": f"Story {story_id} restored successfully", "archived": False}


@router.delete("/{story_id}")
@invalidates_cache(entity_types=["stories"])
async def delete_story(
    story_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Archive a story (soft delete)

    Archives the story instead of permanently deleting it.
    Archived stories are hidden from default listings but can be restored.

    **Cache Invalidation**: Clears all story caches
    """
    service = StoryServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.delete_story(story_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

    return {"message": f"Story {story_id} archived successfully"}
