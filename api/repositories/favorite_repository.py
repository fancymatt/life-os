"""
Favorite Repository

Data access layer for Favorite entity operations.
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import Favorite


class FavoriteRepository:
    """Repository for Favorite database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_favorites(self, user_id: int) -> List[Favorite]:
        """Get all favorites for a user"""
        result = await self.session.execute(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_category(self, user_id: int, category: str) -> List[Favorite]:
        """Get favorites for a specific category"""
        result = await self.session.execute(
            select(Favorite)
            .where(and_(Favorite.user_id == user_id, Favorite.category == category))
            .order_by(Favorite.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_preset(self, user_id: int, category: str, preset_id: str) -> Optional[Favorite]:
        """Get a specific favorite"""
        result = await self.session.execute(
            select(Favorite).where(
                and_(
                    Favorite.user_id == user_id,
                    Favorite.category == category,
                    Favorite.preset_id == preset_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(self, favorite: Favorite) -> Favorite:
        """Create a new favorite"""
        self.session.add(favorite)
        await self.session.flush()  # Get ID without committing
        return favorite

    async def delete(self, favorite: Favorite) -> None:
        """Delete favorite"""
        await self.session.delete(favorite)
        await self.session.flush()
