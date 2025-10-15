"""Preset Service

Manages preset CRUD operations.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.shared.preset import PresetManager
from api.config import settings


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
        "accessories"
    ]

    def __init__(self):
        """Initialize preset service"""
        self.preset_manager = PresetManager()
        self.presets_dir = settings.presets_dir

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
        notes: Optional[str] = None
    ) -> Path:
        """
        Create a new preset

        Args:
            category: Category name
            name: Preset name
            data: Preset data dict
            notes: Optional notes

        Returns:
            Path to created preset
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        # Check if preset already exists
        preset_path = self.presets_dir / category / f"{name}.json"
        if preset_path.exists():
            raise FileExistsError(f"Preset already exists: {category}/{name}")

        # Save preset
        return self.preset_manager.save(category, name, data, notes=notes)

    def update_preset(
        self,
        category: str,
        preset_id: str,
        data: Dict[str, Any],
        display_name: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """
        Update existing preset by ID

        Args:
            category: Category name
            preset_id: Preset UUID
            data: Updated preset data
            display_name: Optional new display name
            notes: Optional notes
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

    def delete_preset(self, category: str, preset_id: str) -> bool:
        """
        Delete a preset by ID

        Args:
            category: Category name
            preset_id: Preset UUID

        Returns:
            True if deleted
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        preset_path = self.presets_dir / category / f"{preset_id}.json"
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {category}/{preset_id}")

        preset_path.unlink()
        return True

    def duplicate_preset(
        self,
        category: str,
        source_name: str,
        new_name: str
    ) -> Path:
        """
        Duplicate a preset

        Args:
            category: Category name
            source_name: Source preset name
            new_name: New preset name

        Returns:
            Path to duplicated preset
        """
        # Get source data
        data = self.get_preset(category, source_name)

        # Remove metadata if present
        data.pop("_metadata", None)
        data.pop("metadata", None)

        # Create new preset
        return self.create_preset(category, new_name, data, notes=f"Duplicated from {source_name}")

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
