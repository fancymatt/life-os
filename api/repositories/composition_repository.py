"""
Composition Repository

Data access layer for Composition entity operations.
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import Composition


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
        offset: int = 0
    ) -> List[Composition]:
        """Get all compositions, optionally filtered by user with pagination support"""
        query = select(Composition).order_by(Composition.updated_at.desc())

        if user_id is not None:
            query = query.where(Composition.user_id == user_id)

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
        """Delete composition"""
        await self.session.delete(composition)
        await self.session.flush()

    async def count(self, user_id: Optional[int] = None) -> int:
        """Count compositions"""
        query = select(func.count()).select_from(Composition)

        if user_id is not None:
            query = query.where(Composition.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one()
