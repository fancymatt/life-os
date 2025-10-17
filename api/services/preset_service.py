"""Preset Service

Manages preset CRUD operations.
"""

import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.shared.preset import PresetManager
from ai_tools.outfit_visualizer.tool import OutfitVisualizer
from ai_tools.shared.visualizer import PresetVisualizer
from ai_capabilities.specs import (
    OutfitSpec,
    VisualStyleSpec,
    ArtStyleSpec,
    HairStyleSpec,
    HairColorSpec,
    MakeupSpec,
    ExpressionSpec,
    AccessoriesSpec,
    CharacterAppearanceSpec
)
from api.config import settings
from api.logging_config import (
    log_background_task_start,
    log_background_task_success,
    log_background_task_error
)


class PresetService:
    """Service for managing presets"""

    CATEGORIES = [
        "outfits",
        "visual_styles",
        "art_styles",
        "hair_styles",
        "hair_colors",
        "makeup",
        "expressions",
        "accessories",
        "character_appearance",
        "story_themes",
        "story_audiences",
        "story_prose_styles"
    ]

    def __init__(self):
        """Initialize preset service"""
        self.preset_manager = PresetManager()
        self.presets_dir = settings.presets_dir
        self.outfit_visualizer = OutfitVisualizer()
        self.generic_visualizer = PresetVisualizer()

    def _generate_preview(self, category: str, preset_id: str, data: Dict[str, Any]):
        """
        Generate a preview image for any preset type

        Args:
            category: Category name (outfits, visual_styles, etc.)
            preset_id: Preset UUID
            data: Preset data dict
        """
        try:
            # Use outfit visualizer for outfits (special case)
            if category == "outfits":
                outfit_spec = OutfitSpec(**data)
                viz_path = self.outfit_visualizer.visualize(
                    outfit=outfit_spec,
                    output_dir=self.presets_dir / category,
                    preset_id=preset_id
                )
            else:
                # Use generic visualizer for all other types
                spec_class_map = {
                    "visual_styles": VisualStyleSpec,
                    "art_styles": ArtStyleSpec,
                    "hair_styles": HairStyleSpec,
                    "hair_colors": HairColorSpec,
                    "makeup": MakeupSpec,
                    "expressions": ExpressionSpec,
                    "accessories": AccessoriesSpec,
                    "character_appearance": CharacterAppearanceSpec
                }

                if category not in spec_class_map:
                    print(f"⚠️  No visualizer for category: {category}")
                    return

                spec_class = spec_class_map[category]
                spec = spec_class(**data)

                viz_path = self.generic_visualizer.visualize(
                    spec_type=category,
                    spec=spec,
                    output_dir=self.presets_dir / category,
                    preset_id=preset_id
                )

            print(f"✅ Generated preview: {viz_path}")
        except Exception as e:
            # Don't fail the whole operation if visualization fails
            print(f"⚠️  Preview generation failed: {e}")

    def _generate_preview_safe(self, category: str, preset_id: str, data: Dict[str, Any]):
        """
        Safe wrapper for preview generation with comprehensive error logging

        Args:
            category: Category name
            preset_id: Preset UUID
            data: Preset data dict
        """
        task_name = "preview_generation"
        start_time = time.time()

        log_background_task_start(
            task_name,
            category=category,
            preset_id=preset_id
        )

        try:
            self._generate_preview(category, preset_id, data)
            duration_ms = (time.time() - start_time) * 1000
            log_background_task_success(
                task_name,
                duration_ms=duration_ms,
                category=category,
                preset_id=preset_id
            )
        except Exception as e:
            log_background_task_error(
                task_name,
                error=e,
                category=category,
                preset_id=preset_id
            )

    def list_categories(self) -> List[str]:
        """List all preset categories"""
        return self.CATEGORIES

    def list_presets(self, category: str) -> List[Dict[str, Any]]:
        """
        List all presets in a category

        Args:
            category: Category name

        Returns:
            List of preset info dicts with preset_id and display_name
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        # Use PresetManager's list method which returns metadata
        presets_with_metadata = self.preset_manager.list(category)

        # Add category to each preset
        for preset in presets_with_metadata:
            preset["category"] = category

        return presets_with_metadata

    def get_preset(self, category: str, preset_id: str) -> Dict[str, Any]:
        """
        Get preset data by ID

        Args:
            category: Category name
            preset_id: Preset UUID

        Returns:
            Preset data dict
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        preset_path = self.presets_dir / category / f"{preset_id}.json"
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {category}/{preset_id}")

        with open(preset_path) as f:
            return json.load(f)

    def create_preset(
        self,
        category: str,
        name: str,
        data: Dict[str, Any],
        notes: Optional[str] = None,
        background_tasks = None
    ) -> tuple[Path, str]:
        """
        Create a new preset

        Args:
            category: Category name
            name: Display name for the preset
            data: Preset data dict
            notes: Optional notes
            background_tasks: Optional FastAPI BackgroundTasks for async visualization

        Returns:
            Tuple of (Path to created preset, preset_id)
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        # Check if a preset with this display name already exists
        existing_presets = self.list_presets(category)
        for preset in existing_presets:
            if preset.get("display_name") == name:
                raise FileExistsError(f"Preset with display name '{name}' already exists in {category}")

        # Get the appropriate spec class for categories that have them
        spec_class_map = {
            "outfits": OutfitSpec,
            "visual_styles": VisualStyleSpec,
            "art_styles": ArtStyleSpec,
            "hair_styles": HairStyleSpec,
            "hair_colors": HairColorSpec,
            "makeup": MakeupSpec,
            "expressions": ExpressionSpec,
            "accessories": AccessoriesSpec,
            "character_appearance": CharacterAppearanceSpec
        }

        # For categories with spec classes, validate with Pydantic
        # For story presets (themes, audiences, prose_styles), save as raw JSON
        if category in spec_class_map:
            # Convert dict to spec instance for validation
            spec_class = spec_class_map[category]
            spec = spec_class(**data)
            data_to_save = spec
        else:
            # Story presets don't have spec classes - save raw data
            data_to_save = data

        # Save preset with generated UUID, using name as display_name
        preset_path, preset_id = self.preset_manager.save(
            tool_type=category,
            data=data_to_save,
            preset_id=None,  # Generate new UUID
            display_name=name,
            notes=notes
        )

        # Generate preview for the new preset
        if background_tasks is not None:
            # Run visualization in background
            background_tasks.add_task(
                self._generate_preview_safe,
                category,
                preset_id,
                data
            )
            print(f"🎨 Queued preview generation for new preset {preset_id}")
        else:
            # Fallback to synchronous generation
            self._generate_preview(category, preset_id, data)

        return preset_path, preset_id

    def update_preset(
        self,
        category: str,
        preset_id: str,
        data: Dict[str, Any],
        display_name: Optional[str] = None,
        notes: Optional[str] = None,
        background_tasks = None
    ):
        """
        Update existing preset by ID

        Args:
            category: Category name
            preset_id: Preset UUID
            data: Updated preset data
            display_name: Optional new display name
            notes: Optional notes
            background_tasks: Optional FastAPI BackgroundTasks for async visualization
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        # Check if preset exists
        preset_path = self.presets_dir / category / f"{preset_id}.json"
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {category}/{preset_id}")

        # Load existing data
        with open(preset_path) as f:
            existing_data = json.load(f)

        # Check if data actually changed (not just metadata) - BEFORE updating
        should_generate_preview = False
        has_preview = self.preset_manager.has_preview_image(category, preset_id)

        if category == "outfits":
            # Compare outfit-specific fields (exclude _metadata)
            old_outfit_data = {k: v for k, v in existing_data.items() if k != "_metadata"}
            new_outfit_data = {k: v for k, v in data.items() if k != "_metadata"}
            data_changed = old_outfit_data != new_outfit_data
            should_generate_preview = data_changed or not has_preview
            print(f"🔍 Outfit - data changed: {data_changed}, has preview: {has_preview}, will generate: {should_generate_preview}")
        elif category in ["visual_styles", "art_styles", "hair_styles", "hair_colors", "makeup", "expressions", "accessories"]:
            # For non-outfit categories, compare data (excluding metadata)
            old_data = {k: v for k, v in existing_data.items() if k != "_metadata"}
            new_data = {k: v for k, v in data.items() if k != "_metadata"}
            data_changed = old_data != new_data
            should_generate_preview = data_changed or not has_preview
            print(f"🔍 {category} - data changed: {data_changed}, has preview: {has_preview}, will generate: {should_generate_preview}")

        # Update fields
        existing_data.update(data)

        # Update metadata
        if "_metadata" not in existing_data:
            existing_data["_metadata"] = {}

        if display_name is not None:
            existing_data["_metadata"]["display_name"] = display_name
        if notes is not None:
            existing_data["_metadata"]["notes"] = notes

        # Write back
        with open(preset_path, 'w') as f:
            json.dump(existing_data, f, indent=2, default=str)

        if should_generate_preview:
            if background_tasks is not None:
                # Run visualization in background
                background_tasks.add_task(
                    self._generate_preview_safe,
                    category,
                    preset_id,
                    existing_data
                )
                print(f"🎨 Queued preview generation for {preset_id}")
            else:
                # Fallback to synchronous generation
                self._generate_preview(category, preset_id, existing_data)

    def delete_preset(self, category: str, preset_id: str) -> bool:
        """
        Delete a preset by ID (and its preview image if applicable)

        Args:
            category: Category name
            preset_id: Preset UUID

        Returns:
            True if deleted
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        # Use preset_manager's delete method which also deletes preview images
        if not self.preset_manager.exists(category, preset_id):
            raise FileNotFoundError(f"Preset not found: {category}/{preset_id}")

        return self.preset_manager.delete(category, preset_id)

    def duplicate_preset(
        self,
        category: str,
        source_name: str,
        new_name: str,
        background_tasks = None
    ) -> Path:
        """
        Duplicate a preset

        Args:
            category: Category name
            source_name: Source preset name
            new_name: New preset name
            background_tasks: Optional FastAPI BackgroundTasks for async visualization

        Returns:
            Path to duplicated preset
        """
        # Get source data
        data = self.get_preset(category, source_name)

        # Remove metadata if present
        data.pop("_metadata", None)
        data.pop("metadata", None)

        # Create new preset (returns tuple now)
        preset_path, preset_id = self.create_preset(
            category,
            new_name,
            data,
            notes=f"Duplicated from {source_name}",
            background_tasks=background_tasks
        )
        return preset_path

    def get_total_presets(self) -> int:
        """Get total number of presets across all categories"""
        total = 0
        for category in self.CATEGORIES:
            total += len(self.list_presets(category))
        return total

    def validate_preset_exists(self, category: str, name: str) -> bool:
        """Check if a preset exists"""
        if category not in self.CATEGORIES:
            return False

        preset_path = self.presets_dir / category / f"{name}.json"
        return preset_path.exists()
