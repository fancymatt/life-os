"""
Favorites Service (PostgreSQL)

Business logic for managing user favorites using PostgreSQL.
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.favorite_repository import FavoriteRepository
from api.models.db import Favorite


class FavoritesServiceDB:
    """Service for managing user favorites (PostgreSQL-backed)"""

    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id
        self.repository = FavoriteRepository(session)

    async def get_user_favorites(self) -> List[str]:
        """
        Get all favorite preset IDs for the current user

        Returns:
            List of "category:preset_id" strings
        """
        favorites = await self.repository.get_user_favorites(self.user_id)
        return [f"{fav.category}:{fav.preset_id}" for fav in favorites]

    async def add_favorite(self, preset_id: str, category: str) -> bool:
        """
        Add a preset to user's favorites

        Args:
            preset_id: Preset identifier
            category: Preset category (e.g., 'outfits', 'hair_styles')

        Returns:
            True if added, False if already exists
        """
        # Check if already exists
        existing = await self.repository.get_by_preset(
            self.user_id, category, preset_id
        )
        if existing:
            return False

        # Create new favorite
        favorite = Favorite(
            user_id=self.user_id,
            category=category,
            preset_id=preset_id
        )
        await self.repository.create(favorite)
        await self.session.commit()
        return True

    async def remove_favorite(self, preset_id: str, category: str) -> bool:
        """
        Remove a preset from user's favorites

        Args:
            preset_id: Preset identifier
            category: Preset category

        Returns:
            True if removed, False if not found
        """
        favorite = await self.repository.get_by_preset(
            self.user_id, category, preset_id
        )
        if not favorite:
            return False

        await self.repository.delete(favorite)
        await self.session.commit()
        return True

    async def is_favorite(self, preset_id: str, category: str) -> bool:
        """
        Check if a preset is marked as favorite

        Args:
            preset_id: Preset identifier
            category: Preset category

        Returns:
            True if favorite, False otherwise
        """
        favorite = await self.repository.get_by_preset(
            self.user_id, category, preset_id
        )
        return favorite is not None

    async def get_favorites_by_category(self, category: str) -> List[str]:
        """
        Get favorite preset IDs for a specific category

        Args:
            category: Preset category

        Returns:
            List of preset IDs in this category
        """
        favorites = await self.repository.get_by_category(self.user_id, category)
        return [fav.preset_id for fav in favorites]
