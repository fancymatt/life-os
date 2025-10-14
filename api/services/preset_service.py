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
            List of preset info dicts
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        category_dir = self.presets_dir / category
        if not category_dir.exists():
            return []

        presets = []
        for preset_file in category_dir.glob("*.json"):
            try:
                stat = preset_file.stat()
                with open(preset_file) as f:
                    data = json.load(f)

                presets.append({
                    "name": preset_file.stem,
                    "category": category,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "size_bytes": stat.st_size,
                    "has_metadata": "_metadata" in data or "metadata" in data
                })
            except Exception:
                continue

        return sorted(presets, key=lambda x: x["name"])

    def get_preset(self, category: str, name: str) -> Dict[str, Any]:
        """
        Get preset data

        Args:
            category: Category name
            name: Preset name

        Returns:
            Preset data dict
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        preset_path = self.presets_dir / category / f"{name}.json"
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {category}/{name}")

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
        name: str,
        data: Dict[str, Any],
        notes: Optional[str] = None
    ) -> Path:
        """
        Update existing preset

        Args:
            category: Category name
            name: Preset name
            data: Updated preset data
            notes: Optional notes

        Returns:
            Path to updated preset
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        # Check if preset exists
        preset_path = self.presets_dir / category / f"{name}.json"
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {category}/{name}")

        # Update preset
        return self.preset_manager.save(category, name, data, notes=notes)

    def delete_preset(self, category: str, name: str) -> bool:
        """
        Delete a preset

        Args:
            category: Category name
            name: Preset name

        Returns:
            True if deleted
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        preset_path = self.presets_dir / category / f"{name}.json"
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {category}/{name}")

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
