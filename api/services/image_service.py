"""
Image Service

Handles business logic for generated images and their relationships to entities.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import Image, ImageEntityRelationship
from api.repositories import ImageRepository, ImageEntityRelationshipRepository
from api.logging_config import get_logger

logger = get_logger(__name__)


class ImageService:
    """Service for managing generated images"""

    def __init__(self, session: AsyncSession, user_id: Optional[int] = None):
        """
        Initialize image service with database session

        Args:
            session: SQLAlchemy async session
            user_id: Optional user ID for filtering
        """
        self.session = session
        self.user_id = user_id
        self.image_repository = ImageRepository(session)
        self.relationship_repository = ImageEntityRelationshipRepository(session)

    def _image_to_dict(self, image: Image) -> Dict[str, Any]:
        """Convert Image model to dict"""
        # Ensure file path starts with / for web access
        file_path = image.file_path
        if not file_path.startswith('/'):
            file_path = '/' + file_path

        return {
            "image_id": image.image_id,
            "file_path": file_path,
            "filename": image.filename,
            "width": image.width,
            "height": image.height,
            "generation_metadata": image.generation_metadata,
            "created_at": image.created_at.isoformat() if image.created_at else None,
            "user_id": image.user_id,
        }

    def _relationship_to_dict(self, rel: ImageEntityRelationship) -> Dict[str, Any]:
        """Convert ImageEntityRelationship model to dict"""
        return {
            "id": rel.id,
            "image_id": rel.image_id,
            "entity_type": rel.entity_type,
            "entity_id": rel.entity_id,
            "role": rel.role,
            "created_at": rel.created_at.isoformat() if rel.created_at else None,
        }

    async def create_image(
        self,
        file_path: str,
        generation_metadata: Optional[Dict[str, Any]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new image record

        Args:
            file_path: Path to the generated image file
            generation_metadata: Optional metadata about generation (model, params, etc.)
            width: Optional image width in pixels
            height: Optional image height in pixels

        Returns:
            Created image dict
        """
        image_id = str(uuid.uuid4())
        filename = Path(file_path).name

        image = Image(
            image_id=image_id,
            file_path=file_path,
            filename=filename,
            width=width,
            height=height,
            generation_metadata=generation_metadata or {},
            user_id=self.user_id
        )

        image = await self.image_repository.create(image)
        await self.session.commit()

        logger.info(f"Created image: {filename}", extra={'extra_fields': {
            'image_id': image_id,
            'file_path': file_path
        }})

        return self._image_to_dict(image)

    async def add_entity_relationships(
        self,
        image_id: str,
        entities: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Add multiple entity relationships to an image

        Args:
            image_id: UUID of the image
            entities: List of dicts with keys: entity_type, entity_id, role (optional)
                     Example: [
                         {"entity_type": "character", "entity_id": "luna", "role": "subject"},
                         {"entity_type": "clothing_item", "entity_id": "jacket-123", "role": "outerwear"},
                         {"entity_type": "visual_style", "entity_id": "noir-style", "role": "visual_style"}
                     ]

        Returns:
            List of created relationship dicts
        """
        relationships = []

        for entity in entities:
            rel = ImageEntityRelationship(
                image_id=image_id,
                entity_type=entity["entity_type"],
                entity_id=entity["entity_id"],
                role=entity.get("role")
            )
            relationships.append(rel)

        created_rels = await self.relationship_repository.create_many(relationships)
        await self.session.commit()

        logger.info(f"Added {len(created_rels)} entity relationships to image {image_id}", extra={'extra_fields': {
            'image_id': image_id,
            'relationship_count': len(created_rels)
        }})

        return [self._relationship_to_dict(rel) for rel in created_rels]

    async def create_image_with_relationships(
        self,
        file_path: str,
        entities: List[Dict[str, str]],
        generation_metadata: Optional[Dict[str, Any]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Create an image and its entity relationships in one transaction

        This is the main method for saving generated images with their associated entities.

        Args:
            file_path: Path to the generated image file
            entities: List of entity dicts (entity_type, entity_id, role)
            generation_metadata: Optional metadata about generation
            width: Optional image width in pixels
            height: Optional image height in pixels

        Returns:
            Tuple of (image_dict, list of relationship_dicts)
        """
        # Create image
        image_dict = await self.create_image(
            file_path=file_path,
            generation_metadata=generation_metadata,
            width=width,
            height=height
        )

        # Add relationships
        if entities:
            relationships = await self.add_entity_relationships(
                image_id=image_dict["image_id"],
                entities=entities
            )
        else:
            relationships = []

        logger.info(f"Created image with {len(relationships)} entity relationships", extra={'extra_fields': {
            'image_id': image_dict["image_id"],
            'file_path': file_path,
            'entity_count': len(entities)
        }})

        return image_dict, relationships

    async def get_images_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all images that used a specific entity (for entity galleries)

        Args:
            entity_type: Type of entity (e.g., "character", "clothing_item", "visual_style")
            entity_id: ID of the entity
            limit: Maximum number of images to return
            offset: Number of images to skip

        Returns:
            List of image dicts
        """
        images = await self.relationship_repository.get_images_by_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset
        )

        return [self._image_to_dict(image) for image in images]

    async def get_image_with_relationships(
        self,
        image_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get an image with all its entity relationships

        Args:
            image_id: UUID of the image

        Returns:
            Dict with image data and relationships, or None if not found
        """
        image = await self.image_repository.get_by_id(image_id)

        if not image:
            return None

        # Check user permission
        if self.user_id and image.user_id != self.user_id:
            return None

        # Get relationships
        relationships = await self.relationship_repository.get_by_image(image_id)

        return {
            "image": self._image_to_dict(image),
            "relationships": [self._relationship_to_dict(rel) for rel in relationships]
        }

    async def delete_image(self, image_id: str) -> bool:
        """
        Delete an image and all its relationships

        Args:
            image_id: UUID of the image

        Returns:
            True if deleted, False if not found
        """
        image = await self.image_repository.get_by_id(image_id)

        if not image:
            return False

        # Check user permission
        if self.user_id and image.user_id != self.user_id:
            return False

        # Delete relationships first (cascade should handle this, but be explicit)
        await self.relationship_repository.delete_by_image(image_id)

        # Delete image
        success = await self.image_repository.delete(image_id)

        if success:
            await self.session.commit()
            logger.info(f"Deleted image: {image_id}", extra={'extra_fields': {
                'image_id': image_id
            }})

        return success

    async def count_images_by_entity(
        self,
        entity_type: str,
        entity_id: str
    ) -> int:
        """
        Count how many images used a specific entity

        Args:
            entity_type: Type of entity
            entity_id: ID of the entity

        Returns:
            Count of images
        """
        return await self.relationship_repository.count_by_entity(
            entity_type=entity_type,
            entity_id=entity_id
        )

    async def list_all_images(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all images with their entity relationships

        Args:
            limit: Maximum number of images to return
            offset: Number of images to skip

        Returns:
            List of image dicts with relationships
        """
        import json
        import aiofiles
        from sqlalchemy import select
        from api.models.db import Character, ClothingItem

        images = await self.image_repository.get_all(limit=limit, offset=offset)

        results = []
        for image in images:
            # Get relationships for this image
            relationships = await self.relationship_repository.get_by_image(image.image_id)

            # Group relationships by entity type and fetch entity details
            entities_by_type = {}
            for rel in relationships:
                if rel.entity_type not in entities_by_type:
                    entities_by_type[rel.entity_type] = []

                # Fetch entity name based on type
                entity_name = rel.entity_id
                if rel.entity_type == 'character':
                    result = await self.session.execute(
                        select(Character.name).where(Character.character_id == rel.entity_id)
                    )
                    char_name = result.scalar_one_or_none()
                    if char_name:
                        entity_name = char_name
                elif rel.entity_type == 'clothing_item':
                    result = await self.session.execute(
                        select(ClothingItem.item).where(ClothingItem.item_id == rel.entity_id)
                    )
                    item_name = result.scalar_one_or_none()
                    if item_name:
                        entity_name = item_name
                elif rel.entity_type == 'visual_style' or rel.entity_type == 'preset':
                    # Read preset file to get name
                    preset_path = Path(f"/app/presets/visual_styles/{rel.entity_id}.json")
                    if preset_path.exists():
                        try:
                            async with aiofiles.open(preset_path, 'r') as f:
                                content = await f.read()
                                preset_data = json.loads(content)
                                # Try _metadata.display_name first, then fall back to name
                                metadata = preset_data.get('_metadata', {})
                                entity_name = metadata.get('display_name') or preset_data.get('name', rel.entity_id)
                        except Exception as e:
                            logger.warning(f"Failed to read preset {rel.entity_id}: {e}")

                entities_by_type[rel.entity_type].append({
                    "entity_id": rel.entity_id,
                    "entity_name": entity_name,
                    "role": rel.role
                })

            image_dict = self._image_to_dict(image)
            image_dict["entities"] = entities_by_type
            results.append(image_dict)

        return results

    async def count_all_images(self) -> int:
        """
        Count total number of images

        Returns:
            Total count of images
        """
        return await self.image_repository.count_all()
