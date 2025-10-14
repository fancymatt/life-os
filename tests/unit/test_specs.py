"""
Tests for ai-capabilities/specs.py (Pydantic models)
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import (
    SpecMetadata,
    ClothingItem,
    OutfitSpec,
    VisualStyleSpec,
    ArtStyleSpec,
    HairStyleSpec,
    HairColorSpec,
    MakeupSpec,
    ExpressionSpec,
    AccessoriesSpec,
    ImageGenerationRequest,
    ImageGenerationResult,
    VideoPromptSpec,
    VideoGenerationRequest,
    VideoGenerationResult,
    AspectRatio,
    VideoModel,
)


@pytest.mark.unit
class TestSpecMetadata:
    """Tests for SpecMetadata"""

    def test_create_metadata(self):
        """Test creating metadata"""
        metadata = SpecMetadata(
            tool="test-tool",
            model_used="gemini-2.0-flash"
        )
        assert metadata.tool == "test-tool"
        assert metadata.model_used == "gemini-2.0-flash"
        assert isinstance(metadata.created_at, datetime)
        assert metadata.tool_version == "1.0.0"

    def test_metadata_with_optional_fields(self):
        """Test metadata with optional fields"""
        metadata = SpecMetadata(
            tool="test-tool",
            model_used="gemini-2.0-flash",
            source_image="test.jpg",
            source_hash="abc123",
            notes="Test notes"
        )
        assert metadata.source_image == "test.jpg"
        assert metadata.source_hash == "abc123"
        assert metadata.notes == "Test notes"


@pytest.mark.unit
class TestOutfitSpec:
    """Tests for OutfitSpec"""

    def test_create_outfit_spec(self, sample_outfit_data):
        """Test creating a valid outfit spec"""
        outfit = OutfitSpec(**sample_outfit_data)
        assert len(outfit.clothing_items) == 2
        assert outfit.style_genre == "modern professional"
        assert outfit.formality == "business formal"

    def test_outfit_spec_with_metadata(self, sample_outfit_data_with_metadata):
        """Test outfit spec with metadata"""
        outfit = OutfitSpec(**sample_outfit_data_with_metadata)
        assert outfit._metadata is not None
        assert outfit._metadata.tool == "outfit-analyzer"

    def test_outfit_spec_missing_required_fields(self):
        """Test that missing required fields raises ValidationError"""
        with pytest.raises(ValidationError):
            OutfitSpec(clothing_items=[])

    def test_clothing_item_validation(self):
        """Test ClothingItem model"""
        item = ClothingItem(
            item="jacket",
            fabric="wool",
            color="black",
            details="slim fit"
        )
        assert item.item == "jacket"
        assert item.fabric == "wool"

    def test_outfit_serialization(self, sample_outfit_data):
        """Test outfit can be serialized to dict"""
        outfit = OutfitSpec(**sample_outfit_data)
        outfit_dict = outfit.model_dump()
        assert outfit_dict["style_genre"] == "modern professional"
        assert len(outfit_dict["clothing_items"]) == 2


@pytest.mark.unit
class TestVisualStyleSpec:
    """Tests for VisualStyleSpec"""

    def test_create_visual_style(self, sample_visual_style_data):
        """Test creating a valid visual style spec"""
        style = VisualStyleSpec(**sample_visual_style_data)
        assert style.lighting_setup == "three-point lighting"
        assert style.mood == "professional and approachable"

    def test_visual_style_serialization(self, sample_visual_style_data):
        """Test visual style serialization"""
        style = VisualStyleSpec(**sample_visual_style_data)
        style_dict = style.model_dump()
        assert "lighting_setup" in style_dict
        assert "photography_style" in style_dict


@pytest.mark.unit
class TestArtStyleSpec:
    """Tests for ArtStyleSpec"""

    def test_create_art_style(self):
        """Test creating art style spec"""
        style = ArtStyleSpec(
            medium="oil painting",
            technique="impasto",
            color_palette=["blue", "gold", "white"],
            texture="thick, textured",
            composition_style="dynamic diagonal",
            artistic_movement="impressionism",
            mood="vibrant and energetic",
            level_of_detail="loose, expressive"
        )
        assert style.medium == "oil painting"
        assert len(style.color_palette) == 3


@pytest.mark.unit
class TestHairSpecs:
    """Tests for hair-related specs"""

    def test_hair_style_spec(self):
        """Test HairStyleSpec"""
        style = HairStyleSpec(
            cut="layered bob",
            length="shoulder length",
            layers="long layers throughout",
            texture="wavy",
            volume="medium volume",
            parting="side part",
            front_styling="swept to the side",
            overall_style="casual modern"
        )
        assert style.cut == "layered bob"
        assert style.length == "shoulder length"

    def test_hair_color_spec(self):
        """Test HairColorSpec"""
        color = HairColorSpec(
            base_color="dark brown",
            undertones="warm caramel",
            dimension="multi-dimensional",
            finish="natural glossy"
        )
        assert color.base_color == "dark brown"
        assert color.finish == "natural glossy"


@pytest.mark.unit
class TestMakeupSpec:
    """Tests for MakeupSpec"""

    def test_makeup_spec(self):
        """Test creating makeup spec"""
        makeup = MakeupSpec(
            complexion="natural foundation, soft blush",
            eyes="neutral eyeshadow, mascara",
            lips="nude lip color",
            overall_style="natural professional",
            intensity="moderate",
            color_palette=["beige", "brown", "rose"]
        )
        assert makeup.intensity == "moderate"
        assert len(makeup.color_palette) == 3


@pytest.mark.unit
class TestExpressionSpec:
    """Tests for ExpressionSpec"""

    def test_expression_spec(self):
        """Test creating expression spec"""
        expr = ExpressionSpec(
            primary_emotion="confidence",
            intensity="moderate",
            mouth="slight smile",
            eyes="direct gaze",
            eyebrows="relaxed",
            gaze_direction="camera",
            overall_mood="professional and approachable"
        )
        assert expr.primary_emotion == "confidence"
        assert expr.gaze_direction == "camera"


@pytest.mark.unit
class TestAccessoriesSpec:
    """Tests for AccessoriesSpec"""

    def test_accessories_spec(self):
        """Test creating accessories spec"""
        acc = AccessoriesSpec(
            jewelry=["stud earrings", "simple necklace"],
            watches="silver watch",
            overall_style="minimalist professional"
        )
        assert len(acc.jewelry) == 2
        assert acc.watches == "silver watch"

    def test_accessories_with_defaults(self):
        """Test accessories with default values"""
        acc = AccessoriesSpec(overall_style="minimal")
        assert acc.jewelry == []
        assert acc.other == []
        assert acc.bags is None


@pytest.mark.unit
class TestImageGenerationSpecs:
    """Tests for image generation request/result specs"""

    def test_image_generation_request(self, sample_outfit_data):
        """Test creating image generation request"""
        outfit = OutfitSpec(**sample_outfit_data)
        request = ImageGenerationRequest(
            subject_image="subject.jpg",
            outfit=outfit,
            variations=2
        )
        assert request.subject_image == "subject.jpg"
        assert request.outfit is not None
        assert request.variations == 2

    def test_image_generation_request_validation(self):
        """Test validation of variations field"""
        with pytest.raises(ValidationError):
            # variations must be 1-10
            ImageGenerationRequest(
                subject_image="test.jpg",
                variations=15
            )

    def test_image_generation_result(self, sample_outfit_data):
        """Test creating image generation result"""
        outfit = OutfitSpec(**sample_outfit_data)
        request = ImageGenerationRequest(
            subject_image="subject.jpg",
            outfit=outfit
        )
        result = ImageGenerationResult(
            file_path="output.png",
            request=request,
            model_used="gemini-2.0-flash",
            cost_estimate=0.05,
            generation_time=12.5
        )
        assert result.file_path == "output.png"
        assert result.cost_estimate == 0.05
        assert isinstance(result.timestamp, datetime)


@pytest.mark.unit
class TestVideoSpecs:
    """Tests for video generation specs"""

    def test_aspect_ratio_enum(self):
        """Test AspectRatio enum"""
        assert AspectRatio.PORTRAIT == "720x1280"
        assert AspectRatio.LANDSCAPE == "1792x1024"
        assert AspectRatio.TALL == "1024x1792"

    def test_video_model_enum(self):
        """Test VideoModel enum"""
        assert VideoModel.SORA_2 == "sora-2"
        assert VideoModel.SORA_2_PRO == "sora-2-pro"

    def test_video_prompt_spec(self):
        """Test VideoPromptSpec"""
        prompt = VideoPromptSpec(
            prompt="A cat playing piano",
            duration=8,
            aspect_ratio=AspectRatio.LANDSCAPE,
            model=VideoModel.SORA_2_PRO
        )
        assert prompt.prompt == "A cat playing piano"
        assert prompt.duration == 8

    def test_video_generation_request(self):
        """Test VideoGenerationRequest"""
        request = VideoGenerationRequest(
            prompt="A cat playing piano",
            enhanced_prompt="A fluffy orange cat...",
            model=VideoModel.SORA_2_PRO,
            size="1792x1024",
            seconds=8
        )
        assert request.prompt == "A cat playing piano"
        assert request.enhanced_prompt is not None

    def test_video_generation_result(self):
        """Test VideoGenerationResult"""
        request = VideoGenerationRequest(
            prompt="test",
            model=VideoModel.SORA_2,
            size="720x1280",
            seconds=4
        )
        result = VideoGenerationResult(
            file_path="video.mp4",
            video_id="vid_123",
            request=request,
            model_used="sora-2",
            file_size_mb=15.5,
            generation_time=180.0,
            cost_estimate=2.00
        )
        assert result.file_path == "video.mp4"
        assert result.video_id == "vid_123"
        assert result.file_size_mb == 15.5


@pytest.mark.unit
class TestSpecSerialization:
    """Tests for spec serialization/deserialization"""

    def test_outfit_round_trip(self, sample_outfit_data):
        """Test outfit can be serialized and deserialized"""
        outfit1 = OutfitSpec(**sample_outfit_data)
        outfit_dict = outfit1.model_dump()
        outfit2 = OutfitSpec(**outfit_dict)

        assert outfit1.style_genre == outfit2.style_genre
        assert len(outfit1.clothing_items) == len(outfit2.clothing_items)

    def test_spec_with_metadata_round_trip(self, sample_outfit_data_with_metadata):
        """Test spec with metadata round trip"""
        outfit1 = OutfitSpec(**sample_outfit_data_with_metadata)
        outfit_dict = outfit1.model_dump(mode='json')
        outfit2 = OutfitSpec(**outfit_dict)

        assert outfit1._metadata.tool == outfit2._metadata.tool
        assert outfit1.style_genre == outfit2.style_genre
