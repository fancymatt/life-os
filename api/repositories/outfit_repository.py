"""
Outfit Repository

Data access layer for Outfit entity operations.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import Outfit
from api.logging_config import get_logger

logger = get_logger(__name__)


class OutfitRepository:
    """Repository for Outfit database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, outfit_id: str) -> Optional[Outfit]:
        """Get outfit by ID"""
        result = await self.session.execute(
            select(Outfit).where(Outfit.outfit_id == outfit_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, user_id: Optional[int] = None, include_archived: bool = False) -> List[Outfit]:
        """Get all outfits, optionally filtered by user"""
        query = select(Outfit).order_by(Outfit.created_at.desc())
        if user_id is not None:
            query = query.where(Outfit.user_id == user_id)
        # Exclude archived by default
        if not include_archived:
            query = query.where(Outfit.archived == False)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, outfit: Outfit) -> Outfit:
        """Create a new outfit"""
        self.session.add(outfit)
        await self.session.flush()  # Get ID without committing
        return outfit

    async def update(self, outfit: Outfit) -> Outfit:
        """Update outfit"""
        await self.session.flush()
        return outfit

    async def delete(self, outfit: Outfit) -> None:
        """Archive outfit (soft delete)"""
        outfit.archived = True
        outfit.archived_at = datetime.utcnow()
        await self.session.flush()
        logger.info(f"Archived outfit in database: {outfit.outfit_id}")

    async def archive(self, outfit_id: str) -> bool:
        """Archive outfit by ID (soft delete)"""
        outfit = await self.get_by_id(outfit_id)
        if not outfit:
            return False
        outfit.archived = True
        outfit.archived_at = datetime.utcnow()
        await self.session.flush()
        logger.info(f"Archived outfit in database: {outfit_id}")
        return True

    async def unarchive(self, outfit_id: str) -> bool:
        """Unarchive outfit by ID"""
        outfit = await self.get_by_id(outfit_id)
        if not outfit:
            return False
        outfit.archived = False
        outfit.archived_at = None
        await self.session.flush()
        logger.info(f"Unarchived outfit in database: {outfit_id}")
        return True
