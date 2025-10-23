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
from api.logging_config import get_logger

logger = get_logger(__name__)


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

    def create_preset_preview(
        self,
        preset_data: dict,
        output_path: str,
        category: str,
        viz_config: Optional[dict] = None
    ) -> Path:
        """
        Generate preview image for a preset, optionally using visualization config

        Args:
            preset_data: Dictionary containing preset data
            output_path: Full path where image should be saved
            category: Preset category (e.g., 'expressions', 'makeup')
            viz_config: Optional visualization config to override defaults

        Returns:
            Path to saved preview image
        """
        # Convert category to spec type
        spec_type_map = {
            "visual_styles": "visual_styles",
            "art_styles": "art_styles",
            "hair_styles": "hair_styles",
            "hair_colors": "hair_colors",
            "makeup": "makeup",
            "expressions": "expressions",
            "accessories": "accessories"
        }
        spec_type = spec_type_map.get(category, category)

        # Load preset data into spec object
        spec_class_map = {
            "visual_styles": VisualStyleSpec,
            "art_styles": ArtStyleSpec,
            "hair_styles": HairStyleSpec,
            "hair_colors": HairColorSpec,
            "makeup": MakeupSpec,
            "expressions": ExpressionSpec,
            "accessories": AccessoriesSpec
        }

        spec_class = spec_class_map.get(spec_type)
        if not spec_class:
            raise ValueError(f"Unknown category: {category}")

        spec = spec_class(**preset_data)

        # Build prompt - use viz config if provided, otherwise use default
        if viz_config:
            prompt = self._build_prompt_with_viz_config(spec_type, spec, viz_config)
            model = viz_config.get("model", "gemini/gemini-2.5-flash-image")
            size = viz_config.get("image_size", "1024x1024")
            reference_image = viz_config.get("reference_image_path")
        else:
            prompt = self._build_prompt(spec_type, spec)
            model = self.model
            size = "1024x1024"
            reference_image = None

        logger.info(f"Generating preview for {category} preset with model {model}...")
        logger.info(f"📝 PROMPT BEING SENT TO MODEL:\n{'-'*80}\n{prompt}\n{'-'*80}")
        if reference_image:
            logger.info(f"🖼️  REFERENCE IMAGE: {reference_image}")
        else:
            logger.info(f"🖼️  NO REFERENCE IMAGE")

        # Determine provider based on model and whether reference image exists
        if "dall-e" in model.lower():
            provider = "dalle"
            quality = "standard"
            # Truncate if too long for DALL-E (4000 char limit)
            if len(prompt) > 3900:
                prompt = prompt[:3900] + "..."
            image_bytes = self.router.generate_image(
                prompt=prompt,
                model=model,
                provider=provider,
                size=size,
                quality=quality
            )
        elif "gemini" in model.lower():
            # Gemini REQUIRES a reference image for image generation
            # If no reference image, fall back to DALL-E
            if reference_image and Path(reference_image).exists():
                logger.info(f"Using Gemini with reference image: {reference_image}")
                image_bytes = self.router.generate_image(
                    prompt=prompt,
                    model=model,
                    provider="gemini",
                    size=size,
                    image_path=reference_image
                )
            else:
                logger.warning(f"No reference image found for Gemini model - falling back to DALL-E")
                # Fall back to DALL-E when no reference image
                if len(prompt) > 3900:
                    prompt = prompt[:3900] + "..."
                image_bytes = self.router.generate_image(
                    prompt=prompt,
                    model="dall-e-3",
                    provider="dalle",
                    size="1024x1024",
                    quality="standard"
                )
        else:
            # Default to DALL-E
            provider = "dalle"
            quality = "standard"
            if len(prompt) > 3900:
                prompt = prompt[:3900] + "..."
            image_bytes = self.router.generate_image(
                prompt=prompt,
                model=model,
                provider=provider,
                size=size,
                quality=quality
            )

        # Save image
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(image_bytes)

        logger.info(f"Saved preview: {output_path}")

        return output_path

    def _build_prompt_with_viz_config(
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
        viz_config: dict
    ) -> str:
        """
        Build prompt using visualization config settings

        Args:
            spec_type: Type of spec
            spec: The spec object
            viz_config: Visualization configuration

        Returns:
            Custom prompt string incorporating viz config
        """
        logger.info(f"🔧 VIZ CONFIG DATA: {viz_config}")

        # Check if we have a reference image and additional instructions
        has_reference = viz_config.get("reference_image_path") and Path(viz_config.get("reference_image_path")).exists()
        additional_instructions = viz_config.get("additional_instructions", "")

        # Get base subject description from the spec
        # When using custom viz config with reference image and instructions,
        # simplify the description to avoid conflicting details
        if has_reference and additional_instructions and spec_type == "expressions":
            # For expressions with custom viz, use simplified description
            # that focuses on emotion/mood, not styling details
            subject_description = self._extract_simplified_expression_description(spec)
        else:
            # For other cases, use full description
            subject_description = self._extract_subject_description(spec_type, spec)

        logger.info(f"📋 SUBJECT DESCRIPTION: {subject_description}")

        # Get additional instructions (primary driver)
        additional_instructions = viz_config.get("additional_instructions", "")

        # Load art style if specified (secondary driver)
        art_style_guidance = ""
        art_style_id = viz_config.get("art_style_id")
        if art_style_id:
            try:
                # Load the art style preset
                from api.config import settings
                art_style_path = settings.presets_dir / "art_styles" / f"{art_style_id}.json"
                if art_style_path.exists():
                    import json
                    with open(art_style_path, 'r') as f:
                        art_style_data = json.load(f)

                    art_style_guidance = f"""
ART STYLE:
- Medium: {art_style_data.get('medium', 'mixed media')}
- Technique: {art_style_data.get('technique', 'varied')}
- Movement: {art_style_data.get('artistic_movement', 'contemporary')}
- Mood: {art_style_data.get('mood', 'neutral')}
- Texture: {art_style_data.get('texture', 'smooth')}
- Detail Level: {art_style_data.get('level_of_detail', 'high')}
"""
            except Exception as e:
                logger.warning(f"Could not load art style {art_style_id}: {e}")

        # Build minimal custom prompt
        # If reference image will be included, tell the model to match its style
        has_reference = viz_config.get("reference_image_path") and Path(viz_config.get("reference_image_path")).exists()
        logger.info(f"🎨 ART STYLE GUIDANCE: {art_style_guidance if art_style_guidance else '(none)'}")
        logger.info(f"📝 ADDITIONAL INSTRUCTIONS: {additional_instructions if additional_instructions else '(none)'}")
        logger.info(f"🖼️  HAS REFERENCE IMAGE: {has_reference}")

        if has_reference:
            prompt = f"""Look at the reference image I've provided. Your task is to create a NEW image using the SAME artistic style, technique, and visual treatment.

🎨 CRITICAL REQUIREMENTS (HIGHEST PRIORITY):
{additional_instructions if additional_instructions else "Match the reference image style exactly"}

📋 SUBJECT/EXPRESSION TO PORTRAY:
{subject_description}
{art_style_guidance}

IMPORTANT: The CRITICAL REQUIREMENTS above override any styling details in the subject description. If there's a conflict (e.g., subject mentions colors but requirements say "NO COLOR"), follow the CRITICAL REQUIREMENTS. Focus on capturing the emotional/structural aspects of the subject using the artistic style shown in the reference image."""
        else:
            prompt = f"""Create a reference image showing this {spec_type.replace('_', ' ')} preset.

SUBJECT DETAILS:
{subject_description}
{art_style_guidance}
{f"INSTRUCTIONS: {additional_instructions}" if additional_instructions else ""}"""

        return prompt

    def _extract_simplified_expression_description(self, spec: ExpressionSpec) -> str:
        """
        Extract a simplified expression description that focuses on emotion and
        facial muscle movements, stripping out styling details like makeup colors,
        lipstick shades, etc. that might conflict with custom visualization styles.

        Args:
            spec: The expression spec object

        Returns:
            Simplified description string focusing on structural/emotional aspects
        """
        import re

        def simplify_description(text: str) -> str:
            """Remove color, makeup, and styling details from a description"""
            # Remove specific styling details that might conflict with custom viz
            patterns_to_remove = [
                r'painted with.*?lipstick',
                r'vibrant red lipstick',
                r'dark eyeliner',
                r'long lashes',
                r'full and.*?lips',
                r'almond-shaped',
                r'framed by.*?\.',
                r'well-defined and arched',
                r'symmetrical and well-groomed'
            ]

            cleaned = text
            for pattern in patterns_to_remove:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

            # Clean up extra whitespace and periods
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            cleaned = re.sub(r'\.\s*\.', '.', cleaned)

            return cleaned

        # Simplify each component
        mouth_simplified = simplify_description(spec.mouth)
        eyes_simplified = simplify_description(spec.eyes)
        eyebrows_simplified = simplify_description(spec.eyebrows)

        return f"""Expression: {spec.primary_emotion}
Intensity: {spec.intensity}
Overall Emotion: {spec.overall_mood}

Facial Muscle Movements:
- Mouth: {mouth_simplified}
- Eyes: {eyes_simplified}
- Eyebrows: {eyebrows_simplified}"""

    def _extract_subject_description(
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
        ]
    ) -> str:
        """
        Extract the core subject description from a spec

        Args:
            spec_type: Type of spec
            spec: The spec object

        Returns:
            Description string
        """
        if spec_type == "expressions":
            return f"""Expression: {spec.primary_emotion}
Intensity: {spec.intensity}
Mood: {spec.overall_mood}
Mouth: {spec.mouth}
Eyes: {spec.eyes}
Eyebrows: {spec.eyebrows}"""

        elif spec_type == "makeup":
            colors = ", ".join(spec.color_palette[:5]) if spec.color_palette else "varied"
            return f"""Style: {spec.overall_style}
Intensity: {spec.intensity}
Colors: {colors}
Complexion: {spec.complexion}
Eyes: {spec.eyes}
Lips: {spec.lips}"""

        elif spec_type == "accessories":
            parts = [f"Style: {spec.overall_style}"]
            if spec.jewelry:
                parts.append(f"Jewelry: {', '.join(spec.jewelry)}")
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
                parts.append(f"Other: {', '.join(spec.other)}")
            return "\n".join(parts)

        elif spec_type == "art_styles":
            colors = ", ".join(spec.color_palette[:5]) if spec.color_palette else "varied"
            return f"""Medium: {spec.medium}
Technique: {spec.technique}
Movement: {spec.artistic_movement}
Colors: {colors}
Texture: {spec.texture}
Detail Level: {spec.level_of_detail}
Mood: {spec.mood}"""

        elif spec_type == "hair_styles":
            return f"""Style: {spec.overall_style}
Cut: {spec.cut}
Length: {spec.length}
Layers: {spec.layers}
Texture: {spec.texture}
Volume: {spec.volume}
Parting: {spec.parting}
Front Styling: {spec.front_styling}"""

        elif spec_type == "hair_colors":
            return f"""Base Color: {spec.base_color}
Undertones: {spec.undertones}
{f"Highlights: {spec.highlights}" if spec.highlights else ""}
{f"Lowlights: {spec.lowlights}" if spec.lowlights else ""}
Dimension: {spec.dimension}
Finish: {spec.finish}"""

        elif spec_type == "visual_styles":
            return f"""Subject & Pose: {spec.subject_action}
Setting: {spec.setting}
Framing: {spec.framing}
Angle: {spec.camera_angle}
Lighting: {spec.lighting}
Mood: {spec.mood}"""

        else:
            return str(spec.model_dump())

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

        logger.info(f"Generating {spec_type} visualization...")

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

        logger.info(f"Saved visualization: {output_path}")

        return output_path
