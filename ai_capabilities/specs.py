"""
AI-Studio Capability Specifications

All Pydantic models defining inputs/outputs for tools and workflows.
Each spec includes metadata support for provenance and versioning.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==============================================================================
# METADATA
# ==============================================================================

class SpecMetadata(BaseModel):
    """Metadata attached to all analyzed/generated specs"""
    preset_id: Optional[str] = Field(None, description="Unique preset ID (UUID)")
    display_name: Optional[str] = Field(None, description="User-editable display name")
    created_at: datetime = Field(default_factory=datetime.now)
    tool: str = Field(..., description="Tool that generated this spec")
    tool_version: str = Field(default="1.0.0")
    source_image: Optional[str] = Field(None, description="Source image path if applicable")
    source_hash: Optional[str] = Field(None, description="SHA256 hash of source image")
    model_used: str = Field(..., description="LLM model used for generation")
    notes: Optional[str] = Field(None, description="User-editable notes")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ==============================================================================
# IMAGE ANALYSIS SPECS
# ==============================================================================

class ClothingItem(BaseModel):
    """Individual clothing item description"""
    item: str = Field(..., description="Type of clothing item")
    fabric: str = Field(..., description="Fabric material")
    color: str = Field(..., description="Color description")
    details: str = Field(..., description="Construction, fit, and design details")


class OutfitSpec(BaseModel):
    """Complete outfit analysis"""
    _metadata: Optional[SpecMetadata] = None
    suggested_name: str = Field(..., description="Short descriptive name for this outfit (2-4 words, e.g., 'Black Leather Jacket Look', 'Summer Floral Dress')")
    clothing_items: List[ClothingItem] = Field(..., description="All clothing items")
    style_genre: str = Field(..., description="Overall style category")
    formality: str = Field(..., description="Formality level")
    aesthetic: str = Field(..., description="Aesthetic influences")
    season: Optional[str] = Field(None, description="Seasonal appropriateness")
    occasion: Optional[str] = Field(None, description="Suitable occasions")


class PhotoCompositionSpec(BaseModel):
    """Photograph composition analysis - what's happening in the frame"""
    _metadata: Optional[SpecMetadata] = None
    suggested_name: str = Field(..., description="Short descriptive name for this photo composition (2-4 words, e.g., 'Mirror Selfie Portrait', 'Outdoor Golden Hour Shot')")
    subject_action: str = Field(
        ...,
        description="DETAILED 4-8 sentence paragraph describing body position, head angle, gaze, facial expression, arms/hands, and body language. MINIMUM 200 characters required."
    )
    setting: str = Field(
        ...,
        description="DETAILED 4-8 sentence paragraph describing background with exact colors, textures, objects, and atmosphere. MINIMUM 200 characters required."
    )
    framing: str = Field(..., description="Camera framing: 'extreme close-up', 'close-up portrait', 'medium shot', 'full body', or 'wide shot'")
    camera_angle: str = Field(..., description="Camera angle: 'eye level', 'low angle', 'high angle', 'slightly from below', or 'slightly from above'")
    lighting: str = Field(
        ...,
        description="DETAILED 4-6 sentence paragraph about light direction, quality, intensity, color temperature, shadows, and highlights. MINIMUM 200 characters required."
    )
    mood: str = Field(
        ...,
        description="DETAILED 4-6 sentence paragraph about emotional tone, energy, atmosphere, and impact. MINIMUM 200 characters required."
    )

    @field_validator('subject_action', 'setting', 'lighting', 'mood')
    @classmethod
    def validate_min_length(cls, v: str, info) -> str:
        """Ensure detailed fields have minimum length"""
        if len(v) < 200:
            raise ValueError(f'{info.field_name} must be at least 200 characters (got {len(v)}). Provide a detailed, multi-sentence paragraph.')
        word_count = len(v.split())
        if word_count < 40:
            raise ValueError(f'{info.field_name} must be at least 40 words (got {word_count}). Provide detailed descriptions, not brief summaries.')
        return v

# Keep VisualStyleSpec as an alias for backward compatibility
VisualStyleSpec = PhotoCompositionSpec


class ArtStyleSpec(BaseModel):
    """Artistic style analysis"""
    _metadata: Optional[SpecMetadata] = None
    suggested_name: str = Field(..., description="Short descriptive name for this art style (2-4 words, e.g., 'Impressionist Oil Painting', 'Digital Pop Art')")
    medium: str = Field(..., description="Artistic medium")
    technique: str = Field(..., description="Application technique")
    color_palette: List[str] = Field(..., description="Dominant colors")
    brush_style: Optional[str] = Field(None, description="Brush work characteristics")
    texture: str = Field(..., description="Surface texture quality")
    composition_style: str = Field(..., description="Compositional approach")
    artistic_movement: str = Field(..., description="Art historical context")
    mood: str = Field(..., description="Emotional quality")
    level_of_detail: str = Field(..., description="Detailed/loose/abstract")


class HairStyleSpec(BaseModel):
    """Hair style structure analysis (not color)"""
    _metadata: Optional[SpecMetadata] = None
    suggested_name: str = Field(..., description="Short descriptive name for this hair style (2-4 words, e.g., 'Long Layered Waves', 'Blunt Bob Cut')")
    cut: str = Field(
        ...,
        description="DETAILED 3-5 sentence description of the haircut including cut type, shape, perimeter, interior technique, and overall silhouette. MINIMUM 150 characters required."
    )
    length: str = Field(..., description="Overall length (e.g., 'chin-length', 'shoulder-length', 'mid-back', 'waist-length')")
    layers: str = Field(
        ...,
        description="DETAILED 3-5 sentence description of the layering structure including layer placement, graduation, weight distribution, and how layers create movement and shape. MINIMUM 150 characters required."
    )
    texture: str = Field(
        ...,
        description="DETAILED 3-5 sentence description of both the natural texture and how it's styled, including curl pattern, smoothness, finish, and styling techniques used. MINIMUM 150 characters required."
    )
    volume: str = Field(..., description="Volume and body (e.g., 'flat at roots', 'lifted crown', 'full throughout', 'voluminous with body')")
    parting: str = Field(..., description="Part placement and style (e.g., 'deep side part', 'center part', 'no visible part', 'zigzag part')")
    front_styling: str = Field(
        ...,
        description="DETAILED 2-4 sentence description of front styling including bang type, framing pieces, face-framing layers, and how the front is shaped and styled. MINIMUM 100 characters required."
    )
    overall_style: str = Field(
        ...,
        description="DETAILED 2-4 sentence professional description of the overall hairstyle including its category, distinctive features, and styling approach. MINIMUM 100 characters required."
    )

    @field_validator('cut', 'layers', 'texture')
    @classmethod
    def validate_detailed_fields(cls, v: str, info) -> str:
        """Ensure detailed fields have minimum length"""
        if len(v) < 150:
            raise ValueError(f'{info.field_name} must be at least 150 characters (got {len(v)}). Provide a detailed, professional multi-sentence description.')
        word_count = len(v.split())
        if word_count < 25:
            raise ValueError(f'{info.field_name} must be at least 25 words (got {word_count}). Provide detailed professional descriptions.')
        return v

    @field_validator('front_styling', 'overall_style')
    @classmethod
    def validate_moderate_fields(cls, v: str, info) -> str:
        """Ensure moderate detail fields have minimum length"""
        if len(v) < 100:
            raise ValueError(f'{info.field_name} must be at least 100 characters (got {len(v)}). Provide a detailed, professional description.')
        word_count = len(v.split())
        if word_count < 15:
            raise ValueError(f'{info.field_name} must be at least 15 words (got {word_count}). Provide detailed professional descriptions.')
        return v


class HairColorSpec(BaseModel):
    """Hair color analysis (not style)"""
    _metadata: Optional[SpecMetadata] = None
    suggested_name: str = Field(..., description="Short descriptive name for this hair color (2-4 words, e.g., 'Platinum Blonde Highlights', 'Rich Chocolate Brown')")
    base_color: str = Field(..., description="Primary hair color")
    undertones: str = Field(..., description="Color undertones")
    highlights: Optional[str] = Field(None, description="Highlight colors and placement")
    lowlights: Optional[str] = Field(None, description="Lowlight colors and placement")
    technique: Optional[str] = Field(None, description="Coloring technique used")
    dimension: str = Field(..., description="Color depth and variation")
    finish: str = Field(..., description="Matte/glossy/natural finish")


class MakeupSpec(BaseModel):
    """Makeup analysis"""
    _metadata: Optional[SpecMetadata] = None
    suggested_name: str = Field(..., description="Short descriptive name for this makeup look (2-4 words, e.g., 'Smokey Eye Glam', 'Natural Fresh Face')")
    complexion: str = Field(..., description="Foundation, blush, highlighter, contour")
    eyes: str = Field(..., description="Shadow, liner, mascara, brows")
    lips: str = Field(..., description="Lip color and finish")
    overall_style: str = Field(..., description="Makeup style category")
    intensity: str = Field(..., description="Natural/moderate/dramatic")
    color_palette: List[str] = Field(..., description="Dominant makeup colors")


class ExpressionSpec(BaseModel):
    """Facial expression analysis"""
    _metadata: Optional[SpecMetadata] = None
    suggested_name: str = Field(..., description="Short descriptive name for this expression (2-4 words, e.g., 'Soft Gentle Smile', 'Confident Direct Gaze')")
    primary_emotion: str = Field(..., description="Main emotional expression")
    intensity: str = Field(..., description="Subtle/moderate/strong")
    mouth: str = Field(..., description="Mouth position and shape")
    eyes: str = Field(..., description="Eye expression")
    eyebrows: str = Field(..., description="Eyebrow position")
    gaze_direction: str = Field(..., description="Where subject is looking")
    overall_mood: str = Field(..., description="Overall emotional impression")


class AccessoriesSpec(BaseModel):
    """Accessories analysis"""
    _metadata: Optional[SpecMetadata] = None
    suggested_name: str = Field(..., description="Short descriptive name for these accessories (2-4 words, e.g., 'Gold Layered Jewelry', 'Minimalist Silver Pieces')")
    jewelry: List[str] = Field(default_factory=list, description="Earrings, necklaces, bracelets, rings")
    bags: Optional[str] = Field(None, description="Bags or purses")
    belts: Optional[str] = Field(None, description="Belt description")
    scarves: Optional[str] = Field(None, description="Scarves or wraps")
    hats: Optional[str] = Field(None, description="Headwear")
    watches: Optional[str] = Field(None, description="Watch description")
    other: List[str] = Field(default_factory=list, description="Other accessories")
    overall_style: str = Field(..., description="Accessory styling approach")


class CharacterAppearanceSpec(BaseModel):
    """Character physical appearance analysis"""
    _metadata: Optional[SpecMetadata] = None
    suggested_name: str = Field(..., description="Short descriptive name (2-4 words, e.g., 'Young Adult Woman', 'Middle-Aged Man')")
    age_appearance: str = Field(..., description="Apparent age or age group (e.g., 'young child', 'teenager', 'young adult', 'middle-aged', 'elderly')")
    gender_presentation: str = Field(..., description="Gender presentation (e.g., 'masculine', 'feminine', 'androgynous')")
    ethnicity: Optional[str] = Field(None, description="Apparent ethnicity or ethnic features if discernible")
    skin_tone: str = Field(..., description="Skin tone description (e.g., 'fair', 'light', 'medium', 'olive', 'tan', 'brown', 'dark')")
    face_shape: str = Field(..., description="Face shape (e.g., 'round', 'oval', 'heart-shaped', 'square', 'long')")
    hair_description: str = Field(..., description="Complete hair description including color, style, length, and texture")
    eye_description: str = Field(..., description="Eye description including color and notable features")
    build: str = Field(..., description="Body build or physique (e.g., 'slender', 'athletic', 'average', 'stocky', 'petite', 'tall')")
    height_appearance: str = Field(..., description="Apparent height (e.g., 'short', 'average height', 'tall')")
    distinctive_features: Optional[str] = Field(None, description="Any distinctive features like freckles, dimples, scars, tattoos, etc.")
    overall_description: str = Field(..., description="A complete, natural-language description combining all features")


class ComprehensiveSpec(BaseModel):
    """Comprehensive analysis combining all aspects"""
    _metadata: Optional[SpecMetadata] = None
    outfit: OutfitSpec = Field(..., description="Outfit analysis")
    visual_style: VisualStyleSpec = Field(..., description="Visual style analysis")
    art_style: ArtStyleSpec = Field(..., description="Artistic style analysis")
    hair_style: HairStyleSpec = Field(..., description="Hair style analysis")
    hair_color: HairColorSpec = Field(..., description="Hair color analysis")
    makeup: MakeupSpec = Field(..., description="Makeup analysis")
    expression: ExpressionSpec = Field(..., description="Expression analysis")
    accessories: AccessoriesSpec = Field(..., description="Accessories analysis")


# ==============================================================================
# IMAGE GENERATION SPECS
# ==============================================================================

class ImageGenerationRequest(BaseModel):
    """Request for image generation with modular components"""
    subject_image: str = Field(..., description="Path to subject image")
    outfit: Optional[OutfitSpec] = Field(None, description="Outfit to apply")
    visual_style: Optional[VisualStyleSpec] = Field(None, description="Visual style to apply")
    hair_style: Optional[HairStyleSpec] = Field(None, description="Hair style to apply")
    hair_color: Optional[HairColorSpec] = Field(None, description="Hair color to apply")
    makeup: Optional[MakeupSpec] = Field(None, description="Makeup to apply")
    expression: Optional[ExpressionSpec] = Field(None, description="Expression to apply")
    accessories: Optional[AccessoriesSpec] = Field(None, description="Accessories to add")
    variations: int = Field(1, ge=1, le=10, description="Number of variations to generate")
    send_original_refs: bool = Field(False, description="Include reference images in API call")


class ImageGenerationResult(BaseModel):
    """Result from image generation"""
    file_path: str = Field(..., description="Path to generated image")
    request: ImageGenerationRequest = Field(..., description="Original request")
    model_used: str = Field(..., description="Model used for generation")
    timestamp: datetime = Field(default_factory=datetime.now)
    cost_estimate: Optional[float] = Field(None, description="Estimated cost in USD")
    generation_time: Optional[float] = Field(None, description="Time in seconds")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StyleTransferRequest(BaseModel):
    """Request for style transfer"""
    source_image: str = Field(..., description="Image to transform")
    style: VisualStyleSpec = Field(..., description="Style to apply")
    strength: float = Field(0.8, ge=0.0, le=1.0, description="Style transfer strength")
    preserve_identity: bool = Field(True, description="Preserve subject identity")


# ==============================================================================
# VIDEO SPECS
# ==============================================================================

class AspectRatio(str, Enum):
    """Video aspect ratios"""
    PORTRAIT = "720x1280"      # 9:16
    LANDSCAPE = "1792x1024"    # 16:9
    TALL = "1024x1792"         # 9:16 tall


class VideoModel(str, Enum):
    """Available video generation models"""
    SORA_2 = "sora-2"
    SORA_2_PRO = "sora-2-pro"


class VideoPromptSpec(BaseModel):
    """Video prompt specification"""
    _metadata: Optional[SpecMetadata] = None
    prompt: str = Field(..., description="Video description")
    duration: int = Field(4, ge=4, le=12, description="Duration in seconds")
    aspect_ratio: AspectRatio = Field(AspectRatio.PORTRAIT, description="Aspect ratio")
    model: VideoModel = Field(VideoModel.SORA_2_PRO, description="Model to use")


class VideoGenerationRequest(BaseModel):
    """Request for video generation"""
    prompt: str = Field(..., description="Video description")
    enhanced_prompt: Optional[str] = Field(None, description="GPT-5 enhanced prompt")
    model: VideoModel = Field(VideoModel.SORA_2_PRO)
    size: str = Field(..., description="Resolution string")
    seconds: int = Field(4, ge=4, le=12)
    skip_enhancement: bool = Field(False, description="Skip prompt enhancement")


class VideoGenerationResult(BaseModel):
    """Result from video generation"""
    file_path: str = Field(..., description="Path to generated video")
    video_id: str = Field(..., description="API video ID")
    request: VideoGenerationRequest = Field(..., description="Original request")
    model_used: str = Field(..., description="Model used")
    timestamp: datetime = Field(default_factory=datetime.now)
    file_size_mb: float = Field(..., description="File size in MB")
    generation_time: float = Field(..., description="Time in seconds")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost in USD")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ==============================================================================
# WORKFLOW SPECS
# ==============================================================================

class OutfitSwapWorkflowInput(BaseModel):
    """Input for outfit-swap batch workflow"""
    subjects: List[str] = Field(..., description="Subject image paths or preset names")
    outfits: List[str] = Field(..., description="Outfit image paths or preset names")
    styles: Optional[List[str]] = Field(None, description="Style image paths or preset names")
    hair_styles: Optional[List[str]] = Field(None)
    hair_colors: Optional[List[str]] = Field(None)
    makeup: Optional[List[str]] = Field(None)
    expressions: Optional[List[str]] = Field(None)
    accessories: Optional[List[str]] = Field(None)
    variations_per_combo: int = Field(1, ge=1, le=10)
    send_original_refs: bool = Field(False)
    save_presets: bool = Field(False, description="Auto-save analyses as presets")


class StyleTransferWorkflowInput(BaseModel):
    """Input for style transfer workflow"""
    source_images: List[str] = Field(..., description="Images to transform")
    styles: List[str] = Field(..., description="Styles to apply")
    strength: float = Field(0.8, ge=0.0, le=1.0)


class VideoCreationWorkflowInput(BaseModel):
    """Input for video creation workflow"""
    prompt: str = Field(..., description="Video description")
    model: VideoModel = Field(VideoModel.SORA_2_PRO)
    duration: int = Field(4, ge=4, le=12)
    aspect_ratio: AspectRatio = Field(AspectRatio.PORTRAIT)
    skip_enhancement: bool = Field(False)
    enhancement_model: str = Field("gpt-4o", description="Model for prompt enhancement")


# ==============================================================================
# LEGACY COMPATIBILITY (keeping original specs)
# ==============================================================================

class ImagePromptSpec(BaseModel):
    """Simple image prompt (legacy)"""
    prompt: str


class ArtDirectionSpec(BaseModel):
    """Art direction spec (legacy)"""
    mood: str
    palette: List[str]
    style_refs: List[str]
