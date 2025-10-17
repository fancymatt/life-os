"""
Integration tests for Story Preset API

Tests the full CRUD lifecycle for story themes, audiences, and prose styles.
These presets use free-form JSON (no Pydantic validation) unlike analyzer presets.
"""

import pytest
import json
from pathlib import Path
from api.services.preset_service import PresetService
from ai_tools.shared.preset import PresetManager


@pytest.fixture
def preset_service(temp_dir):
    """Create a preset service with temporary storage"""
    presets_root = temp_dir / "presets"
    preset_manager = PresetManager(presets_root=presets_root)
    return PresetService(preset_manager=preset_manager)


@pytest.fixture
def sample_story_theme_data():
    """Sample story theme data matching the modal structure"""
    return {
        "suggested_name": "Body Horror",
        "description": "A story theme exploring transformation and the grotesque",
        "setting_guidance": "Urban or isolated settings with clinical/organic contrast",
        "tone": "Unsettling, visceral",
        "common_elements": ["transformation", "body modification", "medical horror"],
        "story_structure_notes": "Gradual escalation of body horror elements",
        "world_building": "Contemporary setting with undertones of the uncanny"
    }


@pytest.fixture
def sample_story_audience_data():
    """Sample story audience data"""
    return {
        "suggested_name": "Young Adult",
        "description": "Teen and young adult readers",
        "age_range": "13-18",
        "reading_level": "8th-10th grade",
        "content_considerations": "Age-appropriate language and themes",
        "engagement_style": "Fast-paced with relatable protagonists"
    }


@pytest.fixture
def sample_prose_style_data():
    """Sample prose style data"""
    return {
        "suggested_name": "Lyrical Literary",
        "description": "Poetic and evocative prose",
        "tone": "Contemplative, elegant",
        "pacing": "Measured, with room for reflection",
        "vocabulary_level": "Advanced",
        "sentence_structure": "Varied, with longer flowing sentences",
        "narrative_voice": "Third person limited, intimate"
    }


class TestStoryThemePresets:
    """Test story theme CRUD operations"""

    def test_create_story_theme(self, preset_service, sample_story_theme_data, temp_dir):
        """Test creating a new story theme preset"""
        # Create preset
        preset_path, preset_id = preset_service.create_preset(
            category="story_themes",
            name="Body Horror",
            data=sample_story_theme_data,
            notes="Created via integration test"
        )

        # Verify file was created
        assert preset_path.exists()
        assert preset_id is not None

        # Verify content
        with open(preset_path, 'r') as f:
            saved_data = json.load(f)

        assert saved_data["suggested_name"] == "Body Horror"
        assert saved_data["description"] == "A story theme exploring transformation and the grotesque"
        assert saved_data["tone"] == "Unsettling, visceral"
        assert "transformation" in saved_data["common_elements"]

        # Verify metadata
        assert "_metadata" in saved_data
        assert saved_data["_metadata"]["preset_id"] == preset_id
        assert saved_data["_metadata"]["display_name"] == "Body Horror"
        assert saved_data["_metadata"]["notes"] == "Created via integration test"

    def test_list_story_themes(self, preset_service, sample_story_theme_data, temp_dir):
        """Test listing story theme presets"""
        # Create multiple presets
        preset_service.create_preset("story_themes", "Theme 1", sample_story_theme_data)
        preset_service.create_preset("story_themes", "Theme 2", sample_story_theme_data)

        # List presets
        presets = preset_service.list_presets("story_themes")

        assert len(presets) == 2
        assert any(p["display_name"] == "Theme 1" for p in presets)
        assert any(p["display_name"] == "Theme 2" for p in presets)

    def test_get_story_theme(self, preset_service, sample_story_theme_data):
        """Test retrieving a specific story theme"""
        # Create preset
        _, preset_id = preset_service.create_preset(
            "story_themes",
            "Body Horror",
            sample_story_theme_data
        )

        # Get preset
        retrieved = preset_service.get_preset("story_themes", preset_id)

        assert retrieved["suggested_name"] == "Body Horror"
        assert retrieved["tone"] == "Unsettling, visceral"
        assert "_metadata" in retrieved

    def test_update_story_theme(self, preset_service, sample_story_theme_data):
        """Test updating a story theme preset"""
        # Create preset
        _, preset_id = preset_service.create_preset(
            "story_themes",
            "Body Horror",
            sample_story_theme_data
        )

        # Update data
        updated_data = sample_story_theme_data.copy()
        updated_data["tone"] = "Terrifying, visceral"
        updated_data["common_elements"] = ["transformation", "mutation", "medical horror", "cosmic horror"]

        preset_service.update_preset(
            "story_themes",
            preset_id,
            updated_data,
            display_name="Body Horror - Updated"
        )

        # Verify update
        retrieved = preset_service.get_preset("story_themes", preset_id)
        assert retrieved["tone"] == "Terrifying, visceral"
        assert "cosmic horror" in retrieved["common_elements"]
        assert retrieved["_metadata"]["display_name"] == "Body Horror - Updated"

    def test_delete_story_theme(self, preset_service, sample_story_theme_data):
        """Test deleting a story theme preset"""
        # Create preset
        preset_path, preset_id = preset_service.create_preset(
            "story_themes",
            "Body Horror",
            sample_story_theme_data
        )

        assert preset_path.exists()

        # Delete preset
        preset_service.delete_preset("story_themes", preset_id)

        # Verify deletion
        assert not preset_path.exists()

        # Verify not in list
        presets = preset_service.list_presets("story_themes")
        assert not any(p["preset_id"] == preset_id for p in presets)

    def test_create_with_minimal_fields(self, preset_service):
        """Test creating story theme with minimal required fields"""
        minimal_data = {
            "suggested_name": "Minimal Theme",
            "description": "A minimal theme"
        }

        preset_path, preset_id = preset_service.create_preset(
            "story_themes",
            "Minimal Theme",
            minimal_data
        )

        assert preset_path.exists()

        # Verify it saved correctly
        retrieved = preset_service.get_preset("story_themes", preset_id)
        assert retrieved["suggested_name"] == "Minimal Theme"
        assert retrieved["description"] == "A minimal theme"


class TestStoryAudiencePresets:
    """Test story audience CRUD operations"""

    def test_create_story_audience(self, preset_service, sample_story_audience_data):
        """Test creating a new story audience preset"""
        preset_path, preset_id = preset_service.create_preset(
            "story_audiences",
            "Young Adult",
            sample_story_audience_data,
            notes="YA audience preset"
        )

        assert preset_path.exists()

        # Verify content
        with open(preset_path, 'r') as f:
            saved_data = json.load(f)

        assert saved_data["suggested_name"] == "Young Adult"
        assert saved_data["age_range"] == "13-18"
        assert saved_data["reading_level"] == "8th-10th grade"

    def test_list_story_audiences(self, preset_service, sample_story_audience_data):
        """Test listing story audience presets"""
        preset_service.create_preset("story_audiences", "YA", sample_story_audience_data)
        preset_service.create_preset("story_audiences", "Adult", sample_story_audience_data)

        presets = preset_service.list_presets("story_audiences")

        assert len(presets) == 2


class TestProseStylePresets:
    """Test prose style CRUD operations"""

    def test_create_prose_style(self, preset_service, sample_prose_style_data):
        """Test creating a new prose style preset"""
        preset_path, preset_id = preset_service.create_preset(
            "story_prose_styles",
            "Lyrical Literary",
            sample_prose_style_data
        )

        assert preset_path.exists()

        # Verify content
        with open(preset_path, 'r') as f:
            saved_data = json.load(f)

        assert saved_data["suggested_name"] == "Lyrical Literary"
        assert saved_data["tone"] == "Contemplative, elegant"
        assert saved_data["narrative_voice"] == "Third person limited, intimate"

    def test_list_prose_styles(self, preset_service, sample_prose_style_data):
        """Test listing prose style presets"""
        preset_service.create_preset("story_prose_styles", "Style 1", sample_prose_style_data)
        preset_service.create_preset("story_prose_styles", "Style 2", sample_prose_style_data)

        presets = preset_service.list_presets("story_prose_styles")

        assert len(presets) == 2


class TestStoryPresetValidation:
    """Test validation and error handling for story presets"""

    def test_create_with_empty_data(self, preset_service):
        """Test that empty data is handled gracefully"""
        empty_data = {}

        # Should not raise an error (story presets don't have strict validation)
        preset_path, preset_id = preset_service.create_preset(
            "story_themes",
            "Empty Theme",
            empty_data
        )

        assert preset_path.exists()

    def test_get_nonexistent_preset(self, preset_service):
        """Test retrieving a preset that doesn't exist"""
        with pytest.raises(FileNotFoundError):
            preset_service.get_preset("story_themes", "nonexistent-id")

    def test_delete_nonexistent_preset(self, preset_service):
        """Test deleting a preset that doesn't exist"""
        with pytest.raises(FileNotFoundError):
            preset_service.delete_preset("story_themes", "nonexistent-id")

    def test_update_nonexistent_preset(self, preset_service, sample_story_theme_data):
        """Test updating a preset that doesn't exist"""
        with pytest.raises(FileNotFoundError):
            preset_service.update_preset(
                "story_themes",
                "nonexistent-id",
                sample_story_theme_data
            )


class TestStoryPresetFieldStructure:
    """Test that created presets have the correct field structure"""

    def test_theme_has_all_expected_fields(self, preset_service, sample_story_theme_data):
        """Test that story themes have all expected fields from the modal"""
        _, preset_id = preset_service.create_preset(
            "story_themes",
            "Complete Theme",
            sample_story_theme_data
        )

        retrieved = preset_service.get_preset("story_themes", preset_id)

        # Check all expected fields exist
        expected_fields = [
            "suggested_name",
            "description",
            "setting_guidance",
            "tone",
            "common_elements",
            "story_structure_notes",
            "world_building"
        ]

        for field in expected_fields:
            assert field in retrieved, f"Missing expected field: {field}"

    def test_audience_has_all_expected_fields(self, preset_service, sample_story_audience_data):
        """Test that story audiences have all expected fields from the modal"""
        _, preset_id = preset_service.create_preset(
            "story_audiences",
            "Complete Audience",
            sample_story_audience_data
        )

        retrieved = preset_service.get_preset("story_audiences", preset_id)

        expected_fields = [
            "suggested_name",
            "description",
            "age_range",
            "reading_level",
            "content_considerations",
            "engagement_style"
        ]

        for field in expected_fields:
            assert field in retrieved, f"Missing expected field: {field}"

    def test_prose_style_has_all_expected_fields(self, preset_service, sample_prose_style_data):
        """Test that prose styles have all expected fields from the modal"""
        _, preset_id = preset_service.create_preset(
            "story_prose_styles",
            "Complete Style",
            sample_prose_style_data
        )

        retrieved = preset_service.get_preset("story_prose_styles", preset_id)

        expected_fields = [
            "suggested_name",
            "description",
            "tone",
            "pacing",
            "vocabulary_level",
            "sentence_structure",
            "narrative_voice"
        ]

        for field in expected_fields:
            assert field in retrieved, f"Missing expected field: {field}"
