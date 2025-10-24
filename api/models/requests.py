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
    """Request for modular generation with preset IDs and clothing items"""
    subject_image: str = Field(..., description="Path to subject image (e.g., jenny.png)")
    variations: int = Field(1, ge=1, le=10, description="Number of variations to generate")

    # Clothing item categories (individual items, can be layered)
    headwear: Optional[Union[str, List[str]]] = Field(None, description="Headwear item ID(s)")
    eyewear: Optional[Union[str, List[str]]] = Field(None, description="Eyewear item ID(s)")
    earrings: Optional[Union[str, List[str]]] = Field(None, description="Earrings item ID(s)")
    neckwear: Optional[Union[str, List[str]]] = Field(None, description="Neckwear item ID(s)")
    tops: Optional[Union[str, List[str]]] = Field(None, description="Tops item ID(s)")
    overtops: Optional[Union[str, List[str]]] = Field(None, description="Overtops item ID(s)")
    outerwear: Optional[Union[str, List[str]]] = Field(None, description="Outerwear item ID(s)")
    one_piece: Optional[Union[str, List[str]]] = Field(None, description="One-piece item ID(s)")
    bottoms: Optional[Union[str, List[str]]] = Field(None, description="Bottoms item ID(s)")
    belts: Optional[Union[str, List[str]]] = Field(None, description="Belts item ID(s)")
    hosiery: Optional[Union[str, List[str]]] = Field(None, description="Hosiery item ID(s)")
    footwear: Optional[Union[str, List[str]]] = Field(None, description="Footwear item ID(s)")
    bags: Optional[Union[str, List[str]]] = Field(None, description="Bags item ID(s)")
    wristwear: Optional[Union[str, List[str]]] = Field(None, description="Wristwear item ID(s)")
    handwear: Optional[Union[str, List[str]]] = Field(None, description="Handwear item ID(s)")

    # Style presets
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
                "tops": "blue-shirt-id",
                "bottoms": "black-pants-id",
                "footwear": "sneakers-id",
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


# ============================================================================
# Board Game Models
# ============================================================================

class BoardGameCreate(BaseModel):
    """Request to create a board game"""
    name: str = Field(..., description="Board game name")
    bgg_id: Optional[int] = Field(None, description="BoardGameGeek ID")
    designer: Optional[str] = Field(None, description="Game designer(s)")
    publisher: Optional[str] = Field(None, description="Publisher")
    year: Optional[int] = Field(None, description="Publication year")
    description: Optional[str] = Field(None, description="Game description")
    player_count_min: Optional[int] = Field(None, description="Minimum players")
    player_count_max: Optional[int] = Field(None, description="Maximum players")
    playtime_min: Optional[int] = Field(None, description="Minimum playtime (minutes)")
    playtime_max: Optional[int] = Field(None, description="Maximum playtime (minutes)")
    complexity: Optional[float] = Field(None, description="Complexity rating (1-5)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wingspan",
                "bgg_id": 266192,
                "designer": "Elizabeth Hargrave",
                "publisher": "Stonemaier Games",
                "year": 2019,
                "player_count_min": 1,
                "player_count_max": 5,
                "playtime_min": 40,
                "playtime_max": 70,
                "complexity": 2.4
            }
        }


class BoardGameUpdate(BaseModel):
    """Request to update a board game"""
    name: Optional[str] = Field(None, description="Board game name")
    designer: Optional[str] = Field(None, description="Game designer(s)")
    publisher: Optional[str] = Field(None, description="Publisher")
    year: Optional[int] = Field(None, description="Publication year")
    description: Optional[str] = Field(None, description="Game description")
    player_count_min: Optional[int] = Field(None, description="Minimum players")
    player_count_max: Optional[int] = Field(None, description="Maximum players")
    playtime_min: Optional[int] = Field(None, description="Minimum playtime (minutes)")
    playtime_max: Optional[int] = Field(None, description="Maximum playtime (minutes)")
    complexity: Optional[float] = Field(None, description="Complexity rating (1-5)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wingspan (2nd Edition)",
                "year": 2020
            }
        }


class QAAskRequest(BaseModel):
    """Request to ask a question"""
    question: str = Field(..., description="The question to ask")
    game_id: Optional[str] = Field(None, description="Board game ID (for document-grounded Q&A)")
    document_ids: Optional[List[str]] = Field(None, description="Specific document IDs to search")
    context_type: str = Field("general", description="Type of Q&A: document, general, image, comparison")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "How many bird cards do you draw during setup?",
                "game_id": "wingspan-266192",
                "context_type": "document"
            }
        }


class QAUpdate(BaseModel):
    """Request to update a Q&A"""
    is_favorite: Optional[bool] = Field(None, description="Mark as favorite")
    was_helpful: Optional[bool] = Field(None, description="Mark as helpful or not")
    user_notes: Optional[str] = Field(None, description="Personal notes")
    custom_tags: Optional[List[str]] = Field(None, description="Custom tags")

    class Config:
        json_schema_extra = {
            "example": {
                "is_favorite": True,
                "was_helpful": True,
                "user_notes": "This rule is important for setup",
                "custom_tags": ["setup", "cards"]
            }
        }


# ============================================================================
# Tag Models
# ============================================================================

class TagCreate(BaseModel):
    """Request to create a tag"""
    name: str = Field(..., min_length=1, max_length=100, description="Tag name")
    category: Optional[str] = Field(None, description="Tag category (material, style, season, genre, etc.)")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code (#RRGGBB)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "casual",
                "category": "style",
                "color": "#4A90E2"
            }
        }


class TagUpdate(BaseModel):
    """Request to update a tag"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Tag name")
    category: Optional[str] = Field(None, description="Tag category")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "smart casual",
                "color": "#5A9FD4"
            }
        }


class EntityTagRequest(BaseModel):
    """Request to tag an entity"""
    tag_names: List[str] = Field(..., min_length=1, description="List of tag names to apply")
    auto_create: bool = Field(True, description="Auto-create tags that don't exist")

    class Config:
        json_schema_extra = {
            "example": {
                "tag_names": ["casual", "summer", "favorite"],
                "auto_create": True
            }
        }


class SetEntityTagsRequest(BaseModel):
    """Request to set all tags on an entity (replaces existing)"""
    tag_names: List[str] = Field(..., description="Complete list of tag names (replaces all existing tags)")

    class Config:
        json_schema_extra = {
            "example": {
                "tag_names": ["casual", "summer", "approved"]
            }
        }
