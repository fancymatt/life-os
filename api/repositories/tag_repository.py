"""
Tag Repository - Data access layer for tags and entity-tag relationships

This repository handles all database operations for tags including:
- CRUD operations for tags
- Entity-tag relationship management
- Tag search and autocomplete
- Usage tracking and statistics
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.db import Tag, EntityTag
from api.database import get_session
from api.logging_config import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)


class TagRepository:
    """Repository for tag and entity-tag database operations"""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize repository with optional database session.

        Args:
            db_session: Database session to use (if None, will create new sessions)
        """
        self.db_session = db_session

    async def _get_session(self):
        """Get database session (use provided or create new context manager)"""
        if self.db_session:
            yield self.db_session
        else:
            async with get_session() as session:
                yield session

    # ========== Tag CRUD Operations ==========

    async def create_tag(
        self,
        name: str,
        category: Optional[str] = None,
        color: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tag:
        """
        Create a new tag.

        Args:
            name: Tag name (unique)
            category: Optional category (material, style, season, genre, etc.)
            color: Optional color hex code
            user_id: Optional user ID (None for system-wide tags)

        Returns:
            Created Tag object
        """
        async for session in self._get_session():
            tag = Tag(
                tag_id=str(uuid.uuid4())[:8],  # Short UUID for tag_id
                name=name,
                category=category,
                color=color,
                usage_count=0,
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(tag)
            await session.commit()
            await session.refresh(tag)

            logger.info(f"Created tag: {name} (category: {category}, id: {tag.tag_id})")
            return tag

    async def get_tag_by_id(self, tag_id: str) -> Optional[Tag]:
        """Get tag by tag_id"""
        async for session in self._get_session():
            result = await session.execute(
                select(Tag).where(Tag.tag_id == tag_id)
            )
            return result.scalar_one_or_none()

    async def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get tag by name (case-insensitive)"""
        async for session in self._get_session():
            result = await session.execute(
                select(Tag).where(func.lower(Tag.name) == name.lower())
            )
            return result.scalar_one_or_none()

    async def list_tags(
        self,
        category: Optional[str] = None,
        user_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "usage_count"  # "usage_count", "name", "created_at"
    ) -> List[Tag]:
        """
        List tags with optional filters.

        Args:
            category: Filter by category
            user_id: Filter by user (None includes system-wide tags)
            search: Search query (partial name match)
            limit: Max results
            offset: Pagination offset
            order_by: Sort order (usage_count, name, created_at)

        Returns:
            List of Tag objects
        """
        async for session in self._get_session():
            query = select(Tag)

            # Apply filters
            filters = []
            if category:
                filters.append(Tag.category == category)
            if user_id is not None:
                # Include both user tags and system-wide tags (user_id is null)
                filters.append(or_(Tag.user_id == user_id, Tag.user_id.is_(None)))
            if search:
                filters.append(Tag.name.ilike(f"%{search}%"))

            if filters:
                query = query.where(and_(*filters))

            # Apply ordering
            if order_by == "usage_count":
                query = query.order_by(Tag.usage_count.desc(), Tag.name)
            elif order_by == "name":
                query = query.order_by(Tag.name)
            elif order_by == "created_at":
                query = query.order_by(Tag.created_at.desc())

            # Apply pagination
            query = query.limit(limit).offset(offset)

            result = await session.execute(query)
            return list(result.scalars().all())

    async def update_tag(
        self,
        tag_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        color: Optional[str] = None
    ) -> Optional[Tag]:
        """Update tag fields"""
        async for session in self._get_session():
            tag = await self.get_tag_by_id(tag_id)
            if not tag:
                return None

            if name is not None:
                tag.name = name
            if category is not None:
                tag.category = category
            if color is not None:
                tag.color = color

            tag.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(tag)

            logger.info(f"Updated tag: {tag_id}")
            return tag

    async def delete_tag(self, tag_id: str) -> bool:
        """
        Delete tag and all its entity relationships.

        Returns:
            True if deleted, False if not found
        """
        async for session in self._get_session():
            # Delete all entity-tag relationships first
            await session.execute(
                delete(EntityTag).where(EntityTag.tag_id == tag_id)
            )

            # Delete the tag
            result = await session.execute(
                delete(Tag).where(Tag.tag_id == tag_id)
            )

            await session.commit()

            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Deleted tag: {tag_id}")
            return deleted

    # ========== Entity-Tag Relationship Operations ==========

    async def add_tag_to_entity(
        self,
        entity_type: str,
        entity_id: str,
        tag_id: str
    ) -> EntityTag:
        """
        Add tag to entity (creates relationship).

        Args:
            entity_type: Type of entity (character, clothing_item, etc.)
            entity_id: Entity ID
            tag_id: Tag ID

        Returns:
            Created EntityTag object
        """
        async for session in self._get_session():
            # Check if relationship already exists
            existing = await session.execute(
                select(EntityTag).where(
                    and_(
                        EntityTag.entity_type == entity_type,
                        EntityTag.entity_id == entity_id,
                        EntityTag.tag_id == tag_id
                    )
                )
            )

            if existing.scalar_one_or_none():
                logger.warning(f"Tag {tag_id} already applied to {entity_type}:{entity_id}")
                return existing.scalar_one()

            # Create relationship
            entity_tag = EntityTag(
                entity_type=entity_type,
                entity_id=entity_id,
                tag_id=tag_id,
                created_at=datetime.utcnow()
            )

            session.add(entity_tag)

            # Increment usage count on tag
            tag = await self.get_tag_by_id(tag_id)
            if tag:
                tag.usage_count += 1
                tag.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(entity_tag)

            logger.info(f"Added tag {tag_id} to {entity_type}:{entity_id}")
            return entity_tag

    async def remove_tag_from_entity(
        self,
        entity_type: str,
        entity_id: str,
        tag_id: str
    ) -> bool:
        """
        Remove tag from entity (deletes relationship).

        Returns:
            True if removed, False if not found
        """
        async for session in self._get_session():
            result = await session.execute(
                delete(EntityTag).where(
                    and_(
                        EntityTag.entity_type == entity_type,
                        EntityTag.entity_id == entity_id,
                        EntityTag.tag_id == tag_id
                    )
                )
            )

            # Decrement usage count on tag
            if result.rowcount > 0:
                tag = await self.get_tag_by_id(tag_id)
                if tag and tag.usage_count > 0:
                    tag.usage_count -= 1
                    tag.updated_at = datetime.utcnow()

            await session.commit()

            removed = result.rowcount > 0
            if removed:
                logger.info(f"Removed tag {tag_id} from {entity_type}:{entity_id}")
            return removed

    async def get_entity_tags(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[Tag]:
        """
        Get all tags for an entity.

        Returns:
            List of Tag objects
        """
        async for session in self._get_session():
            # Join EntityTag with Tag to get full tag info
            result = await session.execute(
                select(Tag)
                .join(EntityTag, Tag.tag_id == EntityTag.tag_id)
                .where(
                    and_(
                        EntityTag.entity_type == entity_type,
                        EntityTag.entity_id == entity_id
                    )
                )
                .order_by(Tag.name)
            )
            return list(result.scalars().all())

    async def get_entities_by_tag(
        self,
        tag_id: str,
        entity_type: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get all entities with a specific tag.

        Args:
            tag_id: Tag ID
            entity_type: Optional entity type filter

        Returns:
            List of dicts with entity_type and entity_id
        """
        async for session in self._get_session():
            query = select(EntityTag.entity_type, EntityTag.entity_id).where(
                EntityTag.tag_id == tag_id
            )

            if entity_type:
                query = query.where(EntityTag.entity_type == entity_type)

            result = await session.execute(query)
            return [
                {"entity_type": row[0], "entity_id": row[1]}
                for row in result.all()
            ]

    async def set_entity_tags(
        self,
        entity_type: str,
        entity_id: str,
        tag_ids: List[str]
    ) -> List[Tag]:
        """
        Replace all tags for an entity with new set.

        Args:
            entity_type: Entity type
            entity_id: Entity ID
            tag_ids: List of tag IDs to set

        Returns:
            List of Tag objects now on the entity
        """
        async for session in self._get_session():
            # Remove all existing tags
            await session.execute(
                delete(EntityTag).where(
                    and_(
                        EntityTag.entity_type == entity_type,
                        EntityTag.entity_id == entity_id
                    )
                )
            )

            # Add new tags
            for tag_id in tag_ids:
                await self.add_tag_to_entity(entity_type, entity_id, tag_id)

            # Return final tag list
            return await self.get_entity_tags(entity_type, entity_id)

    # ========== Search and Statistics ==========

    async def autocomplete_tags(
        self,
        query: str,
        category: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Tag]:
        """
        Autocomplete tag search (for UI tag input).

        Args:
            query: Partial tag name
            category: Optional category filter
            user_id: Optional user filter
            limit: Max results

        Returns:
            List of matching tags sorted by usage count
        """
        return await self.list_tags(
            category=category,
            user_id=user_id,
            search=query,
            limit=limit,
            order_by="usage_count"
        )

    async def get_tag_statistics(self) -> Dict[str, Any]:
        """
        Get tag usage statistics.

        Returns:
            Dict with total_tags, total_relationships, top_tags, etc.
        """
        async for session in self._get_session():
            # Total tags
            total_tags_result = await session.execute(select(func.count(Tag.id)))
            total_tags = total_tags_result.scalar()

            # Total entity-tag relationships
            total_rels_result = await session.execute(select(func.count(EntityTag.id)))
            total_relationships = total_rels_result.scalar()

            # Top tags by usage
            top_tags_result = await session.execute(
                select(Tag).order_by(Tag.usage_count.desc()).limit(20)
            )
            top_tags = [
                {"tag_id": tag.tag_id, "name": tag.name, "usage_count": tag.usage_count}
                for tag in top_tags_result.scalars().all()
            ]

            # Tags by category
            category_result = await session.execute(
                select(Tag.category, func.count(Tag.id))
                .group_by(Tag.category)
                .order_by(func.count(Tag.id).desc())
            )
            tags_by_category = {
                row[0] or "uncategorized": row[1]
                for row in category_result.all()
            }

            return {
                "total_tags": total_tags,
                "total_relationships": total_relationships,
                "top_tags": top_tags,
                "tags_by_category": tags_by_category
            }
