"""
Story Service (PostgreSQL)

Database-backed implementation of story service using PostgreSQL.
Handles story and story scene persistence.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import Story, StoryScene
from api.repositories import StoryRepository
from api.logging_config import get_logger

logger = get_logger(__name__)


class StoryServiceDB:
    """PostgreSQL-based story service"""

    def __init__(self, session: AsyncSession, user_id: Optional[int] = None):
        """
        Initialize story service with database session

        Args:
            session: SQLAlchemy async session
            user_id: Optional user ID for filtering
        """
        self.session = session
        self.user_id = user_id
        self.repository = StoryRepository(session)

    def _story_to_dict(self, story: Story) -> Dict[str, Any]:
        """Convert Story model to dict"""
        return {
            "story_id": story.story_id,
            "title": story.title,
            "content": story.content,
            "character_id": story.character_id,
            "theme": story.theme,
            "story_type": story.story_type,
            "word_count": story.word_count,
            "metadata": story.meta,  # Note: 'meta' in DB, 'metadata' in API
            "created_at": story.created_at.isoformat() if story.created_at else None,
            "updated_at": story.updated_at.isoformat() if story.updated_at else None,
            "archived": story.archived,
            "archived_at": story.archived_at.isoformat() if story.archived_at else None,
            "scenes": [self._scene_to_dict(scene) for scene in story.scenes] if story.scenes else []
        }

    def _scene_to_dict(self, scene: StoryScene) -> Dict[str, Any]:
        """Convert StoryScene model to dict"""
        return {
            "scene_id": scene.scene_id,
            "story_id": scene.story_id,
            "scene_number": scene.scene_number,
            "title": scene.title,
            "content": scene.content,
            "action": scene.action,
            "illustration_prompt": scene.illustration_prompt,
            "illustration_url": scene.illustration_url,
            "metadata": scene.meta,  # Note: 'meta' in DB, 'metadata' in API
            "created_at": scene.created_at.isoformat() if scene.created_at else None,
            "archived": scene.archived,
            "archived_at": scene.archived_at.isoformat() if scene.archived_at else None
        }

    async def create_story(
        self,
        title: str,
        content: str,
        scenes: Optional[List[Dict[str, Any]]] = None,
        character_id: Optional[str] = None,
        theme: Optional[str] = None,
        story_type: Optional[str] = None,
        word_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new story in database

        Args:
            title: Story title
            content: Full story text
            scenes: Optional list of scene dicts
            character_id: Optional character ID
            theme: Optional story theme
            story_type: Optional story type (normal, transformation, outfit)
            word_count: Word count
            metadata: Additional metadata

        Returns:
            Story data dict
        """
        story_id = str(uuid.uuid4())[:8]

        story = Story(
            story_id=story_id,
            title=title,
            content=content,
            character_id=character_id,
            theme=theme,
            story_type=story_type,
            word_count=word_count,
            meta=metadata or {},  # Note: 'meta' in DB
            user_id=self.user_id
        )

        story = await self.repository.create(story)

        # Create scenes if provided
        if scenes:
            for scene_data in scenes:
                scene_id = str(uuid.uuid4())[:8]
                scene = StoryScene(
                    scene_id=scene_id,
                    story_id=story_id,
                    scene_number=scene_data.get('scene_number', 0),
                    title=scene_data.get('title', ''),
                    content=scene_data.get('content', ''),
                    action=scene_data.get('action'),
                    illustration_prompt=scene_data.get('illustration_prompt'),
                    illustration_url=scene_data.get('illustration_url'),
                    meta=scene_data.get('metadata', {})
                )
                await self.repository.create_scene(scene)

        await self.session.commit()

        # Refresh to get scenes
        story = await self.repository.get_by_id(story_id)
        return self._story_to_dict(story)

    async def create_story_from_workflow_result(
        self,
        workflow_result: Dict[str, Any],
        character_id: Optional[str] = None,
        theme: Optional[str] = None,
        story_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a story from workflow execution result

        Args:
            workflow_result: Result from story generation workflow
            character_id: Optional character ID
            theme: Optional theme
            story_type: Optional story type

        Returns:
            Story data dict
        """
        # Extract story data from workflow result
        title = workflow_result.get('title', 'Untitled Story')
        content = workflow_result.get('content', '')
        word_count = len(content.split()) if content else 0

        # Extract scenes
        scenes_data = workflow_result.get('scenes', [])
        scenes = []
        for idx, scene_data in enumerate(scenes_data):
            scenes.append({
                'scene_number': idx + 1,
                'title': scene_data.get('title', f'Scene {idx + 1}'),
                'content': scene_data.get('content', ''),
                'action': scene_data.get('action'),
                'illustration_prompt': scene_data.get('illustration_prompt'),
                'illustration_url': scene_data.get('illustration_url'),
                'metadata': scene_data.get('metadata', {})
            })

        # Store workflow metadata
        metadata = {
            'workflow_id': workflow_result.get('workflow_id'),
            'generation_params': workflow_result.get('generation_params', {}),
            'generated_at': datetime.utcnow().isoformat()
        }

        return await self.create_story(
            title=title,
            content=content,
            scenes=scenes,
            character_id=character_id,
            theme=theme,
            story_type=story_type,
            word_count=word_count,
            metadata=metadata
        )

    async def get_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a story by ID

        Args:
            story_id: Story ID

        Returns:
            Story data dict or None if not found
        """
        story = await self.repository.get_by_id(story_id)

        if not story:
            return None

        # Filter by user if specified
        if self.user_id and story.user_id != self.user_id:
            return None

        return self._story_to_dict(story)

    async def list_stories(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all stories (filtered by user if specified)

        Args:
            limit: Maximum number of stories to return
            offset: Number of stories to skip
            include_archived: If True, include archived stories. Default False.

        Returns:
            List of story data dicts
        """
        stories = await self.repository.get_all(
            user_id=self.user_id,
            limit=limit,
            offset=offset,
            include_archived=include_archived
        )
        return [self._story_to_dict(story) for story in stories]

    async def update_story(
        self,
        story_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        character_id: Optional[str] = None,
        theme: Optional[str] = None,
        story_type: Optional[str] = None,
        word_count: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a story

        Args:
            story_id: Story ID
            title: New title (optional)
            content: New content (optional)
            character_id: New character ID (optional)
            theme: New theme (optional)
            story_type: New story type (optional)
            word_count: New word count (optional)
            metadata: New metadata (optional)

        Returns:
            Updated story data dict or None if not found
        """
        story = await self.repository.get_by_id(story_id)

        if not story:
            return None

        # Check user permission
        if self.user_id and story.user_id != self.user_id:
            return None

        # Update fields if provided
        if title is not None:
            story.title = title
        if content is not None:
            story.content = content
        if character_id is not None:
            story.character_id = character_id
        if theme is not None:
            story.theme = theme
        if story_type is not None:
            story.story_type = story_type
        if word_count is not None:
            story.word_count = word_count
        if metadata is not None:
            story.meta.update(metadata)  # Note: 'meta' in DB

        story.updated_at = datetime.utcnow()

        story = await self.repository.update(story)
        await self.session.commit()

        return self._story_to_dict(story)

    async def delete_story(self, story_id: str) -> bool:
        """
        Delete a story (soft delete - archives it)

        Args:
            story_id: Story ID

        Returns:
            True if deleted, False if not found
        """
        return await self.archive_story(story_id)

    async def archive_story(self, story_id: str) -> bool:
        """
        Archive a story (soft delete)

        Args:
            story_id: Story ID

        Returns:
            True if archived, False if not found or permission denied
        """
        story = await self.repository.get_by_id(story_id)

        if not story:
            return False

        # Check user permission
        if self.user_id and story.user_id != self.user_id:
            return False

        success = await self.repository.archive(story_id)

        if success:
            await self.session.commit()

        return success

    async def unarchive_story(self, story_id: str) -> bool:
        """
        Unarchive a story

        Args:
            story_id: Story ID

        Returns:
            True if unarchived, False if not found or permission denied
        """
        story = await self.repository.get_by_id(story_id)

        if not story:
            return False

        # Check user permission
        if self.user_id and story.user_id != self.user_id:
            return False

        success = await self.repository.unarchive(story_id)

        if success:
            await self.session.commit()

        return success

    async def search_stories(
        self,
        query: Optional[str] = None,
        character_id: Optional[str] = None,
        theme: Optional[str] = None,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search stories with filters

        Args:
            query: Text search query
            character_id: Filter by character ID
            theme: Filter by theme
            include_archived: If True, include archived stories. Default False.

        Returns:
            List of matching story data dicts
        """
        stories = await self.repository.search(
            query=query,
            user_id=self.user_id,
            character_id=character_id,
            theme=theme,
            include_archived=include_archived
        )

        return [self._story_to_dict(story) for story in stories]

    async def count_stories(self, include_archived: bool = False) -> int:
        """
        Count total stories (filtered by user if specified)

        Args:
            include_archived: If True, include archived stories. Default False.

        Returns:
            Total number of stories
        """
        return await self.repository.count(user_id=self.user_id, include_archived=include_archived)
