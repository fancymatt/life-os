"""API Request Models"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Union, List


class ImageInput(BaseModel):
    """Image input - either URL or base64 data"""
    image_url: Optional[HttpUrl] = None
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "http://example.com/image.jpg"
            }
        }


class AnalyzeRequest(BaseModel):
    """Request to analyze an image"""
    image: ImageInput
    save_as_preset: Optional[Union[str, bool]] = Field(None, description="Save result as preset (True for auto-name, or custom name)")
    skip_cache: bool = Field(False, description="Skip cache lookup")
    selected_analyses: Optional[dict] = Field(None, description="For comprehensive analyzer: dict of which analyses to run")

    class Config:
        json_schema_extra = {
            "example": {
                "image": {"image_url": "http://example.com/photo.jpg"},
                "save_as_preset": True,
                "skip_cache": False
            }
        }


class GenerateRequest(BaseModel):
    """Request to generate an image"""
    subject_image: ImageInput
    outfit: Optional[Union[str, dict]] = Field(None, description="Outfit preset name or spec dict")
    visual_style: Optional[Union[str, dict]] = Field(None, description="Visual style preset name or spec dict")
    art_style: Optional[Union[str, dict]] = Field(None, description="Art style preset name or spec dict")
    hair_style: Optional[Union[str, dict]] = Field(None, description="Hair style preset name or spec dict")
    hair_color: Optional[Union[str, dict]] = Field(None, description="Hair color preset name or spec dict")
    makeup: Optional[Union[str, dict]] = Field(None, description="Makeup preset name or spec dict")
    expression: Optional[Union[str, dict]] = Field(None, description="Expression preset name or spec dict")
    accessories: Optional[Union[str, dict]] = Field(None, description="Accessories preset name or spec dict")
    temperature: float = Field(0.8, ge=0.0, le=1.0, description="Generation temperature")

    class Config:
        json_schema_extra = {
            "example": {
                "subject_image": {"image_url": "http://example.com/subject.jpg"},
                "outfit": "casual-outfit",
                "visual_style": "film-noir",
                "temperature": 0.8
            }
        }


class BatchAnalyzeRequest(BaseModel):
    """Request to batch analyze images"""
    images: List[ImageInput] = Field(..., description="List of images to analyze")
    analyzer: str = Field(..., description="Analyzer to use (outfit, comprehensive, etc.)")
    save_as_prefix: Optional[str] = Field(None, description="Prefix for saved presets")
    skip_cache: bool = Field(False, description="Skip cache lookup")

    class Config:
        json_schema_extra = {
            "example": {
                "images": [
                    {"image_url": "http://example.com/photo1.jpg"},
                    {"image_url": "http://example.com/photo2.jpg"}
                ],
                "analyzer": "outfit",
                "save_as_prefix": "batch",
                "skip_cache": False
            }
        }


class BatchGenerateRequest(BaseModel):
    """Request to batch generate images"""
    subjects: List[str] = Field(..., description="Subject image URLs or preset names")
    outfits: List[str] = Field(..., description="Outfit preset names")
    styles: Optional[List[str]] = Field(None, description="Visual style preset names")
    temperature: float = Field(0.8, ge=0.0, le=1.0)

    class Config:
        json_schema_extra = {
            "example": {
                "subjects": ["subject1.jpg", "subject2.jpg"],
                "outfits": ["casual", "formal"],
                "styles": ["vintage", "modern"]
            }
        }


class PresetCreate(BaseModel):
    """Request to create a preset"""
    name: str = Field(..., description="Preset name")
    data: dict = Field(..., description="Preset data (spec dict)")
    notes: Optional[str] = Field(None, description="Optional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "my-outfit",
                "data": {
                    "style_genre": "casual",
                    "formality": "casual",
                    "clothing_items": []
                },
                "notes": "Custom preset"
            }
        }


class PresetUpdate(BaseModel):
    """Request to update a preset"""
    data: dict = Field(..., description="Updated preset data")
    display_name: Optional[str] = Field(None, description="Optional display name")
    notes: Optional[str] = Field(None, description="Optional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "style_genre": "smart casual",
                    "formality": "semi-formal"
                },
                "display_name": "Updated outfit name"
            }
        }


class ModularGenerateRequest(BaseModel):
    """Request for modular generation with preset IDs"""
    subject_image: str = Field(..., description="Path to subject image (e.g., jenny.png)")
    variations: int = Field(1, ge=1, le=10, description="Number of variations to generate")
    outfit: Optional[Union[str, List[str]]] = Field(None, description="Outfit preset ID or list of IDs for amalgamation")
    visual_style: Optional[str] = Field(None, description="Visual style preset ID")
    art_style: Optional[str] = Field(None, description="Art style preset ID")
    hair_style: Optional[str] = Field(None, description="Hair style preset ID")
    hair_color: Optional[str] = Field(None, description="Hair color preset ID")
    makeup: Optional[str] = Field(None, description="Makeup preset ID")
    expression: Optional[str] = Field(None, description="Expression preset ID")
    accessories: Optional[str] = Field(None, description="Accessories preset ID")

    class Config:
        json_schema_extra = {
            "example": {
                "subject_image": "jenny.png",
                "variations": 2,
                "outfit": ["casual-preset-id", "jacket-preset-id"],
                "visual_style": "film-noir-id"
            }
        }


class CharacterCreate(BaseModel):
    """Request to create a character"""
    name: str = Field(..., description="Character name")
    visual_description: Optional[str] = Field(None, description="Visual appearance description")
    personality: Optional[str] = Field(None, description="Personality traits and characteristics")
    reference_image: Optional[ImageInput] = Field(None, description="Reference image for the character")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")

    # Detailed appearance fields (from character_appearance_analyzer)
    age: Optional[str] = Field(None, description="Apparent age or age group")
    skin_tone: Optional[str] = Field(None, description="Skin tone description")
    face_description: Optional[str] = Field(None, description="Facial description")
    hair_description: Optional[str] = Field(None, description="Hair description")
    body_description: Optional[str] = Field(None, description="Body/physique description")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Luna",
                "visual_description": "young girl with curly brown hair and green eyes, wearing a red dress",
                "personality": "curious and brave, loves to explore",
                "tags": ["protagonist", "adventure"]
            }
        }


class CharacterUpdate(BaseModel):
    """Request to update a character"""
    name: Optional[str] = Field(None, description="Character name")
    visual_description: Optional[str] = Field(None, description="Visual appearance description")
    personality: Optional[str] = Field(None, description="Personality traits")
    reference_image: Optional[ImageInput] = Field(None, description="Reference image")
    tags: Optional[List[str]] = Field(None, description="Tags")

    # Detailed appearance fields (from character_appearance_analyzer)
    age: Optional[str] = Field(None, description="Apparent age or age group")
    skin_tone: Optional[str] = Field(None, description="Skin tone description")
    face_description: Optional[str] = Field(None, description="Facial description")
    hair_description: Optional[str] = Field(None, description="Hair description")
    body_description: Optional[str] = Field(None, description="Body/physique description")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Luna the Explorer",
                "personality": "curious, brave, and kind-hearted"
            }
        }


class CharacterFromSubject(BaseModel):
    """Request to create character from a subject image"""
    subject_path: str = Field(..., description="Path to subject image (e.g., jenny.png) or full URL")
    name: str = Field(..., description="Character name")
    analyze_first: bool = Field(True, description="Run comprehensive analysis first")
    create_presets: bool = Field(False, description="Create presets from analysis")
    personality: Optional[str] = Field(None, description="Personality traits")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")

    class Config:
        json_schema_extra = {
            "example": {
                "subject_path": "jenny.png",
                "name": "Jenny",
                "analyze_first": True,
                "create_presets": False,
                "personality": "cheerful and energetic",
                "tags": ["main", "protagonist"]
            }
        }
