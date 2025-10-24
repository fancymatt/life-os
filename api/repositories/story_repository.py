"""
Story Repository

Handles database operations for Story and StoryScene entities.
Provides clean separation between business logic and data access.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models.db import Story, StoryScene
from api.logging_config import get_logger

logger = get_logger(__name__)


class StoryRepository:
    """Repository for Story database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, story_id: str) -> Optional[Story]:
        """Get story by ID with all scenes loaded"""
        result = await self.session.execute(
            select(Story)
            .where(Story.story_id == story_id)
            .options(selectinload(Story.scenes))
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        user_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Story]:
        """Get all stories, optionally filtered by user with pagination support

        Args:
            user_id: Filter by user ID
            limit: Maximum number of results
            offset: Number of results to skip
            include_archived: If True, include archived stories. Default False.
        """
        query = select(Story).order_by(Story.created_at.desc())

        if user_id is not None:
            query = query.where(Story.user_id == user_id)

        # Exclude archived by default
        if not include_archived:
            query = query.where(Story.archived == False)

        if limit is not None:
            query = query.limit(limit)

        query = query.offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, story: Story) -> Story:
        """Create new story"""
        self.session.add(story)
        await self.session.flush()  # Get the ID without committing

        logger.info(f"Created story in database: {story.title} ({story.story_id})")
        return story

    async def create_scene(self, scene: StoryScene) -> StoryScene:
        """Create new story scene"""
        self.session.add(scene)
        await self.session.flush()

        logger.info(f"Created story scene in database: {scene.title} (scene {scene.scene_number})")
        return scene

    async def update(self, story: Story) -> Story:
        """Update existing story"""
        await self.session.merge(story)
        await self.session.flush()

        logger.info(f"Updated story in database: {story.title} ({story.story_id})")
        return story

    async def delete(self, story_id: str) -> bool:
        """Archive story by ID (soft delete)"""
        return await self.archive(story_id)

    async def archive(self, story_id: str) -> bool:
        """Archive story by ID (soft delete)"""
        story = await self.get_by_id(story_id)

        if not story:
            return False

        story.archived = True
        story.archived_at = datetime.utcnow()
        await self.session.flush()

        logger.info(f"Archived story in database: {story_id}")
        return True

    async def unarchive(self, story_id: str) -> bool:
        """Unarchive story by ID"""
        story = await self.get_by_id(story_id)

        if not story:
            return False

        story.archived = False
        story.archived_at = None
        await self.session.flush()

        logger.info(f"Unarchived story in database: {story_id}")
        return True

    async def search(
        self,
        query: Optional[str] = None,
        user_id: Optional[int] = None,
        character_id: Optional[str] = None,
        theme: Optional[str] = None,
        include_archived: bool = False
    ) -> List[Story]:
        """
        Search stories with optional filters

        Args:
            query: Text search in title or content
            user_id: Filter by user ID
            character_id: Filter by character ID
            theme: Filter by theme
            include_archived: If True, include archived stories. Default False.
        """
        stmt = select(Story)

        if user_id is not None:
            stmt = stmt.where(Story.user_id == user_id)

        # Exclude archived by default
        if not include_archived:
            stmt = stmt.where(Story.archived == False)

        if character_id is not None:
            stmt = stmt.where(Story.character_id == character_id)

        if theme is not None:
            stmt = stmt.where(Story.theme == theme)

        if query:
            # Case-insensitive search in title or content
            search_filter = (
                Story.title.ilike(f"%{query}%") |
                Story.content.ilike(f"%{query}%")
            )
            stmt = stmt.where(search_filter)

        stmt = stmt.order_by(Story.created_at.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists(self, story_id: str) -> bool:
        """Check if story exists"""
        story = await self.get_by_id(story_id)
        return story is not None

    async def count(self, user_id: Optional[int] = None, include_archived: bool = False) -> int:
        """Count stories, optionally filtered by user

        Args:
            user_id: Filter by user ID
            include_archived: If True, include archived stories. Default False.
        """
        from sqlalchemy import func

        query = select(func.count()).select_from(Story)

        if user_id is not None:
            query = query.where(Story.user_id == user_id)

        # Exclude archived by default
        if not include_archived:
            query = query.where(Story.archived == False)

        result = await self.session.execute(query)
        return result.scalar_one()
