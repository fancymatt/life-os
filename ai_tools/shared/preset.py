"""
Preset Manager

Manages user-editable presets (promoted artifacts from analyses).
Presets are curated, reusable building blocks stored as JSON files.
Uses UUID-based storage with display names for easy renaming.
"""

import json
import uuid
from pathlib import Path
from typing import Optional, List, Type, Dict, Any
from pydantic import BaseModel, ValidationError
from datetime import datetime


class PresetNotFoundError(Exception):
    """Raised when a preset doesn't exist"""
    pass


class PresetValidationError(Exception):
    """Raised when a preset fails validation"""
    pass


class ValidationResult(BaseModel):
    """Result from preset validation"""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class PresetManager:
    """
    Manages user-editable presets

    Presets are JSON files organized by tool type:
    - presets/outfits/fancy-suit.json
    - presets/visual-styles/dramatic.json
    - etc.

    Each preset includes:
    - _metadata: Provenance information
    - Fields specific to the tool type (OutfitSpec, VisualStyleSpec, etc.)
    """

    def __init__(self, presets_root: Optional[Path] = None):
        """
        Initialize the preset manager

        Args:
            presets_root: Root directory for presets (default: project_root/presets)
        """
        if presets_root is None:
            # Default to project root / presets
            self.presets_root = Path(__file__).parent.parent.parent / "presets"
        else:
            self.presets_root = Path(presets_root)

        # Ensure presets root exists
        self.presets_root.mkdir(parents=True, exist_ok=True)

    def _get_preset_dir(self, tool_type: str) -> Path:
        """Get the directory for a specific tool type's presets"""
        preset_dir = self.presets_root / tool_type
        preset_dir.mkdir(parents=True, exist_ok=True)
        return preset_dir

    def _get_preset_path(self, tool_type: str, preset_id: str) -> Path:
        """Get the full path to a preset file by ID"""
        # Remove .json extension if provided
        preset_id = preset_id.replace(".json", "")
        return self._get_preset_dir(tool_type) / f"{preset_id}.json"

    def save(
        self,
        tool_type: str,
        data: BaseModel,
        preset_id: Optional[str] = None,
        display_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> tuple[Path, str]:
        """
        Save a preset

        Args:
            tool_type: Type of tool (e.g., "outfits", "visual-styles")
            data: Pydantic model to save
            preset_id: Optional preset ID (generates UUID if not provided)
            display_name: Optional display name
            notes: Optional user notes to add to metadata

        Returns:
            Tuple of (Path to saved preset file, preset_id)
        """
        # Generate UUID if not provided
        if preset_id is None:
            preset_id = str(uuid.uuid4())

        preset_path = self._get_preset_path(tool_type, preset_id)

        # Convert to dict
        preset_dict = data.model_dump(mode='json')

        # Ensure metadata exists
        if "_metadata" not in preset_dict or preset_dict["_metadata"] is None:
            preset_dict["_metadata"] = {}

        # Update metadata with preset info
        preset_dict["_metadata"]["preset_id"] = preset_id
        if display_name is not None:
            preset_dict["_metadata"]["display_name"] = display_name
        if notes is not None:
            preset_dict["_metadata"]["notes"] = notes

        # Write with pretty printing
        with open(preset_path, 'w') as f:
            json.dump(preset_dict, f, indent=2, default=str)

        return preset_path, preset_id

    def load(
        self,
        tool_type: str,
        preset_id: str,
        spec_class: Type[BaseModel]
    ) -> BaseModel:
        """
        Load a preset by ID

        Args:
            tool_type: Type of tool (e.g., "outfits", "visual-styles")
            preset_id: Preset UUID
            spec_class: Pydantic model class to parse into

        Returns:
            Parsed Pydantic model instance

        Raises:
            PresetNotFoundError: If preset doesn't exist
            PresetValidationError: If preset fails validation
        """
        preset_path = self._get_preset_path(tool_type, preset_id)

        if not preset_path.exists():
            raise PresetNotFoundError(
                f"Preset not found: {tool_type}/{preset_id}\n"
                f"Looked at: {preset_path}"
            )

        # Load JSON
        with open(preset_path, 'r') as f:
            preset_data = json.load(f)

        # Parse into spec
        try:
            return spec_class.model_validate(preset_data)
        except ValidationError as e:
            raise PresetValidationError(
                f"Preset validation failed: {tool_type}/{preset_id}\n"
                f"Errors: {e.errors()}"
            )

    def exists(self, tool_type: str, preset_id: str) -> bool:
        """
        Check if a preset exists

        Args:
            tool_type: Type of tool
            preset_id: Preset UUID

        Returns:
            True if preset exists
        """
        preset_path = self._get_preset_path(tool_type, preset_id)
        return preset_path.exists()

    def list(self, tool_type: str) -> List[Dict[str, Any]]:
        """
        List all presets for a tool type with metadata

        Args:
            tool_type: Type of tool

        Returns:
            List of dicts with preset_id, display_name, and other metadata
        """
        preset_dir = self._get_preset_dir(tool_type)

        if not preset_dir.exists():
            return []

        # Get all .json files
        presets = []
        for preset_file in preset_dir.glob("*.json"):
            preset_id = preset_file.stem

            # Load metadata
            try:
                with open(preset_file, 'r') as f:
                    data = json.load(f)
                    metadata = data.get("_metadata", {})

                    presets.append({
                        "preset_id": preset_id,
                        "display_name": metadata.get("display_name"),
                        "created_at": metadata.get("created_at"),
                        "tool": metadata.get("tool"),
                        "notes": metadata.get("notes")
                    })
            except Exception:
                # Skip corrupted files
                continue

        return sorted(presets, key=lambda x: x.get("created_at") or "", reverse=True)

    def list_all(self) -> Dict[str, List[str]]:
        """
        List all presets across all tool types

        Returns:
            Dictionary mapping tool_type -> list of preset names
        """
        all_presets = {}

        # Check all subdirectories in presets root
        if self.presets_root.exists():
            for tool_dir in self.presets_root.iterdir():
                if tool_dir.is_dir():
                    tool_type = tool_dir.name
                    presets = self.list(tool_type)
                    if presets:
                        all_presets[tool_type] = presets

        return all_presets

    def delete(self, tool_type: str, preset_id: str) -> bool:
        """
        Delete a preset (and its preview image if it exists)

        Args:
            tool_type: Type of tool
            preset_id: Preset UUID

        Returns:
            True if deleted, False if didn't exist
        """
        preset_path = self._get_preset_path(tool_type, preset_id)

        if not preset_path.exists():
            return False

        # Delete preset file
        preset_path.unlink()

        # Also delete preview image if it exists
        self.delete_preview_image(tool_type, preset_id)

        return True

    def update_display_name(self, tool_type: str, preset_id: str, display_name: str) -> bool:
        """
        Update the display name of a preset

        Args:
            tool_type: Type of tool
            preset_id: Preset UUID
            display_name: New display name

        Returns:
            True if updated successfully

        Raises:
            PresetNotFoundError: If preset doesn't exist
        """
        preset_path = self._get_preset_path(tool_type, preset_id)

        if not preset_path.exists():
            raise PresetNotFoundError(f"Preset not found: {tool_type}/{preset_id}")

        # Load, update, and save
        with open(preset_path, 'r') as f:
            data = json.load(f)

        if "_metadata" not in data:
            data["_metadata"] = {}

        data["_metadata"]["display_name"] = display_name

        with open(preset_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return True

    def get_metadata(self, tool_type: str, preset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a preset without loading the full spec

        Args:
            tool_type: Type of tool
            preset_id: Preset UUID

        Returns:
            Metadata dict or None if no metadata
        """
        preset_path = self._get_preset_path(tool_type, preset_id)

        if not preset_path.exists():
            raise PresetNotFoundError(f"Preset not found: {tool_type}/{preset_id}")

        with open(preset_path, 'r') as f:
            preset_data = json.load(f)

        return preset_data.get("_metadata")

    def validate(
        self,
        tool_type: str,
        name: str,
        spec_class: Type[BaseModel]
    ) -> ValidationResult:
        """
        Validate a preset against its schema

        Args:
            tool_type: Type of tool
            name: Preset name
            spec_class: Pydantic model class for validation

        Returns:
            ValidationResult with errors/warnings
        """
        result = ValidationResult(valid=True)

        try:
            # Try to load the preset
            self.load(tool_type, name, spec_class)
        except PresetNotFoundError as e:
            result.valid = False
            result.errors.append(str(e))
        except PresetValidationError as e:
            result.valid = False
            result.errors.append(str(e))
        except Exception as e:
            result.valid = False
            result.errors.append(f"Unexpected error: {str(e)}")

        # Add warnings for missing optional metadata
        if result.valid:
            metadata = self.get_metadata(tool_type, name)
            if metadata:
                if not metadata.get("notes"):
                    result.warnings.append("No user notes in metadata")
                if not metadata.get("source_image"):
                    result.warnings.append("No source image recorded in metadata")

        return result

    def promote_from_dict(
        self,
        tool_type: str,
        name: str,
        data: Dict[str, Any],
        spec_class: Type[BaseModel],
        notes: Optional[str] = None
    ) -> Path:
        """
        Promote a dictionary (e.g., from cache) to a preset

        Args:
            tool_type: Type of tool
            name: Preset name
            data: Dictionary data to promote
            spec_class: Pydantic model class
            notes: Optional user notes

        Returns:
            Path to saved preset
        """
        # Parse into spec to validate
        try:
            spec = spec_class.model_validate(data)
        except ValidationError as e:
            raise PresetValidationError(f"Data validation failed: {e.errors()}")

        # Save with optional notes
        return self.save(tool_type, name, spec, notes=notes)

    def get_info(self, tool_type: str, name: str) -> Dict[str, Any]:
        """
        Get information about a preset

        Args:
            tool_type: Type of tool
            name: Preset name

        Returns:
            Dictionary with preset info
        """
        preset_path = self._get_preset_path(tool_type, name)

        if not preset_path.exists():
            raise PresetNotFoundError(f"Preset not found: {tool_type}/{name}")

        # Get file stats
        stat = preset_path.stat()

        info = {
            "name": name,
            "tool_type": tool_type,
            "path": str(preset_path),
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

        # Add metadata if present
        metadata = self.get_metadata(tool_type, name)
        if metadata:
            info["metadata"] = metadata

        return info

    def get_preview_image_path(self, tool_type: str, preset_id: str) -> Path:
        """
        Get the path where a preview image for a preset should be stored

        Args:
            tool_type: Type of tool
            preset_id: Preset UUID

        Returns:
            Path to preview image (may not exist yet)
        """
        preset_id = preset_id.replace(".json", "")
        preset_dir = self._get_preset_dir(tool_type)
        return preset_dir / f"{preset_id}_preview.png"

    def save_preview_image(
        self,
        tool_type: str,
        preset_id: str,
        image_data: bytes
    ) -> Path:
        """
        Save a preview image for a preset

        Args:
            tool_type: Type of tool
            preset_id: Preset UUID
            image_data: Image bytes (PNG format)

        Returns:
            Path to saved preview image
        """
        preview_path = self.get_preview_image_path(tool_type, preset_id)

        with open(preview_path, 'wb') as f:
            f.write(image_data)

        return preview_path

    def has_preview_image(self, tool_type: str, preset_id: str) -> bool:
        """
        Check if a preset has a preview image

        Args:
            tool_type: Type of tool
            preset_id: Preset UUID

        Returns:
            True if preview image exists
        """
        preview_path = self.get_preview_image_path(tool_type, preset_id)
        return preview_path.exists()

    def delete_preview_image(self, tool_type: str, preset_id: str) -> bool:
        """
        Delete a preset's preview image

        Args:
            tool_type: Type of tool
            preset_id: Preset UUID

        Returns:
            True if deleted, False if didn't exist
        """
        preview_path = self.get_preview_image_path(tool_type, preset_id)

        if not preview_path.exists():
            return False

        preview_path.unlink()
        return True


# Convenience functions

_default_manager: Optional[PresetManager] = None


def get_preset_manager() -> PresetManager:
    """Get the default preset manager (singleton)"""
    global _default_manager
    if _default_manager is None:
        _default_manager = PresetManager()
    return _default_manager


def save_preset(
    tool_type: str,
    data: BaseModel,
    preset_id: Optional[str] = None,
    display_name: Optional[str] = None,
    notes: Optional[str] = None
) -> tuple[Path, str]:
    """Quick function to save a preset"""
    return get_preset_manager().save(tool_type, data, preset_id, display_name, notes)


def load_preset(tool_type: str, preset_id: str, spec_class: Type[BaseModel]) -> BaseModel:
    """Quick function to load a preset"""
    return get_preset_manager().load(tool_type, preset_id, spec_class)


def list_presets(tool_type: str) -> List[Dict[str, Any]]:
    """Quick function to list presets"""
    return get_preset_manager().list(tool_type)


def preset_exists(tool_type: str, preset_id: str) -> bool:
    """Quick function to check if preset exists"""
    return get_preset_manager().exists(tool_type, preset_id)
