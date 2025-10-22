"""
Board Game Repository

Handles database operations for BoardGame entities.
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import BoardGame
from api.logging_config import get_logger

logger = get_logger(__name__)


class BoardGameRepository:
    """Repository for BoardGame database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, game_id: str) -> Optional[BoardGame]:
        """Get board game by ID"""
        result = await self.session.execute(
            select(BoardGame).where(BoardGame.game_id == game_id)
        )
        return result.scalar_one_or_none()

    async def get_by_bgg_id(self, bgg_id: int) -> Optional[BoardGame]:
        """Get board game by BoardGameGeek ID"""
        result = await self.session.execute(
            select(BoardGame).where(BoardGame.bgg_id == bgg_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, user_id: Optional[int] = None) -> List[BoardGame]:
        """Get all board games, optionally filtered by user"""
        query = select(BoardGame).order_by(BoardGame.name)

        if user_id is not None:
            query = query.where(BoardGame.user_id == user_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, game: BoardGame) -> BoardGame:
        """Create new board game"""
        self.session.add(game)
        await self.session.flush()

        logger.info(f"Created board game in database: {game.name} (BGG:{game.bgg_id})")
        return game

    async def update(self, game: BoardGame) -> BoardGame:
        """Update existing board game"""
        await self.session.merge(game)
        await self.session.flush()

        logger.info(f"Updated board game in database: {game.name} ({game.game_id})")
        return game

    async def delete(self, game_id: str) -> bool:
        """Delete board game by ID"""
        game = await self.get_by_id(game_id)

        if not game:
            return False

        await self.session.delete(game)
        await self.session.flush()

        logger.info(f"Deleted board game from database: {game_id}")
        return True

    async def search(
        self,
        query: Optional[str] = None,
        designer: Optional[str] = None,
        min_players: Optional[int] = None,
        max_players: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[BoardGame]:
        """
        Search board games with optional filters

        Args:
            query: Text search in name, designer, or publisher
            designer: Filter by designer
            min_players: Filter by minimum player count
            max_players: Filter by maximum player count
            user_id: Filter by user ID
        """
        stmt = select(BoardGame)

        if user_id is not None:
            stmt = stmt.where(BoardGame.user_id == user_id)

        if query:
            # Case-insensitive search in name, designer, or publisher
            search_filter = (
                BoardGame.name.ilike(f"%{query}%") |
                BoardGame.designer.ilike(f"%{query}%") |
                BoardGame.publisher.ilike(f"%{query}%")
            )
            stmt = stmt.where(search_filter)

        if designer:
            stmt = stmt.where(BoardGame.designer.ilike(f"%{designer}%"))

        if min_players is not None:
            # Game supports at least min_players
            stmt = stmt.where(BoardGame.player_count_max >= min_players)

        if max_players is not None:
            # Game supports at most max_players
            stmt = stmt.where(BoardGame.player_count_min <= max_players)

        stmt = stmt.order_by(BoardGame.name)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists(self, game_id: str) -> bool:
        """Check if board game exists"""
        game = await self.get_by_id(game_id)
        return game is not None

    async def exists_by_bgg_id(self, bgg_id: int) -> bool:
        """Check if board game exists by BGG ID"""
        game = await self.get_by_bgg_id(bgg_id)
        return game is not None

    async def count(self, user_id: Optional[int] = None) -> int:
        """Count board games"""
        query = select(func.count()).select_from(BoardGame)

        if user_id is not None:
            query = query.where(BoardGame.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one()
