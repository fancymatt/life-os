"""
Board Game Service

Handles board game entity storage, retrieval, and management.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from api.config import settings
from api.logging_config import get_logger

logger = get_logger(__name__)


class BoardGameService:
    """Service for managing board game entities"""

    def __init__(self):
        """Initialize board game service"""
        self.games_dir = Path(settings.base_dir) / "data" / "board_games"
        self.games_dir.mkdir(parents=True, exist_ok=True)

    def _get_game_path(self, game_id: str) -> Path:
        """Get path to board game JSON file"""
        return self.games_dir / f"{game_id}.json"

    def create_board_game(
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

        game_data = {
            "game_id": game_id,
            "name": name,
            "bgg_id": bgg_id,
            "designer": designer,
            "publisher": publisher,
            "year": year,
            "description": description,
            "player_count_min": player_count_min,
            "player_count_max": player_count_max,
            "playtime_min": playtime_min,
            "playtime_max": playtime_max,
            "complexity": complexity,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        # Save game data
        game_file = self._get_game_path(game_id)
        with open(game_file, 'w') as f:
            json.dump(game_data, f, indent=2)

        return game_data

    def get_board_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a board game by ID

        Args:
            game_id: Board game ID

        Returns:
            Board game data dict or None if not found
        """
        game_file = self._get_game_path(game_id)

        if not game_file.exists():
            return None

        with open(game_file, 'r') as f:
            return json.load(f)

    def get_by_bgg_id(self, bgg_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a board game by BGG ID

        Args:
            bgg_id: BoardGameGeek ID

        Returns:
            Board game data dict or None if not found
        """
        return self.get_board_game(f"bgg-{bgg_id}")

    def list_board_games(self) -> List[Dict[str, Any]]:
        """
        List all board games

        Returns:
            List of board game data dicts
        """
        games = []

        for file_path in self.games_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    game_data = json.load(f)
                    games.append(game_data)
            except Exception as e:
                logger.error(f"Error loading board game {file_path}: {e}")
                continue

        # Sort by name
        games.sort(key=lambda x: x.get('name', '').lower())

        return games

    def update_board_game(
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
        game_data = self.get_board_game(game_id)

        if not game_data:
            return None

        # Update fields if provided
        if name is not None:
            game_data['name'] = name
        if designer is not None:
            game_data['designer'] = designer
        if publisher is not None:
            game_data['publisher'] = publisher
        if year is not None:
            game_data['year'] = year
        if description is not None:
            game_data['description'] = description
        if player_count_min is not None:
            game_data['player_count_min'] = player_count_min
        if player_count_max is not None:
            game_data['player_count_max'] = player_count_max
        if playtime_min is not None:
            game_data['playtime_min'] = playtime_min
        if playtime_max is not None:
            game_data['playtime_max'] = playtime_max
        if complexity is not None:
            game_data['complexity'] = complexity
        if metadata is not None:
            game_data['metadata'].update(metadata)

        game_data['updated_at'] = datetime.utcnow().isoformat()

        # Save updated data
        game_file = self._get_game_path(game_id)
        with open(game_file, 'w') as f:
            json.dump(game_data, f, indent=2)

        return game_data

    def delete_board_game(self, game_id: str) -> bool:
        """
        Delete a board game

        Args:
            game_id: Board game ID

        Returns:
            True if deleted, False if not found
        """
        game_file = self._get_game_path(game_id)

        if not game_file.exists():
            return False

        # Delete game file
        game_file.unlink()

        return True
