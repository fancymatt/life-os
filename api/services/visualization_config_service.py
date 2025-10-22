"""
Visualization Config Service

Business logic for managing visualization configuration entities.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import uuid
import sys

from api.config import settings
from ai_capabilities.specs import (
    VisualizationConfigEntity,
    CompositionStyle,
    Framing,
    CameraAngle,
    BackgroundStyle,
    LightingStyle
)


class VisualizationConfigService:
    """Service for managing visualization config entities"""

    def __init__(self):
        self.configs_dir = settings.base_dir / "data" / "visualization_configs"
        self.configs_dir.mkdir(parents=True, exist_ok=True)

    def list_configs(
        self,
        entity_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all visualization configs, optionally filtered by entity type

        Args:
            entity_type: Optional filter by entity type (e.g., "clothing_item", "character")
            limit: Maximum number of configs to return
            offset: Number of configs to skip

        Returns:
            List of visualization config dicts
        """
        configs = []

        # Read all config files
        for config_path in self.configs_dir.glob("*.json"):
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)

                    # Apply entity_type filter if provided
                    if entity_type and config_data.get('entity_type') != entity_type:
                        continue

                    configs.append(config_data)
            except Exception as e:
                print(f"⚠️  Failed to load config {config_path.name}: {e}")
                continue

        # Sort by updated_at (newest first)
        configs.sort(key=lambda x: x.get('updated_at', ''), reverse=True)

        # Apply pagination
        if offset:
            configs = configs[offset:]
        if limit:
            configs = configs[:limit]

        return configs

    def get_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single visualization config by ID

        Args:
            config_id: UUID of the config

        Returns:
            Config dict or None if not found
        """
        config_path = self.configs_dir / f"{config_id}.json"

        if not config_path.exists():
            return None

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load config {config_id}: {e}")
            return None

    def get_default_config(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the default visualization config for an entity type

        Args:
            entity_type: Entity type (e.g., "clothing_item")

        Returns:
            Default config dict or None if not found
        """
        configs = self.list_configs(entity_type=entity_type)

        # Find the config marked as default
        for config in configs:
            if config.get('is_default', False):
                return config

        # If no default found, return the first config
        if configs:
            return configs[0]

        return None

    def create_config(
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
        # Generate UUID
        config_id = str(uuid.uuid4())

        # If this should be the default, unmark any existing defaults for this entity type
        if is_default:
            self._unmark_defaults(entity_type)

        # Create entity
        config_entity = VisualizationConfigEntity(
            config_id=config_id,
            entity_type=entity_type,
            display_name=display_name,
            composition_style=CompositionStyle(composition_style),
            framing=Framing(framing),
            angle=CameraAngle(angle),
            background=BackgroundStyle(background),
            lighting=LightingStyle(lighting),
            art_style_id=art_style_id,
            reference_image_path=reference_image_path,
            additional_instructions=additional_instructions,
            image_size=image_size,
            model=model,
            is_default=is_default,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to file
        config_path = self.configs_dir / f"{config_id}.json"
        with open(config_path, 'w') as f:
            json.dump(config_entity.dict(), f, indent=2, default=str)

        print(f"✅ Created visualization config: {display_name} ({entity_type})")

        return config_entity.dict()

    def update_config(
        self,
        config_id: str,
        display_name: Optional[str] = None,
        composition_style: Optional[str] = None,
        framing: Optional[str] = None,
        angle: Optional[str] = None,
        background: Optional[str] = None,
        lighting: Optional[str] = None,
        art_style_id: Optional[str] = None,
        reference_image_path: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        image_size: Optional[str] = None,
        model: Optional[str] = None,
        is_default: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a visualization config

        Args:
            config_id: UUID of the config
            (various optional update fields)

        Returns:
            Updated config dict or None if not found
        """
        # Load existing config
        existing_config = self.get_config(config_id)
        if not existing_config:
            return None

        # If making this the default, unmark other defaults for this entity type
        if is_default is True:
            self._unmark_defaults(existing_config['entity_type'], exclude_id=config_id)

        # Update fields
        if display_name is not None:
            existing_config['display_name'] = display_name
        if composition_style is not None:
            existing_config['composition_style'] = composition_style
        if framing is not None:
            existing_config['framing'] = framing
        if angle is not None:
            existing_config['angle'] = angle
        if background is not None:
            existing_config['background'] = background
        if lighting is not None:
            existing_config['lighting'] = lighting
        if art_style_id is not None:
            existing_config['art_style_id'] = art_style_id
        if reference_image_path is not None:
            existing_config['reference_image_path'] = reference_image_path
        if additional_instructions is not None:
            existing_config['additional_instructions'] = additional_instructions
        if image_size is not None:
            existing_config['image_size'] = image_size
        if model is not None:
            existing_config['model'] = model
        if is_default is not None:
            existing_config['is_default'] = is_default

        # Update timestamp
        existing_config['updated_at'] = datetime.now().isoformat()

        # Save updated config
        config_path = self.configs_dir / f"{config_id}.json"
        with open(config_path, 'w') as f:
            json.dump(existing_config, f, indent=2, default=str)

        print(f"✅ Updated visualization config: {config_id}")

        return existing_config

    def delete_config(self, config_id: str) -> bool:
        """
        Delete a visualization config

        Args:
            config_id: UUID of the config

        Returns:
            True if deleted, False if not found
        """
        config_path = self.configs_dir / f"{config_id}.json"

        if not config_path.exists():
            return False

        # Check if this is a default config
        config_data = self.get_config(config_id)
        if config_data and config_data.get('is_default', False):
            print(f"⚠️  Warning: Deleting default config for {config_data.get('entity_type')}")

        config_path.unlink()
        print(f"✅ Deleted visualization config: {config_id}")

        return True

    def _unmark_defaults(self, entity_type: str, exclude_id: Optional[str] = None):
        """
        Unmark all default configs for an entity type

        Args:
            entity_type: Entity type to unmark defaults for
            exclude_id: Optional config ID to exclude from unmarking
        """
        configs = self.list_configs(entity_type=entity_type)

        for config in configs:
            if config.get('is_default', False) and config['config_id'] != exclude_id:
                config['is_default'] = False
                config['updated_at'] = datetime.now().isoformat()

                config_path = self.configs_dir / f"{config['config_id']}.json"
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2, default=str)

    def get_entity_types_summary(self) -> Dict[str, int]:
        """
        Get count of configs per entity type

        Returns:
            Dict mapping entity type to count
        """
        configs = self.list_configs()

        summary = {}
        for config in configs:
            entity_type = config.get('entity_type', 'unknown')
            summary[entity_type] = summary.get(entity_type, 0) + 1

        return summary
