"""
Database Repositories

Provides data access layer for PostgreSQL database operations.
"""

from api.repositories.user_repository import UserRepository
from api.repositories.character_repository import CharacterRepository
from api.repositories.clothing_item_repository import ClothingItemRepository
from api.repositories.board_game_repository import BoardGameRepository
from api.repositories.outfit_repository import OutfitRepository
from api.repositories.story_repository import StoryRepository
from api.repositories.favorite_repository import FavoriteRepository
from api.repositories.composition_repository import CompositionRepository
from api.repositories.image_repository import ImageRepository
from api.repositories.image_entity_relationship_repository import ImageEntityRelationshipRepository
from api.repositories.visualization_config_repository import VisualizationConfigRepository

__all__ = [
    'UserRepository',
    'CharacterRepository',
    'ClothingItemRepository',
    'BoardGameRepository',
    'OutfitRepository',
    'StoryRepository',
    'FavoriteRepository',
    'CompositionRepository',
    'ImageRepository',
    'ImageEntityRelationshipRepository',
    'VisualizationConfigRepository',
]
