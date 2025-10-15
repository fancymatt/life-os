"""
Generic Preset Visualizer

Generates preview images for any preset type using DALL-E 3.
Automatically creates appropriate prompts based on the spec type.
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
            model: DALL-E model to use (default: dall-e-3)
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
        Build DALL-E prompt based on spec type

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

        return f"""Create an artistic style reference showing:

Medium: {spec.medium}
Technique: {spec.technique}
Artistic Movement: {spec.artistic_movement}

Visual Characteristics:
- Color Palette: {colors}
- Texture: {spec.texture}
- Composition Style: {spec.composition_style}
- Level of Detail: {spec.level_of_detail}
- Mood: {spec.mood}
{f"- Brush Style: {spec.brush_style}" if spec.brush_style else ""}

Create a portrait or figure study that exemplifies this artistic style on a white background."""

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

        return f"""Create a makeup reference showing:

Makeup Style: {spec.overall_style}
Intensity: {spec.intensity}
Color Palette: {colors}

Application Details:
- Complexion: {spec.complexion}
- Eyes: {spec.eyes}
- Lips: {spec.lips}

Show a beauty portrait focusing on the makeup. White background, even lighting to show makeup details clearly."""

    def _build_expression_prompt(self, spec: ExpressionSpec) -> str:
        """Build prompt for expression preview"""
        return f"""Create a facial expression reference showing:

Primary Emotion: {spec.primary_emotion}
Intensity: {spec.intensity}
Overall Mood: {spec.overall_mood}

Facial Details:
- Mouth: {spec.mouth}
- Eyes: {spec.eyes}
- Eyebrows: {spec.eyebrows}
- Gaze Direction: {spec.gaze_direction}

Show a clean portrait capturing this specific expression. White background, neutral lighting, focus on facial expression."""

    def _build_accessories_prompt(self, spec: AccessoriesSpec) -> str:
        """Build prompt for accessories preview"""
        jewelry_list = ", ".join(spec.jewelry) if spec.jewelry else "none"
        other_list = ", ".join(spec.other) if spec.other else "none"

        parts = [f"Accessory Style: {spec.overall_style}"]

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

        return f"""Create an accessories reference showing:

{description}

Show these accessories on a model or as a styled flat lay. White background, good lighting to show details clearly."""

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
