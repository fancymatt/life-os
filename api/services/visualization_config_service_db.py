"""
Visualization Config Service (PostgreSQL)

Database-backed implementation of visualization config service using PostgreSQL.
Replaces JSON file storage with relational database.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.models.db import VisualizationConfig
from api.repositories import VisualizationConfigRepository
from api.logging_config import get_logger

logger = get_logger(__name__)


class VisualizationConfigServiceDB:
    """PostgreSQL-based visualization config service"""

    def __init__(self, session: AsyncSession, user_id: Optional[int] = None):
        """
        Initialize visualization config service with database session

        Args:
            session: SQLAlchemy async session
            user_id: Optional user ID for filtering
        """
        self.session = session
        self.user_id = user_id
        self.repository = VisualizationConfigRepository(session)

    def _config_to_dict(self, config: VisualizationConfig) -> Dict[str, Any]:
        """Convert VisualizationConfig model to dict"""
        return {
            "config_id": config.config_id,
            "entity_type": config.entity_type,
            "display_name": config.display_name,
            "composition_style": config.composition_style,
            "framing": config.framing,
            "angle": config.angle,
            "background": config.background,
            "lighting": config.lighting,
            "art_style_id": config.art_style_id,
            "reference_image_path": config.reference_image_path,
            "additional_instructions": config.additional_instructions,
            "image_size": config.image_size,
            "model": config.model,
            "is_default": config.is_default,
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        }

    async def list_configs(
        self,
        entity_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all visualization configs, optionally filtered by entity type

        Args:
            entity_type: Optional filter by entity type (e.g., "clothing_item", "character")
            limit: Maximum number of configs to return
            offset: Number of configs to skip
            include_archived: If True, include archived configs. Default False.

        Returns:
            List of visualization config dicts
        """
        configs = await self.repository.get_all(
            entity_type=entity_type,
            user_id=self.user_id,
            limit=limit,
            offset=offset,
            include_archived=include_archived
        )
        return [self._config_to_dict(config) for config in configs]

    async def get_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single visualization config by ID

        Args:
            config_id: UUID of the config

        Returns:
            Config dict or None if not found
        """
        config = await self.repository.get_by_id(config_id)

        if not config:
            return None

        # Filter by user if specified
        if self.user_id and config.user_id != self.user_id:
            return None

        return self._config_to_dict(config)

    async def get_default_config(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the default visualization config for an entity type

        Args:
            entity_type: Entity type (e.g., "clothing_item")

        Returns:
            Default config dict or None if not found
        """
        config = await self.repository.get_default_for_entity_type(entity_type)

        if not config:
            return None

        return self._config_to_dict(config)

    async def create_config(
        self,
        entity_type: str,
        display_name: str,
        composition_style: str = "product",
        framing: str = "medium",
        angle: str = "front",
        background: str = "white",
        lighting: str = "soft_even",
        art_style_id: Optional[str] = None,
        reference_image_path: Optional[str] = None,
        additional_instructions: str = "",
        image_size: str = "1024x1024",
        model: str = "gemini/gemini-2.5-flash-image",
        is_default: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new visualization config

        Args:
            entity_type: Entity type this config applies to
            display_name: User-friendly name
            composition_style: Visual composition style
            framing: Camera framing
            angle: Camera angle
            background: Background style
            lighting: Lighting style
            art_style_id: Optional link to art style preset
            reference_image_path: Optional reference image path
            additional_instructions: Free-form instructions
            image_size: Output image dimensions
            model: Image generation model
            is_default: Whether this is the default config for this entity type

        Returns:
            Created config dict
        """
        config_id = str(uuid.uuid4())

        # If this should be the default, unmark any existing defaults for this entity type
        if is_default:
            await self.repository.unmark_all_defaults_for_entity_type(entity_type)

        config = VisualizationConfig(
            config_id=config_id,
            entity_type=entity_type,
            display_name=display_name,
            composition_style=composition_style,
            framing=framing,
            angle=angle,
            background=background,
            lighting=lighting,
            art_style_id=art_style_id,
            reference_image_path=reference_image_path,
            additional_instructions=additional_instructions,
            image_size=image_size,
            model=model,
            is_default=is_default,
            user_id=self.user_id
        )

        config = await self.repository.create(config)
        await self.session.commit()

        logger.info(f"Created visualization config: {display_name} ({entity_type})")

        return self._config_to_dict(config)

    async def update_config(
        self,
        config_id: str,
        **updates
    ) -> Optional[Dict[str, Any]]:
        """
        Update a visualization config

        Args:
            config_id: UUID of the config
            **updates: Dict of field names to update values
                      Fields not present in updates will not be modified
                      Fields present with value None will be cleared (set to None)

        Returns:
            Updated config dict or None if not found
        """
        # Load existing config
        config = await self.repository.get_by_id(config_id)
        if not config:
            return None

        # Check user permission
        if self.user_id and config.user_id != self.user_id:
            return None

        # If making this the default, unmark other defaults for this entity type
        if updates.get('is_default') is True:
            await self.repository.unmark_all_defaults_for_entity_type(
                config.entity_type,
                exclude_config_id=config_id
            )

        # Define which fields are allowed to be updated
        allowed_fields = {
            'display_name', 'entity_type', 'composition_style', 'framing', 'angle',
            'background', 'lighting', 'art_style_id', 'reference_image_path',
            'additional_instructions', 'image_size', 'model', 'is_default'
        }

        # Update only the fields that were provided in updates
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(config, field, value)
            else:
                logger.warning(f"Ignoring unknown field in update: {field}")

        # Update timestamp
        config.updated_at = datetime.utcnow()

        config = await self.repository.update(config)
        await self.session.commit()

        logger.info(f"Updated visualization config: {config_id}")

        return self._config_to_dict(config)

    async def delete_config(self, config_id: str) -> bool:
        """
        Delete a visualization config

        Args:
            config_id: UUID of the config

        Returns:
            True if deleted, False if not found
        """
        config = await self.repository.get_by_id(config_id)

        if not config:
            return False

        # Check user permission
        if self.user_id and config.user_id != self.user_id:
            return False

        # Check if this is a default config
        if config.is_default:
            logger.warning(f"Warning: Deleting default config for {config.entity_type}")

        success = await self.repository.delete(config_id)

        if success:
            await self.session.commit()
            logger.info(f"Deleted visualization config: {config_id}")

        return success

    async def archive_config(self, config_id: str) -> bool:
        """
        Archive a visualization config (soft delete)

        Args:
            config_id: UUID of the config

        Returns:
            True if archived, False if not found
        """
        config = await self.repository.get_by_id(config_id)

        if not config:
            return False

        # Check user permission
        if self.user_id and config.user_id != self.user_id:
            return False

        # Check if this is a default config
        if config.is_default:
            logger.warning(f"Warning: Archiving default config for {config.entity_type}")

        success = await self.repository.archive(config_id)

        if success:
            await self.session.commit()
            logger.info(f"Archived visualization config: {config_id}")

        return success

    async def unarchive_config(self, config_id: str) -> bool:
        """
        Unarchive a visualization config

        Args:
            config_id: UUID of the config

        Returns:
            True if unarchived, False if not found
        """
        config = await self.repository.get_by_id(config_id)

        if not config:
            return False

        # Check user permission
        if self.user_id and config.user_id != self.user_id:
            return False

        success = await self.repository.unarchive(config_id)

        if success:
            await self.session.commit()
            logger.info(f"Unarchived visualization config: {config_id}")

        return success

    async def count_configs(
        self,
        entity_type: Optional[str] = None,
        include_archived: bool = False
    ) -> int:
        """
        Count total visualization configs (before pagination)

        Args:
            entity_type: Optional filter by entity type
            include_archived: If True, include archived configs. Default False.

        Returns:
            Total number of configs matching the filter
        """
        return await self.repository.count(
            entity_type=entity_type,
            user_id=self.user_id,
            include_archived=include_archived
        )

    async def get_entity_types_summary(self) -> Dict[str, int]:
        """
        Get count of configs per entity type

        Returns:
            Dict mapping entity type to count
        """
        return await self.repository.get_entity_types_summary()
