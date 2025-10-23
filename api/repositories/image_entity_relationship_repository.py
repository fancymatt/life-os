"""
Image Entity Relationship Repository

Handles database operations for ImageEntityRelationship entities (polymorphic joins).
"""

from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import ImageEntityRelationship, Image
from api.logging_config import get_logger

logger = get_logger(__name__)


class ImageEntityRelationshipRepository:
    """Repository for ImageEntityRelationship database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, relationship_id: int) -> Optional[ImageEntityRelationship]:
        """Get relationship by ID"""
        result = await self.session.execute(
            select(ImageEntityRelationship).where(ImageEntityRelationship.id == relationship_id)
        )
        return result.scalar_one_or_none()

    async def get_by_image(self, image_id: str) -> List[ImageEntityRelationship]:
        """Get all entity relationships for an image"""
        result = await self.session.execute(
            select(ImageEntityRelationship)
            .where(ImageEntityRelationship.image_id == image_id)
            .order_by(ImageEntityRelationship.created_at)
        )
        return list(result.scalars().all())

    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ImageEntityRelationship]:
        """
        Get all relationships for a specific entity

        This is used for entity galleries: "show me all images that used this character"
        """
        query = (
            select(ImageEntityRelationship)
            .where(and_(
                ImageEntityRelationship.entity_type == entity_type,
                ImageEntityRelationship.entity_id == entity_id
            ))
            .order_by(ImageEntityRelationship.created_at.desc())
        )

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_images_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Image]:
        """
        Get all images that used a specific entity

        This is the main method for entity galleries. Returns actual Image objects,
        not just relationships.
        """
        query = (
            select(Image)
            .join(ImageEntityRelationship, Image.image_id == ImageEntityRelationship.image_id)
            .where(and_(
                ImageEntityRelationship.entity_type == entity_type,
                ImageEntityRelationship.entity_id == entity_id
            ))
            .order_by(Image.created_at.desc())
        )

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, relationship: ImageEntityRelationship) -> ImageEntityRelationship:
        """Create new relationship"""
        self.session.add(relationship)
        await self.session.flush()

        logger.info(f"Created image-entity relationship: {relationship.image_id} -> {relationship.entity_type}:{relationship.entity_id}")
        return relationship

    async def create_many(self, relationships: List[ImageEntityRelationship]) -> List[ImageEntityRelationship]:
        """Create multiple relationships in bulk"""
        self.session.add_all(relationships)
        await self.session.flush()

        logger.info(f"Created {len(relationships)} image-entity relationships")
        return relationships

    async def delete(self, relationship_id: int) -> bool:
        """Delete relationship by ID"""
        relationship = await self.get_by_id(relationship_id)

        if not relationship:
            return False

        await self.session.delete(relationship)
        await self.session.flush()

        logger.info(f"Deleted image-entity relationship: {relationship_id}")
        return True

    async def delete_by_image(self, image_id: str) -> int:
        """
        Delete all relationships for an image

        Returns count of deleted relationships
        """
        relationships = await self.get_by_image(image_id)
        count = len(relationships)

        for rel in relationships:
            await self.session.delete(rel)

        await self.session.flush()
        logger.info(f"Deleted {count} relationships for image: {image_id}")
        return count

    async def count_by_entity(self, entity_type: str, entity_id: str) -> int:
        """Count how many images used a specific entity"""
        query = select(func.count()).select_from(ImageEntityRelationship).where(and_(
            ImageEntityRelationship.entity_type == entity_type,
            ImageEntityRelationship.entity_id == entity_id
        ))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def exists(
        self,
        image_id: str,
        entity_type: str,
        entity_id: str,
        role: Optional[str] = None
    ) -> bool:
        """Check if a specific relationship exists"""
        query = select(ImageEntityRelationship).where(and_(
            ImageEntityRelationship.image_id == image_id,
            ImageEntityRelationship.entity_type == entity_type,
            ImageEntityRelationship.entity_id == entity_id
        ))

        if role is not None:
            query = query.where(ImageEntityRelationship.role == role)

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
