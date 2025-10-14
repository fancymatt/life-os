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
    clothing_items: List[ClothingItem] = Field(..., description="All clothing items")
    style_genre: str = Field(..., description="Overall style category")
    formality: str = Field(..., description="Formality level")
    aesthetic: str = Field(..., description="Aesthetic influences")
    season: Optional[str] = Field(None, description="Seasonal appropriateness")
    occasion: Optional[str] = Field(None, description="Suitable occasions")


class VisualStyleSpec(BaseModel):
    """Photographic/visual style analysis"""
    _metadata: Optional[SpecMetadata] = None
    composition: str = Field(..., description="Composition, rule of thirds, visual balance, leading lines")
    framing: str = Field(..., description="Framing details (close-up, medium shot, full body, etc.)")
    pose: str = Field(..., description="Body pose - hands, arms, head tilt, stance (no clothing/accessories)")
    body_position: str = Field(..., description="Body position and orientation (standing, sitting, profile, etc.)")
    lighting: str = Field(..., description="Lighting analysis including type, direction, quality, shadows, highlights")
    color_palette: List[str] = Field(..., description="All dominant and accent colors")
    color_grading: str = Field(..., description="Color grading and toning (warm/cool/desaturated/etc.)")
    mood: str = Field(..., description="Overall mood, atmosphere, and emotional tone")
    background: str = Field(..., description="Detailed background including depth, bokeh, environmental elements")
    photographic_style: str = Field(..., description="Specific photo style (fashion editorial, candid, portrait, etc.)")
    artistic_style: str = Field(..., description="Artistic aesthetic style (retro 80s, film noir, minimalist, etc.)")
    film_grain: str = Field(..., description="Presence and intensity of film grain or noise")
    image_quality: str = Field(..., description="Quality characteristics (sharp, soft focus, motion blur, etc.)")
    era_aesthetic: str = Field(..., description="Time period aesthetic (1980s, modern, vintage, etc.)")
    camera_angle: str = Field(..., description="Camera angle and perspective (eye level, low angle, etc.)")
    depth_of_field: str = Field(..., description="DOF characteristics (shallow with bokeh, deep, selective focus)")
    post_processing: str = Field(..., description="Post-processing effects (HDR, cross-processing, filters, etc.)")


class ArtStyleSpec(BaseModel):
    """Artistic style analysis"""
    _metadata: Optional[SpecMetadata] = None
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
    cut: str = Field(..., description="Haircut type and shape")
    length: str = Field(..., description="Overall length")
    layers: str = Field(..., description="Layering structure")
    texture: str = Field(..., description="Natural texture and styling")
    volume: str = Field(..., description="Volume and body")
    parting: str = Field(..., description="Part placement and style")
    front_styling: str = Field(..., description="Bangs, framing, front details")
    overall_style: str = Field(..., description="Style category")


class HairColorSpec(BaseModel):
    """Hair color analysis (not style)"""
    _metadata: Optional[SpecMetadata] = None
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
    complexion: str = Field(..., description="Foundation, blush, highlighter, contour")
    eyes: str = Field(..., description="Shadow, liner, mascara, brows")
    lips: str = Field(..., description="Lip color and finish")
    overall_style: str = Field(..., description="Makeup style category")
    intensity: str = Field(..., description="Natural/moderate/dramatic")
    color_palette: List[str] = Field(..., description="Dominant makeup colors")


class ExpressionSpec(BaseModel):
    """Facial expression analysis"""
    _metadata: Optional[SpecMetadata] = None
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
    jewelry: List[str] = Field(default_factory=list, description="Earrings, necklaces, bracelets, rings")
    bags: Optional[str] = Field(None, description="Bags or purses")
    belts: Optional[str] = Field(None, description="Belt description")
    scarves: Optional[str] = Field(None, description="Scarves or wraps")
    hats: Optional[str] = Field(None, description="Headwear")
    watches: Optional[str] = Field(None, description="Watch description")
    other: List[str] = Field(default_factory=list, description="Other accessories")
    overall_style: str = Field(..., description="Accessory styling approach")


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
