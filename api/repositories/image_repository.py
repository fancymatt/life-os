"""
Image Repository

Handles database operations for Image entities.
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import Image
from api.logging_config import get_logger

logger = get_logger(__name__)


class ImageRepository:
    """Repository for Image database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, image_id: str) -> Optional[Image]:
        """Get image by ID"""
        result = await self.session.execute(
            select(Image).where(Image.image_id == image_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        user_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Image]:
        """Get all images, optionally filtered by user"""
        query = select(Image).order_by(Image.created_at.desc())

        if user_id is not None:
            query = query.where(Image.user_id == user_id)

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, image: Image) -> Image:
        """Create new image"""
        self.session.add(image)
        await self.session.flush()

        logger.info(f"Created image in database: {image.image_id}")
        return image

    async def update(self, image: Image) -> Image:
        """Update existing image"""
        await self.session.merge(image)
        await self.session.flush()

        logger.info(f"Updated image in database: {image.image_id}")
        return image

    async def delete(self, image_id: str) -> bool:
        """Delete image by ID"""
        image = await self.get_by_id(image_id)

        if not image:
            return False

        await self.session.delete(image)
        await self.session.flush()

        logger.info(f"Deleted image from database: {image_id}")
        return True

    async def exists(self, image_id: str) -> bool:
        """Check if image exists"""
        image = await self.get_by_id(image_id)
        return image is not None

    async def count(self, user_id: Optional[int] = None) -> int:
        """Count images"""
        query = select(func.count()).select_from(Image)

        if user_id is not None:
            query = query.where(Image.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one()
