"""
Board Game Service (PostgreSQL)

Database-backed implementation of board game service using PostgreSQL.
Replaces JSON file storage with relational database.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import BoardGame
from api.repositories import BoardGameRepository
from api.logging_config import get_logger

logger = get_logger(__name__)


class BoardGameServiceDB:
    """PostgreSQL-based board game service"""

    def __init__(self, session: AsyncSession, user_id: Optional[int] = None):
        """
        Initialize board game service with database session

        Args:
            session: SQLAlchemy async session
            user_id: Optional user ID for filtering
        """
        self.session = session
        self.user_id = user_id
        self.repository = BoardGameRepository(session)

    def _board_game_to_dict(self, game: BoardGame) -> Dict[str, Any]:
        """Convert BoardGame model to dict"""
        return {
            "game_id": game.game_id,
            "name": game.name,
            "bgg_id": game.bgg_id,
            "designer": game.designer,
            "publisher": game.publisher,
            "year": game.year,
            "description": game.description,
            "player_count_min": game.player_count_min,
            "player_count_max": game.player_count_max,
            "playtime_min": game.playtime_min,
            "playtime_max": game.playtime_max,
            "complexity": game.complexity,
            "created_at": game.created_at.isoformat() if game.created_at else None,
            "updated_at": game.updated_at.isoformat() if game.updated_at else None,
            "metadata": game.meta,  # Note: 'meta' in DB, 'metadata' in API
        }

    async def create_board_game(
        self,
        name: str,
        bgg_id: Optional[int] = None,
        designer: Optional[str] = None,
        publisher: Optional[str] = None,
        year: Optional[int] = None,
        description: Optional[str] = None,
        player_count_min: Optional[int] = None,
        player_count_max: Optional[int] = None,
        playtime_min: Optional[int] = None,
        playtime_max: Optional[int] = None,
        complexity: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new board game

        Args:
            name: Board game name
            bgg_id: BoardGameGeek ID
            designer: Game designer(s)
            publisher: Publisher
            year: Publication year
            description: Game description
            player_count_min: Minimum players
            player_count_max: Maximum players
            playtime_min: Minimum playtime (minutes)
            playtime_max: Maximum playtime (minutes)
            complexity: Complexity rating (1-5)
            metadata: Additional metadata

        Returns:
            Board game data dict
        """
        # Use bgg_id as game_id if provided, otherwise generate UUID
        if bgg_id:
            game_id = f"bgg-{bgg_id}"
        else:
            game_id = str(uuid.uuid4())[:8]

        board_game = BoardGame(
            game_id=game_id,
            name=name,
            bgg_id=bgg_id,
            designer=designer,
            publisher=publisher,
            year=year,
            description=description,
            player_count_min=player_count_min,
            player_count_max=player_count_max,
            playtime_min=playtime_min,
            playtime_max=playtime_max,
            complexity=complexity,
            meta=metadata or {},  # Note: 'meta' in DB
            user_id=self.user_id
        )

        board_game = await self.repository.create(board_game)
        await self.session.commit()

        logger.info(f"Created board game: {name}", extra={'extra_fields': {
            'game_id': game_id,
            'name': name,
            'bgg_id': bgg_id
        }})

        return self._board_game_to_dict(board_game)

    async def get_board_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a board game by ID

        Args:
            game_id: Board game ID

        Returns:
            Board game data dict or None if not found
        """
        board_game = await self.repository.get_by_id(game_id)

        if not board_game:
            return None

        # Filter by user if specified
        if self.user_id and board_game.user_id != self.user_id:
            return None

        return self._board_game_to_dict(board_game)

    async def get_by_bgg_id(self, bgg_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a board game by BGG ID

        Args:
            bgg_id: BoardGameGeek ID

        Returns:
            Board game data dict or None if not found
        """
        board_game = await self.repository.get_by_bgg_id(bgg_id)

        if not board_game:
            return None

        # Filter by user if specified
        if self.user_id and board_game.user_id != self.user_id:
            return None

        return self._board_game_to_dict(board_game)

    async def list_board_games(self) -> List[Dict[str, Any]]:
        """
        List all board games (filtered by user if specified)

        Returns:
            List of board game data dicts
        """
        board_games = await self.repository.get_all(user_id=self.user_id)
        return [self._board_game_to_dict(game) for game in board_games]

    async def update_board_game(
        self,
        game_id: str,
        name: Optional[str] = None,
        designer: Optional[str] = None,
        publisher: Optional[str] = None,
        year: Optional[int] = None,
        description: Optional[str] = None,
        player_count_min: Optional[int] = None,
        player_count_max: Optional[int] = None,
        playtime_min: Optional[int] = None,
        playtime_max: Optional[int] = None,
        complexity: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a board game

        Args:
            game_id: Board game ID
            name: New name (optional)
            designer: New designer (optional)
            publisher: New publisher (optional)
            year: New year (optional)
            description: New description (optional)
            player_count_min: New minimum players (optional)
            player_count_max: New maximum players (optional)
            playtime_min: New minimum playtime (optional)
            playtime_max: New maximum playtime (optional)
            complexity: New complexity rating (optional)
            metadata: New metadata (optional)

        Returns:
            Updated board game data dict or None if not found
        """
        board_game = await self.repository.get_by_id(game_id)

        if not board_game:
            return None

        # Check user permission
        if self.user_id and board_game.user_id != self.user_id:
            return None

        # Update fields if provided
        if name is not None:
            board_game.name = name
        if designer is not None:
            board_game.designer = designer
        if publisher is not None:
            board_game.publisher = publisher
        if year is not None:
            board_game.year = year
        if description is not None:
            board_game.description = description
        if player_count_min is not None:
            board_game.player_count_min = player_count_min
        if player_count_max is not None:
            board_game.player_count_max = player_count_max
        if playtime_min is not None:
            board_game.playtime_min = playtime_min
        if playtime_max is not None:
            board_game.playtime_max = playtime_max
        if complexity is not None:
            board_game.complexity = complexity
        if metadata is not None:
            board_game.meta.update(metadata)  # Note: 'meta' in DB

        board_game.updated_at = datetime.utcnow()

        board_game = await self.repository.update(board_game)
        await self.session.commit()

        logger.info(f"Updated board game: {game_id}", extra={'extra_fields': {
            'game_id': game_id
        }})

        return self._board_game_to_dict(board_game)

    async def delete_board_game(self, game_id: str) -> bool:
        """
        Delete a board game

        Args:
            game_id: Board game ID

        Returns:
            True if deleted, False if not found
        """
        board_game = await self.repository.get_by_id(game_id)

        if not board_game:
            return False

        # Check user permission
        if self.user_id and board_game.user_id != self.user_id:
            return False

        success = await self.repository.delete(game_id)

        if success:
            await self.session.commit()
            logger.info(f"Deleted board game: {game_id}", extra={'extra_fields': {
                'game_id': game_id
            }})

        return success
