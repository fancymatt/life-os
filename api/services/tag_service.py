"""
Tag Service - Business logic layer for tag operations

This service handles:
- Tag creation with validation
- Tag suggestion and auto-creation
- Entity tagging workflows
- Tag merging and cleanup
- Usage statistics and insights
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from api.repositories.tag_repository import TagRepository
from api.models.db import Tag, EntityTag
from api.logging_config import get_logger
from fastapi import HTTPException
import re

logger = get_logger(__name__)


class TagService:
    """Service for tag business logic"""

    def __init__(self, db_session: Optional['AsyncSession'] = None):
        """
        Initialize TagService with optional database session.

        Args:
            db_session: Optional database session for transactional consistency
        """
        self.repository = TagRepository(db_session=db_session)

        # Common tag categories
        self.CATEGORIES = [
            "material",  # leather, cotton, silk, wool
            "style",  # casual, formal, vintage, modern
            "season",  # winter, summer, spring, fall
            "genre",  # fantasy, scifi, horror, romance
            "color",  # red, blue, green (if not using color field)
            "mood",  # happy, sad, dramatic, peaceful
            "setting",  # urban, nature, indoor, outdoor
            "character",  # protagonist, villain, hero
            "custom"  # user-defined
        ]

        # Common system tags (auto-created)
        self.SYSTEM_TAGS = {
            "favorite": {"category": "custom", "color": "#FFD700"},
            "draft": {"category": "custom", "color": "#FFA500"},
            "needs-review": {"category": "custom", "color": "#FF6B6B"},
            "approved": {"category": "custom", "color": "#51CF66"},
            "archived": {"category": "custom", "color": "#868E96"},
        }

    # ========== Tag CRUD with Validation ==========

    async def create_tag(
        self,
        name: str,
        category: Optional[str] = None,
        color: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tag:
        """
        Create a new tag with validation.

        Args:
            name: Tag name (will be normalized)
            category: Optional category (validated against known categories)
            color: Optional hex color (validated)
            user_id: Optional user ID (None for system tags)

        Returns:
            Created Tag object

        Raises:
            HTTPException: If validation fails or tag already exists
        """
        # Normalize name (lowercase, trim, remove extra spaces)
        normalized_name = self._normalize_tag_name(name)

        if not normalized_name:
            raise HTTPException(status_code=400, detail="Tag name cannot be empty")

        if len(normalized_name) > 100:
            raise HTTPException(status_code=400, detail="Tag name too long (max 100 characters)")

        # Check if tag already exists
        existing = await self.repository.get_tag_by_name(normalized_name)
        if existing:
            logger.info(f"Tag already exists: {normalized_name} (returning existing)")
            return existing

        # Validate category
        if category and category not in self.CATEGORIES:
            logger.warning(f"Unknown category: {category}, using 'custom'")
            category = "custom"

        # Validate color (hex format)
        if color:
            color = self._validate_color(color)

        # Create tag
        tag = await self.repository.create_tag(
            name=normalized_name,
            category=category,
            color=color,
            user_id=user_id
        )

        logger.info(f"Created tag: {normalized_name} (id: {tag.tag_id})")
        return tag

    async def get_or_create_tag(
        self,
        name: str,
        category: Optional[str] = None,
        color: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tag:
        """
        Get existing tag or create if doesn't exist.

        This is the preferred method for applying tags from user input,
        as it handles both existing and new tags transparently.
        """
        normalized_name = self._normalize_tag_name(name)

        existing = await self.repository.get_tag_by_name(normalized_name)
        if existing:
            return existing

        return await self.create_tag(normalized_name, category, color, user_id)

    async def list_tags(
        self,
        category: Optional[str] = None,
        user_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Tag]:
        """List tags with filters"""
        return await self.repository.list_tags(
            category=category,
            user_id=user_id,
            search=search,
            limit=limit,
            offset=offset
        )

    async def update_tag(
        self,
        tag_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        color: Optional[str] = None
    ) -> Tag:
        """Update tag with validation"""
        # Normalize and validate inputs
        if name:
            name = self._normalize_tag_name(name)
            if not name:
                raise HTTPException(status_code=400, detail="Tag name cannot be empty")

        if category and category not in self.CATEGORIES:
            logger.warning(f"Unknown category: {category}, using 'custom'")
            category = "custom"

        if color:
            color = self._validate_color(color)

        tag = await self.repository.update_tag(tag_id, name, category, color)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        return tag

    async def delete_tag(self, tag_id: str) -> bool:
        """Delete tag and all relationships"""
        deleted = await self.repository.delete_tag(tag_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Tag not found")

        logger.info(f"Deleted tag: {tag_id}")
        return True

    # ========== Entity Tagging Workflows ==========

    async def tag_entity(
        self,
        entity_type: str,
        entity_id: str,
        tag_names: List[str],
        user_id: Optional[int] = None,
        auto_create: bool = True
    ) -> List[Tag]:
        """
        Tag an entity with one or more tags.

        Args:
            entity_type: Type of entity (character, clothing_item, etc.)
            entity_id: Entity ID
            tag_names: List of tag names (will be normalized)
            user_id: Optional user ID for creating new tags
            auto_create: Auto-create tags that don't exist

        Returns:
            List of Tag objects now on the entity
        """
        tags = []

        for tag_name in tag_names:
            # Get or create tag
            if auto_create:
                tag = await self.get_or_create_tag(tag_name, user_id=user_id)
            else:
                tag = await self.repository.get_tag_by_name(tag_name)
                if not tag:
                    logger.warning(f"Tag not found: {tag_name} (skipping)")
                    continue

            # Add tag to entity
            await self.repository.add_tag_to_entity(entity_type, entity_id, tag.tag_id)
            tags.append(tag)

        logger.info(f"Tagged {entity_type}:{entity_id} with {len(tags)} tags")
        return tags

    async def untag_entity(
        self,
        entity_type: str,
        entity_id: str,
        tag_names: List[str]
    ) -> int:
        """
        Remove tags from entity.

        Returns:
            Number of tags removed
        """
        removed_count = 0

        for tag_name in tag_names:
            tag = await self.repository.get_tag_by_name(tag_name)
            if not tag:
                logger.warning(f"Tag not found: {tag_name} (skipping)")
                continue

            removed = await self.repository.remove_tag_from_entity(
                entity_type, entity_id, tag.tag_id
            )
            if removed:
                removed_count += 1

        logger.info(f"Removed {removed_count} tags from {entity_type}:{entity_id}")
        return removed_count

    async def set_entity_tags(
        self,
        entity_type: str,
        entity_id: str,
        tag_names: List[str],
        user_id: Optional[int] = None
    ) -> List[Tag]:
        """
        Replace all tags on entity with new set.

        This is the preferred method for updating entity tags from the UI,
        as it handles additions and removals in a single operation.
        """
        # Get or create all tags
        tags = []
        for tag_name in tag_names:
            tag = await self.get_or_create_tag(tag_name, user_id=user_id)
            tags.append(tag)

        # Set tags on entity (replaces all existing)
        tag_ids = [tag.tag_id for tag in tags]
        return await self.repository.set_entity_tags(entity_type, entity_id, tag_ids)

    async def get_entity_tags(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[Tag]:
        """Get all tags for an entity"""
        return await self.repository.get_entity_tags(entity_type, entity_id)

    # ========== Search and Discovery ==========

    async def autocomplete(
        self,
        query: str,
        category: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Autocomplete tag search for UI.

        Returns:
            List of tag suggestions with usage counts
        """
        tags = await self.repository.autocomplete_tags(
            query=query,
            category=category,
            user_id=user_id,
            limit=limit
        )

        return [
            {
                "tag_id": tag.tag_id,
                "name": tag.name,
                "category": tag.category,
                "color": tag.color,
                "usage_count": tag.usage_count
            }
            for tag in tags
        ]

    async def suggest_tags(
        self,
        entity_type: str,
        entity_description: Optional[str] = None,
        limit: int = 10
    ) -> List[Tag]:
        """
        Suggest relevant tags based on entity type and description.

        This is a placeholder for future AI-powered tag suggestions.
        Currently returns most popular tags for the entity type.

        Args:
            entity_type: Type of entity
            entity_description: Optional description for AI analysis
            limit: Max suggestions

        Returns:
            List of suggested tags
        """
        # TODO: Implement AI-powered tag suggestions
        # For now, return most popular tags
        tags = await self.repository.list_tags(
            limit=limit,
            order_by="usage_count"
        )

        logger.info(f"Suggested {len(tags)} tags for {entity_type}")
        return tags

    async def find_related_entities(
        self,
        entity_type: str,
        entity_id: str,
        min_shared_tags: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Find entities with shared tags.

        Args:
            entity_type: Entity type
            entity_id: Entity ID
            min_shared_tags: Minimum number of shared tags

        Returns:
            List of related entities with shared tag count
        """
        # Get tags for this entity
        entity_tags = await self.get_entity_tags(entity_type, entity_id)

        if not entity_tags:
            return []

        # Find other entities with these tags
        related = {}  # entity_id -> {entity_type, shared_tags}

        for tag in entity_tags:
            entities = await self.repository.get_entities_by_tag(
                tag.tag_id,
                entity_type=entity_type
            )

            for entity in entities:
                eid = entity["entity_id"]
                if eid == entity_id:
                    continue  # Skip self

                if eid not in related:
                    related[eid] = {
                        "entity_type": entity["entity_type"],
                        "entity_id": eid,
                        "shared_tags": []
                    }

                related[eid]["shared_tags"].append(tag.name)

        # Filter by minimum shared tags and sort by shared count
        filtered = [
            {**info, "shared_count": len(info["shared_tags"])}
            for info in related.values()
            if len(info["shared_tags"]) >= min_shared_tags
        ]

        filtered.sort(key=lambda x: x["shared_count"], reverse=True)

        logger.info(f"Found {len(filtered)} related entities for {entity_type}:{entity_id}")
        return filtered

    # ========== Statistics and Insights ==========

    async def get_statistics(self) -> Dict[str, Any]:
        """Get tag usage statistics"""
        return await self.repository.get_tag_statistics()

    async def cleanup_unused_tags(self, min_usage: int = 0) -> int:
        """
        Delete tags with usage count below threshold.

        Args:
            min_usage: Minimum usage count to keep (default: 0 = delete only unused)

        Returns:
            Number of tags deleted
        """
        # Get all tags
        all_tags = await self.repository.list_tags(limit=10000)

        deleted_count = 0
        for tag in all_tags:
            if tag.usage_count <= min_usage:
                await self.repository.delete_tag(tag.tag_id)
                deleted_count += 1

        logger.info(f"Cleaned up {deleted_count} unused tags")
        return deleted_count

    # ========== System Tags ==========

    async def ensure_system_tags(self) -> List[Tag]:
        """
        Ensure all system tags exist.

        Called on application startup to create default tags.
        """
        created = []

        for name, config in self.SYSTEM_TAGS.items():
            tag = await self.get_or_create_tag(
                name=name,
                category=config["category"],
                color=config["color"],
                user_id=None  # System-wide
            )
            created.append(tag)

        logger.info(f"Ensured {len(created)} system tags exist")
        return created

    # ========== Helper Methods ==========

    def _normalize_tag_name(self, name: str) -> str:
        """Normalize tag name (lowercase, trim, remove extra spaces)"""
        if not name:
            return ""

        # Remove leading/trailing whitespace
        name = name.strip()

        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name)

        # Lowercase
        name = name.lower()

        return name

    def _validate_color(self, color: str) -> str:
        """
        Validate and normalize hex color.

        Args:
            color: Color string (hex format with or without #)

        Returns:
            Normalized hex color (#RRGGBB format)

        Raises:
            HTTPException: If color format is invalid
        """
        # Remove # if present
        if color.startswith('#'):
            color = color[1:]

        # Validate hex format
        if not re.match(r'^[0-9A-Fa-f]{6}$', color):
            raise HTTPException(status_code=400, detail="Invalid color format (use #RRGGBB)")

        # Return with # prefix
        return f"#{color.upper()}"
