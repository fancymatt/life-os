"""
Composition Repository

Data access layer for Composition entity operations.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import Composition
from api.logging_config import get_logger

logger = get_logger(__name__)


class CompositionRepository:
    """Repository for Composition database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, composition_id: str) -> Optional[Composition]:
        """Get composition by ID"""
        result = await self.session.execute(
            select(Composition).where(Composition.composition_id == composition_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        user_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Composition]:
        """Get all compositions, optionally filtered by user with pagination support"""
        query = select(Composition).order_by(Composition.updated_at.desc())

        if user_id is not None:
            query = query.where(Composition.user_id == user_id)

        # Exclude archived by default
        if not include_archived:
            query = query.where(Composition.archived == False)

        if limit is not None:
            query = query.limit(limit)

        query = query.offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, composition: Composition) -> Composition:
        """Create a new composition"""
        self.session.add(composition)
        await self.session.flush()  # Get ID without committing
        return composition

    async def update(self, composition: Composition) -> Composition:
        """Update composition"""
        await self.session.flush()
        return composition

    async def delete(self, composition: Composition) -> None:
        """Archive composition (soft delete)"""
        composition.archived = True
        composition.archived_at = datetime.utcnow()
        await self.session.flush()
        logger.info(f"Archived composition in database: {composition.composition_id}")

    async def archive(self, composition_id: str) -> bool:
        """Archive composition by ID (soft delete)"""
        composition = await self.get_by_id(composition_id)
        if not composition:
            return False
        composition.archived = True
        composition.archived_at = datetime.utcnow()
        await self.session.flush()
        logger.info(f"Archived composition in database: {composition_id}")
        return True

    async def unarchive(self, composition_id: str) -> bool:
        """Unarchive composition by ID"""
        composition = await self.get_by_id(composition_id)
        if not composition:
            return False
        composition.archived = False
        composition.archived_at = None
        await self.session.flush()
        logger.info(f"Unarchived composition in database: {composition_id}")
        return True

    async def count(self, user_id: Optional[int] = None, include_archived: bool = False) -> int:
        """Count compositions"""
        query = select(func.count()).select_from(Composition)

        if user_id is not None:
            query = query.where(Composition.user_id == user_id)

        # Exclude archived by default
        if not include_archived:
            query = query.where(Composition.archived == False)

        result = await self.session.execute(query)
        return result.scalar_one()
