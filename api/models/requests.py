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
    save_as_preset: Optional[str] = Field(None, description="Save result as preset with this name")
    skip_cache: bool = Field(False, description="Skip cache lookup")

    class Config:
        json_schema_extra = {
            "example": {
                "image": {"image_url": "http://example.com/photo.jpg"},
                "save_as_preset": "my-outfit",
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
