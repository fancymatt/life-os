"""
Favorites Service

Manages user favorite presets.
"""

import json
from pathlib import Path
from typing import List, Set
from api.config import settings


class FavoritesService:
    """Service for managing user favorite presets"""

    def __init__(self):
        """Initialize favorites service"""
        self.data_dir = settings.base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.favorites_file = self.data_dir / "favorites.json"

        # Initialize file if it doesn't exist
        if not self.favorites_file.exists():
            self._save_favorites({})

    def _load_favorites(self) -> dict:
        """Load favorites from JSON file"""
        try:
            with open(self.favorites_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_favorites(self, favorites: dict):
        """Save favorites to JSON file"""
        with open(self.favorites_file, 'w') as f:
            json.dump(favorites, f, indent=2)

    def get_user_favorites(self, username: str) -> List[str]:
        """
        Get all favorite preset IDs for a user

        Args:
            username: Username

        Returns:
            List of preset IDs marked as favorite
        """
        favorites = self._load_favorites()
        return favorites.get(username, [])

    def add_favorite(self, username: str, preset_id: str, category: str) -> bool:
        """
        Add a preset to user's favorites

        Args:
            username: Username
            preset_id: Preset identifier
            category: Preset category (e.g., 'outfits', 'hair_styles')

        Returns:
            True if added, False if already exists
        """
        favorites = self._load_favorites()

        if username not in favorites:
            favorites[username] = []

        # Store as "category:preset_id" for uniqueness
        favorite_key = f"{category}:{preset_id}"

        if favorite_key in favorites[username]:
            return False

        favorites[username].append(favorite_key)
        self._save_favorites(favorites)
        return True

    def remove_favorite(self, username: str, preset_id: str, category: str) -> bool:
        """
        Remove a preset from user's favorites

        Args:
            username: Username
            preset_id: Preset identifier
            category: Preset category

        Returns:
            True if removed, False if not found
        """
        favorites = self._load_favorites()

        if username not in favorites:
            return False

        favorite_key = f"{category}:{preset_id}"

        if favorite_key not in favorites[username]:
            return False

        favorites[username].remove(favorite_key)
        self._save_favorites(favorites)
        return True

    def is_favorite(self, username: str, preset_id: str, category: str) -> bool:
        """
        Check if a preset is marked as favorite

        Args:
            username: Username
            preset_id: Preset identifier
            category: Preset category

        Returns:
            True if favorite, False otherwise
        """
        favorites = self._load_favorites()

        if username not in favorites:
            return False

        favorite_key = f"{category}:{preset_id}"
        return favorite_key in favorites[username]

    def get_favorites_by_category(self, username: str, category: str) -> List[str]:
        """
        Get favorite preset IDs for a specific category

        Args:
            username: Username
            category: Preset category

        Returns:
            List of preset IDs in this category
        """
        all_favorites = self.get_user_favorites(username)
        category_prefix = f"{category}:"

        return [
            fav.replace(category_prefix, '')
            for fav in all_favorites
            if fav.startswith(category_prefix)
        ]


# Global instance
favorites_service = FavoritesService()
