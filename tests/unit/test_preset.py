"""
Tests for ai-tools/shared/preset.py (PresetManager)
"""

import pytest
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.shared.preset import (
    PresetManager,
    PresetNotFoundError,
    PresetValidationError,
    ValidationResult,
)
from ai_capabilities.specs import OutfitSpec, VisualStyleSpec, SpecMetadata


@pytest.mark.unit
class TestPresetManager:
    """Tests for PresetManager"""

    def test_init_with_custom_root(self, presets_dir):
        """Test initialization with custom presets root"""
        manager = PresetManager(presets_root=presets_dir)
        assert manager.presets_root == presets_dir
        assert manager.presets_root.exists()

    def test_get_preset_dir(self, presets_dir):
        """Test getting preset directory for a tool type"""
        manager = PresetManager(presets_root=presets_dir)
        outfit_dir = manager._get_preset_dir("outfits")

        assert outfit_dir.exists()
        assert outfit_dir.name == "outfits"
        assert outfit_dir.parent == presets_dir

    def test_save_preset(self, presets_dir, sample_outfit_data):
        """Test saving a preset"""
        manager = PresetManager(presets_root=presets_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        preset_path, preset_id = manager.save("outfits", outfit, "test-suit")

        assert preset_path.exists()
        assert preset_path.name == "test-suit.json"
        assert preset_id == "test-suit"

        # Verify content
        with open(preset_path) as f:
            data = json.load(f)
            assert data["style_genre"] == "modern professional"

    def test_save_preset_with_notes(self, presets_dir, sample_outfit_data_with_metadata):
        """Test saving preset with notes"""
        manager = PresetManager(presets_root=presets_dir)
        outfit = OutfitSpec(**sample_outfit_data_with_metadata)

        preset_path, preset_id = manager.save("outfits", outfit, "test-suit", notes="Custom notes")

        with open(preset_path) as f:
            data = json.load(f)
            assert data["_metadata"]["notes"] == "Custom notes"

    def test_load_preset(self, presets_dir, sample_outfit_data):
        """Test loading a preset"""
        manager = PresetManager(presets_root=presets_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        # Save first
        manager.save("outfits", outfit, "test-suit")

        # Load
        loaded_outfit = manager.load("outfits", "test-suit", OutfitSpec)

        assert loaded_outfit.style_genre == outfit.style_genre
        assert len(loaded_outfit.clothing_items) == len(outfit.clothing_items)

    def test_load_nonexistent_preset(self, presets_dir):
        """Test loading a preset that doesn't exist"""
        manager = PresetManager(presets_root=presets_dir)

        with pytest.raises(PresetNotFoundError):
            manager.load("outfits", "nonexistent", OutfitSpec)

    def test_exists(self, presets_dir, sample_outfit_data):
        """Test checking if preset exists"""
        manager = PresetManager(presets_root=presets_dir)

        assert not manager.exists("outfits", "test-suit")

        outfit = OutfitSpec(**sample_outfit_data)
        manager.save("outfits", outfit, "test-suit")

        assert manager.exists("outfits", "test-suit")

    def test_list_presets(self, presets_dir, sample_outfit_data):
        """Test listing presets"""
        manager = PresetManager(presets_root=presets_dir)

        # Initially empty
        assert manager.list("outfits") == []

        # Add some presets
        outfit = OutfitSpec(**sample_outfit_data)
        manager.save("outfits", outfit, "suit-1")
        manager.save("outfits", outfit, "suit-2")
        manager.save("outfits", outfit, "suit-3")

        presets = manager.list("outfits")
        assert len(presets) == 3
        preset_ids = [p["preset_id"] for p in presets]
        assert "suit-1" in preset_ids
        assert "suit-2" in preset_ids
        assert "suit-3" in preset_ids

    def test_list_all_presets(self, presets_dir, sample_outfit_data, sample_visual_style_data):
        """Test listing all presets across tool types"""
        manager = PresetManager(presets_root=presets_dir)

        # Add presets of different types
        outfit = OutfitSpec(**sample_outfit_data)
        style = VisualStyleSpec(**sample_visual_style_data)

        manager.save("outfits", outfit, "suit")
        manager.save("visual-styles", style, "dramatic")

        all_presets = manager.list_all()

        assert "outfits" in all_presets
        assert "visual-styles" in all_presets
        # list_all returns list of dicts
        outfit_ids = [p["preset_id"] for p in all_presets["outfits"]]
        style_ids = [p["preset_id"] for p in all_presets["visual-styles"]]
        assert "suit" in outfit_ids
        assert "dramatic" in style_ids

    def test_delete_preset(self, presets_dir, sample_outfit_data):
        """Test deleting a preset"""
        manager = PresetManager(presets_root=presets_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        manager.save("outfits", outfit, "test-suit")
        assert manager.exists("outfits", "test-suit")

        # Delete
        result = manager.delete("outfits", "test-suit")
        assert result is True
        assert not manager.exists("outfits", "test-suit")

        # Delete nonexistent
        result = manager.delete("outfits", "test-suit")
        assert result is False

    def test_get_metadata(self, presets_dir, sample_outfit_data):
        """Test getting preset metadata"""
        manager = PresetManager(presets_root=presets_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        # Manually assign metadata (Pydantic v2 doesn't allow _ fields in __init__)
        outfit._metadata = SpecMetadata(
            tool="outfit-analyzer",
            model_used="gemini-2.0-flash"
        )

        manager.save("outfits", outfit, "test-suit")

        metadata = manager.get_metadata("outfits", "test-suit")
        assert metadata is not None
        assert metadata["tool"] == "outfit-analyzer"
        assert metadata["model_used"] == "gemini-2.0-flash"

    def test_validate_preset(self, presets_dir, sample_outfit_data):
        """Test validating a preset"""
        manager = PresetManager(presets_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        manager.save("outfits", outfit, "test-suit")

        result = manager.validate("outfits", "test-suit", OutfitSpec)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_nonexistent_preset(self, presets_dir):
        """Test validating preset that doesn't exist"""
        manager = PresetManager(presets_dir)

        result = manager.validate("outfits", "nonexistent", OutfitSpec)
        assert result.valid is False
        assert len(result.errors) > 0

    def test_validate_invalid_preset(self, presets_dir):
        """Test validating preset with invalid data"""
        manager = PresetManager(presets_dir)

        # Create invalid preset manually
        preset_path = manager._get_preset_path("outfits", "invalid")
        preset_path.parent.mkdir(parents=True, exist_ok=True)

        with open(preset_path, 'w') as f:
            json.dump({"invalid": "data"}, f)

        result = manager.validate("outfits", "invalid", OutfitSpec)
        assert result.valid is False
        assert len(result.errors) > 0

    def test_promote_from_dict(self, presets_dir, sample_outfit_data):
        """Test promoting a dict to preset"""
        manager = PresetManager(presets_dir)

        preset_path = manager.promote_from_dict(
            "outfits",
            "promoted-suit",
            sample_outfit_data,
            OutfitSpec,
            notes="Promoted from cache"
        )

        assert preset_path.exists()

        # Load and verify
        outfit = manager.load("outfits", "promoted-suit", OutfitSpec)
        assert outfit.style_genre == "modern professional"

    def test_promote_from_invalid_dict(self, presets_dir):
        """Test promoting invalid dict raises error"""
        manager = PresetManager(presets_dir)

        with pytest.raises(PresetValidationError):
            manager.promote_from_dict(
                "outfits",
                "invalid",
                {"invalid": "data"},
                OutfitSpec
            )

    def test_get_info(self, presets_dir, sample_outfit_data):
        """Test getting preset info"""
        manager = PresetManager(presets_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        # Manually assign metadata (Pydantic v2 doesn't allow _ fields in __init__)
        outfit._metadata = SpecMetadata(
            tool="outfit-analyzer",
            model_used="gemini-2.0-flash"
        )

        manager.save("outfits", outfit, "test-suit")

        info = manager.get_info("outfits", "test-suit")

        assert info["name"] == "test-suit"
        assert info["tool_type"] == "outfits"
        assert "path" in info
        assert "size_bytes" in info
        assert "modified" in info
        assert "metadata" in info
        assert info["metadata"]["tool"] == "outfit-analyzer"

    def test_preset_name_sanitization(self, presets_dir, sample_outfit_data):
        """Test that preset names are sanitized"""
        manager = PresetManager(presets_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        # Name with spaces and slashes
        manager.save("outfits", outfit, "my fancy suit")

        # Should be converted to safe filename
        assert manager.exists("outfits", "my-fancy-suit")

    def test_preset_with_json_extension(self, presets_dir, sample_outfit_data):
        """Test saving preset with .json extension (should be removed)"""
        manager = PresetManager(presets_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        manager.save("outfits", outfit, "test-suit.json")

        # Should exist without .json in name
        assert manager.exists("outfits", "test-suit")

    def test_round_trip(self, presets_dir, sample_outfit_data):
        """Test complete save/load round trip preserves data"""
        manager = PresetManager(presets_dir)
        original = OutfitSpec(**sample_outfit_data)

        # Manually assign metadata (Pydantic v2 doesn't allow _ fields in __init__)
        original._metadata = SpecMetadata(
            tool="outfit-analyzer",
            model_used="gemini-2.0-flash"
        )

        manager.save("outfits", original, "round-trip-test")
        loaded = manager.load("outfits", "round-trip-test", OutfitSpec)

        # Check all fields match
        assert loaded.style_genre == original.style_genre
        assert loaded.formality == original.formality
        assert loaded.aesthetic == original.aesthetic
        assert len(loaded.clothing_items) == len(original.clothing_items)

        # Check metadata
        assert loaded._metadata.tool == original._metadata.tool
        assert loaded._metadata.model_used == original._metadata.model_used


@pytest.mark.unit
class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_get_preset_manager_singleton(self):
        """Test that get_preset_manager returns singleton"""
        from ai_tools.shared.preset import get_preset_manager

        manager1 = get_preset_manager()
        manager2 = get_preset_manager()

        assert manager1 is manager2
