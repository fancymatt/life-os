"""
Character Repository

Handles database operations for Character entities.
Provides clean separation between business logic and data access.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import Character
from api.logging_config import get_logger

logger = get_logger(__name__)


class CharacterRepository:
    """Repository for Character database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, character_id: str) -> Optional[Character]:
        """Get character by ID"""
        result = await self.session.execute(
            select(Character).where(Character.character_id == character_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, user_id: Optional[int] = None) -> List[Character]:
        """Get all characters, optionally filtered by user"""
        query = select(Character).order_by(Character.created_at.desc())

        if user_id is not None:
            query = query.where(Character.user_id == user_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, character: Character) -> Character:
        """Create new character"""
        self.session.add(character)
        await self.session.flush()  # Get the ID without committing

        logger.info(f"Created character in database: {character.name} ({character.character_id})")
        return character

    async def update(self, character: Character) -> Character:
        """Update existing character"""
        await self.session.merge(character)
        await self.session.flush()

        logger.info(f"Updated character in database: {character.name} ({character.character_id})")
        return character

    async def delete(self, character_id: str) -> bool:
        """Delete character by ID"""
        character = await self.get_by_id(character_id)

        if not character:
            return False

        await self.session.delete(character)
        await self.session.flush()

        logger.info(f"Deleted character from database: {character_id}")
        return True

    async def search(
        self,
        query: Optional[str] = None,
        user_id: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> List[Character]:
        """
        Search characters with optional filters

        Args:
            query: Text search in name, personality, or description
            user_id: Filter by user ID
            tags: Filter by tags (must have all tags)
        """
        stmt = select(Character)

        if user_id is not None:
            stmt = stmt.where(Character.user_id == user_id)

        if query:
            # Case-insensitive search in name, personality, or visual description
            search_filter = (
                Character.name.ilike(f"%{query}%") |
                Character.personality.ilike(f"%{query}%") |
                Character.visual_description.ilike(f"%{query}%")
            )
            stmt = stmt.where(search_filter)

        # Note: Tag filtering with JSON arrays is complex in PostgreSQL
        # For now, we'll do tag filtering in Python after retrieval

        stmt = stmt.order_by(Character.created_at.desc())

        result = await self.session.execute(stmt)
        characters = list(result.scalars().all())

        # Filter by tags if provided
        if tags:
            characters = [
                char for char in characters
                if all(tag in char.tags for tag in tags)
            ]

        return characters

    async def exists(self, character_id: str) -> bool:
        """Check if character exists"""
        character = await self.get_by_id(character_id)
        return character is not None

    async def count(self, user_id: Optional[int] = None) -> int:
        """Count characters, optionally filtered by user"""
        from sqlalchemy import func

        query = select(func.count()).select_from(Character)

        if user_id is not None:
            query = query.where(Character.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one()
