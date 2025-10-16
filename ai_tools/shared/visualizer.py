"""
Generic Preset Visualizer

Generates preview images for any preset type using DALL-E 3.
Automatically creates appropriate prompts based on the spec type.

Note: For full subject-based generation (like modular_image_generator),
Gemini 2.5 Flash is used as it has a subject image to work with.
"""

from pathlib import Path
from typing import Union, Optional
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import (
    VisualStyleSpec,
    ArtStyleSpec,
    HairStyleSpec,
    HairColorSpec,
    MakeupSpec,
    ExpressionSpec,
    AccessoriesSpec
)
from ai_tools.shared.router import LLMRouter
from ai_tools.shared.preset import PresetManager


class PresetVisualizer:
    """
    Generic visualizer for all preset types

    Generates square preview images (1024x1024) on white background
    using DALL-E 3 based on preset specifications.
    """

    def __init__(self, model: Optional[str] = None):
        """
        Initialize the visualizer

        Args:
            model: Model to use (default: dall-e-3)
        """
        self.model = model or "dall-e-3"
        self.router = LLMRouter(model=self.model)
        self.preset_manager = PresetManager()

    def _build_prompt(self, spec_type: str, spec: Union[
        VisualStyleSpec,
        ArtStyleSpec,
        HairStyleSpec,
        HairColorSpec,
        MakeupSpec,
        ExpressionSpec,
        AccessoriesSpec
    ]) -> str:
        """
        Build image generation prompt based on spec type

        Args:
            spec_type: Type of spec (visual-styles, art-styles, etc.)
            spec: The spec object

        Returns:
            Generated prompt string
        """
        if spec_type == "visual_styles":
            return self._build_visual_style_prompt(spec)
        elif spec_type == "art_styles":
            return self._build_art_style_prompt(spec)
        elif spec_type == "hair_styles":
            return self._build_hair_style_prompt(spec)
        elif spec_type == "hair_colors":
            return self._build_hair_color_prompt(spec)
        elif spec_type == "makeup":
            return self._build_makeup_prompt(spec)
        elif spec_type == "expressions":
            return self._build_expression_prompt(spec)
        elif spec_type == "accessories":
            return self._build_accessories_prompt(spec)
        else:
            raise ValueError(f"Unknown spec type: {spec_type}")

    def _build_visual_style_prompt(self, spec: VisualStyleSpec) -> str:
        """Build prompt for photograph composition preview as artistic storyboard illustration"""
        return f"""Create a soft, artistic storyboard illustration showing this composition:

SUBJECT & POSE:
{spec.subject_action}

BACKGROUND/SETTING:
{spec.setting}

FRAMING: {spec.framing}
CAMERA ANGLE: {spec.camera_angle}

LIGHTING: {spec.lighting}

MOOD: {spec.mood}

Style: Soft, painterly storyboard illustration with gentle linework and subtle watercolor-like shading. Show the exact pose, framing, and composition described above. The illustration should have a clean, artistic quality with soft edges and delicate color washes that suggest the lighting and mood. Use the background/setting exactly as described - whether it's a solid color, outdoor environment, interior space, or any other setting. Use natural skin tones and render the environment with appropriate colors and details matching the setting description. Focus on capturing the pose, expression, and overall composition in an elegant, illustrative style. No film equipment, clapboards, or production elements - just a beautiful composition sketch showing the subject in their described environment."""

    def _build_art_style_prompt(self, spec: ArtStyleSpec) -> str:
        """Build prompt for art style preview"""
        colors = ", ".join(spec.color_palette[:5]) if spec.color_palette else "varied colors"

        return f"""Create a STANDARDIZED art style reference following EXACT specifications to ensure consistency across ALL art style previews.

**CRITICAL: LOCKED-DOWN VISUALIZATION STYLE - SAME SUBJECT, DIFFERENT ARTISTIC TREATMENT**

Art Style to Apply:
- Medium: {spec.medium}
- Technique: {spec.technique}
- Movement: {spec.artistic_movement}
- Colors: {colors}
- Texture: {spec.texture}
- Composition: {spec.composition_style}
- Detail Level: {spec.level_of_detail}
- Mood: {spec.mood}
{f"- Brush Style: {spec.brush_style}" if spec.brush_style else ""}

**SUBJECT SPECIFICATIONS (MUST BE IDENTICAL ACROSS ALL PREVIEWS):**
- Same neutral female portrait subject in all previews
- Three-quarter view facing slightly left
- Shoulders and upper torso visible
- Serene, neutral expression
- Medium-length hair
- Simple, classic composition

**POSE & COMPOSITION (MUST BE IDENTICAL):**
- Subject positioned identically in every preview
- Head at same angle and position
- Same cropping (shoulders to top of head)
- Centered in frame with consistent margins

**BACKGROUND:**
- Simple, neutral background that works with the art style
- Not distracting from the artistic treatment
- Complementary to the medium and movement specified

**FRAMING:**
- Square format (1024x1024 pixels)
- Subject fills 75% of frame height
- Consistent positioning across all previews

**PURPOSE:**
This is a STANDARDIZED ART STYLE COMPARISON REFERENCE. Every art style preview must use the EXACT SAME subject, pose, and composition. ONLY the artistic medium, technique, and stylistic treatment should vary. A viewer should be able to compare different art styles side-by-side and see clearly how each movement/medium interprets the same subject. Think of this like those "art history evolution" charts showing the same subject painted in different artistic periods."""

    def _build_hair_style_prompt(self, spec: HairStyleSpec) -> str:
        """Build prompt for hair style preview"""
        return f"""Create a professional hair style reference image showing a brown wig on a minimalist mannequin head:

Hair Style: {spec.overall_style}
Cut: {spec.cut}
Length: {spec.length}

Styling Details:
- Layers: {spec.layers}
- Texture: {spec.texture}
- Volume: {spec.volume}
- Parting: {spec.parting}
- Front Styling: {spec.front_styling}

IMPORTANT REQUIREMENTS:
- Hair Color: Medium brown (always use this color regardless of any color mentions in the style description)
- Mannequin: Clean, minimal salon mannequin head with barely visible, simplified facial features (subtle nose bridge, minimal eye/mouth indication)
- The mannequin should look like a professional salon wig display head - smooth, neutral, featureless
- White or very light neutral background
- Professional salon lighting to showcase the hair structure, layers, and styling
- The hair/wig should be the primary focus, not the mannequin
- Render as a high-quality salon product photograph showcasing the hairstyle structure and cut"""

    def _build_hair_color_prompt(self, spec: HairColorSpec) -> str:
        """Build prompt for hair color preview"""
        return f"""Create a beautiful close-up photograph of flowing, wavy hair showcasing this color:

Base Color: {spec.base_color}
Undertones: {spec.undertones}
{f"Highlights: {spec.highlights}" if spec.highlights else ""}
{f"Lowlights: {spec.lowlights}" if spec.lowlights else ""}
{f"Coloring Technique: {spec.technique}" if spec.technique else ""}

Color Characteristics:
- Dimension: {spec.dimension}
- Finish: {spec.finish}

Style: Professional hair color swatch photograph. Show only the flowing, wavy hair texture filling the entire frame - no face, no person, just beautiful cascading waves of hair. The hair should have natural movement and flow with soft S-curves and waves. Lighting should be even and professional to showcase the color dimension, depth, and {spec.finish} finish clearly. The image should look like a luxury hair color reference card or salon color swatch. White or very light neutral background. Focus on displaying the richness, dimension, and beautiful tones of the hair color."""

    def _build_makeup_prompt(self, spec: MakeupSpec) -> str:
        """Build prompt for makeup preview"""
        colors = ", ".join(spec.color_palette[:5]) if spec.color_palette else "varied colors"

        return f"""Create a STANDARDIZED makeup reference following EXACT specifications to ensure consistency across ALL makeup previews.

**CRITICAL: LOCKED-DOWN VISUALIZATION STYLE - NO CREATIVE INTERPRETATION**

Makeup Details to Apply:
- Style: {spec.overall_style}
- Intensity: {spec.intensity}
- Colors: {colors}
- Complexion: {spec.complexion}
- Eyes: {spec.eyes}
- Lips: {spec.lips}

**FACE MODEL SPECIFICATIONS (MUST BE IDENTICAL ACROSS ALL PREVIEWS):**
- Smooth, neutral-toned face mannequin or model (medium skin tone, Fitz III)
- Completely neutral expression - no smile, no emotion
- Eyes looking directly forward at camera, no gaze deviation
- Face perfectly centered and symmetrical
- Head perfectly straight, no tilt
- Minimal facial features/structure variation - aim for an "averaged" neutral face

**POSE & ANGLE (MUST BE IDENTICAL):**
- Direct frontal view, straight-on
- Face fills 65% of frame height
- Eyes positioned at 45% from top of frame
- Shoulders barely visible at bottom, straight and level
- Neck centered and straight

**LIGHTING (MUST BE IDENTICAL):**
- Soft, even beauty lighting from directly front
- No dramatic shadows on face
- Gentle shadow only on neck and below jawline
- Lighting designed to show makeup clearly without creating mood
- No side lighting, no rim lighting, no creative lighting

**BACKGROUND:**
- Pure white (#FFFFFF)
- No gradient, no texture
- Perfectly even and clean

**HAIR:**
- Hair pulled completely back away from face
- Neutral brown or black hair
- No visible hairstyle - hair should not be a focal point
- Clean hairline, no flyaways

**FRAMING:**
- Square format (1024x1024 pixels)
- Face and upper shoulders only
- Equal margins around face
- Makeup must be clearly visible and in sharp focus

**PURPOSE:**
This is NOT a beauty shot - it is a STANDARDIZED MAKEUP REFERENCE. Every makeup preview must look nearly identical except for the makeup application itself. The face, expression, angle, lighting, and background must be perfectly consistent. A viewer should be able to overlay two different makeup previews and see only the makeup differences."""

    def _build_expression_prompt(self, spec: ExpressionSpec) -> str:
        """Build prompt for expression preview"""
        return f"""Create a STANDARDIZED expression reference following EXACT specifications to ensure consistency across ALL expression previews.

**CRITICAL: LOCKED-DOWN VISUALIZATION STYLE - NO CREATIVE INTERPRETATION**

Expression Details to Show:
- Emotion: {spec.primary_emotion}
- Intensity: {spec.intensity}
- Mood: {spec.overall_mood}
- Mouth: {spec.mouth}
- Eyes: {spec.eyes}
- Eyebrows: {spec.eyebrows}
- Gaze: {spec.gaze_direction}

**FACE MODEL SPECIFICATIONS (MUST BE IDENTICAL ACROSS ALL PREVIEWS):**
- Neutral, averaged human face (medium skin tone, androgynous features)
- Same base face structure across all previews - only the EXPRESSION changes
- Clean, minimal features
- No distinctive features like moles, freckles, or unique characteristics
- Hair pulled completely back, not visible

**NEUTRAL BASE (BEFORE EXPRESSION APPLIED):**
- Start with completely neutral face as template
- Same bone structure, same proportions every time
- Apply ONLY the specified expression to this neutral base

**POSE & ANGLE (MUST BE IDENTICAL):**
- Direct frontal view, perfectly centered
- Face fills 70% of frame height
- Eyes positioned at 40% from top of frame
- Head perfectly straight, no tilt, no rotation
- Shoulders barely visible, straight and level

**LIGHTING (MUST BE IDENTICAL):**
- Soft, even frontal lighting
- No dramatic shadows
- Gentle shadow only on neck
- Lighting shows expression clearly without adding mood
- No creative lighting that might enhance or alter emotional read

**BACKGROUND:**
- Pure white (#FFFFFF)
- No gradient, no texture
- Perfectly even

**FRAMING:**
- Square format (1024x1024 pixels)
- Face and minimal shoulders only
- Expression must be clearly visible

**PURPOSE:**
This is NOT a portrait - it is a STANDARDIZED EXPRESSION REFERENCE for actors and animators. Every expression preview must use the IDENTICAL neutral base face. The ONLY difference between previews should be the facial expression itself - the face structure, angle, lighting, and background must be perfectly consistent. A viewer should be able to overlay two different expression previews and see only the muscle movements and expression differences."""

    def _build_accessories_prompt(self, spec: AccessoriesSpec) -> str:
        """Build prompt for accessories preview"""
        jewelry_list = ", ".join(spec.jewelry) if spec.jewelry else "none"
        other_list = ", ".join(spec.other) if spec.other else "none"

        parts = [f"Style: {spec.overall_style}"]
        if spec.jewelry:
            parts.append(f"Jewelry: {jewelry_list}")
        if spec.bags:
            parts.append(f"Bags: {spec.bags}")
        if spec.belts:
            parts.append(f"Belts: {spec.belts}")
        if spec.scarves:
            parts.append(f"Scarves: {spec.scarves}")
        if spec.hats:
            parts.append(f"Hats: {spec.hats}")
        if spec.watches:
            parts.append(f"Watches: {spec.watches}")
        if spec.other:
            parts.append(f"Other: {other_list}")

        description = "\n".join(parts)

        return f"""Create a STANDARDIZED accessories reference following EXACT specifications to ensure consistency across ALL accessory previews.

**CRITICAL: LOCKED-DOWN VISUALIZATION STYLE - NO CREATIVE INTERPRETATION**

Accessories to Display:
{description}

**LAYOUT SPECIFICATIONS (MUST BE IDENTICAL):**
- Clean, professional product photography flat lay
- Accessories arranged on pure white surface (#FFFFFF)
- Symmetrical, organized layout - not scattered or random
- Items positioned to show full detail and scale
- Consistent spacing between items

**STYLING (MUST BE IDENTICAL):**
- No model, no mannequin - flat lay only
- Items arranged as if for professional catalog photography
- Each accessory fully visible, not overlapping
- Jewelry laid flat showing full design
- Bags, hats shown from optimal angle to see shape and details

**LIGHTING (MUST BE IDENTICAL):**
- Soft, even overhead lighting
- No dramatic shadows
- Gentle shadow directly beneath items for depth only
- Professional product photography lighting
- No creative or mood lighting

**BACKGROUND:**
- Pure white (#FFFFFF)
- No texture, no surface details
- Perfectly even and clean

**FRAMING:**
- Square format (1024x1024 pixels)
- Accessories fill 60-70% of frame
- Equal margins on all sides
- All items clearly visible and in focus

**PURPOSE:**
This is NOT a lifestyle shot - it is a STANDARDIZED ACCESSORY CATALOG REFERENCE. Every accessories preview must use identical layout style, lighting, and background. Only the actual accessories themselves should vary. Layout should be clean and organized enough that individual pieces can be easily identified."""

    def visualize(
        self,
        spec_type: str,
        spec: Union[
            VisualStyleSpec,
            ArtStyleSpec,
            HairStyleSpec,
            HairColorSpec,
            MakeupSpec,
            ExpressionSpec,
            AccessoriesSpec
        ],
        output_dir: Union[Path, str] = "output/visualizations",
        preset_id: Optional[str] = None,
        quality: str = "standard"
    ) -> Path:
        """
        Generate visualization for a spec

        Args:
            spec_type: Type of spec (visual-styles, art-styles, etc.)
            spec: The spec object to visualize
            output_dir: Directory to save visualization
            preset_id: Optional preset ID (will generate filename if provided)
            quality: DALL-E quality setting (standard or hd)

        Returns:
            Path to saved visualization
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build prompt
        prompt = self._build_prompt(spec_type, spec)

        # Truncate if too long for DALL-E (4000 char limit)
        if len(prompt) > 3900:
            prompt = prompt[:3900] + "..."

        print(f"🎨 Generating {spec_type} visualization...")

        # Generate image using DALL-E
        image_bytes = self.router.generate_image(
            prompt=prompt,
            model=self.model,
            provider="dalle",
            size="1024x1024",  # Square format
            quality=quality
        )

        # Determine filename
        if preset_id:
            filename = f"{preset_id}_preview.png"
        else:
            filename = f"{spec_type}_preview.png"

        output_path = output_dir / filename

        # Save image
        with open(output_path, 'wb') as f:
            f.write(image_bytes)

        print(f"✅ Saved visualization: {output_path}")

        return output_path
