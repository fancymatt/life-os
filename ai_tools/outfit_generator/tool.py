"""
Outfit Generator Tool

Generates new images with specified outfits applied to a subject.

Features:
- Load outfit from preset or direct specification
- Optional visual style application
- Subject preservation with outfit transformation
- Metadata tracking for generated images
"""

from pathlib import Path
from typing import Optional, Union
from datetime import datetime
import sys
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import OutfitSpec, VisualStyleSpec, ImageGenerationResult, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.preset import PresetManager


class OutfitGenerator:
    """
    Generates images with specified outfits applied to subjects

    Features:
    - Preset-based or direct spec generation
    - Visual style integration
    - Subject identity preservation
    - Metadata and provenance tracking
    """

    def __init__(self, model: Optional[str] = None):
        """
        Initialize the outfit generator

        Args:
            model: Model to use (default from config)
        """
        # Get model from config if not specified
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("outfit_generator")

        self.router = LLMRouter(model=model)
        self.preset_manager = PresetManager()

    def _construct_outfit_prompt(self, outfit: OutfitSpec) -> str:
        """
        Construct a detailed prompt from an OutfitSpec

        Args:
            outfit: The outfit specification

        Returns:
            Formatted prompt text
        """
        prompt_parts = []

        # Add each clothing item with full detail
        for i, item in enumerate(outfit.clothing_items, 1):
            item_desc = f"{i}. {item.item.upper()}"
            item_desc += f"\n   Material: {item.fabric}"
            item_desc += f"\n   Color: {item.color}"
            item_desc += f"\n   Details: {item.details}"
            prompt_parts.append(item_desc)

        outfit_text = "\n\n".join(prompt_parts)

        # Add style context
        style_context = f"\nStyle: {outfit.style_genre} ({outfit.formality})"
        style_context += f"\nAesthetic: {outfit.aesthetic}"

        return outfit_text + style_context

    def _construct_generation_prompt(
        self,
        outfit_prompt: str,
        visual_style: Optional[VisualStyleSpec] = None,
        aspect_ratio: str = "9:16"
    ) -> str:
        """
        Construct the final generation prompt

        Args:
            outfit_prompt: Detailed outfit description
            visual_style: Optional visual style to apply
            aspect_ratio: Image aspect ratio (default 9:16 portrait)

        Returns:
            Complete generation prompt
        """
        prompt = f"""Generate a {aspect_ratio} portrait format image of this person wearing EXACTLY the following outfit with PRECISE COLOR ACCURACY:

{outfit_prompt}

CRITICAL REQUIREMENTS:
- Every color mentioned must be reproduced EXACTLY as specified (e.g., if a white collar is mentioned, it MUST be white, not black or any other color)
- All garment details, trims, patterns, and color combinations must match the description precisely
- Keep their face and features exactly the same
- IMPORTANT: If the person is wearing glasses in the original image, they MUST keep wearing the exact same glasses. If they're not wearing glasses, they should not have glasses in the generated image
- Glasses are NOT part of the outfit - preserve the subject's original eyewear status"""

        if visual_style:
            prompt += f"\n\nVISUAL STYLE REQUIREMENTS:"
            prompt += f"\n- Lighting: {visual_style.lighting}"
            prompt += f"\n- Color Grading: {visual_style.color_grading}"
            prompt += f"\n- Mood: {visual_style.mood}"
            prompt += f"\n- Photography Style: {visual_style.photographic_style}"
            prompt += f"\n- Artistic Style: {visual_style.artistic_style}"
            prompt += f"\n- Camera Angle: {visual_style.camera_angle}"
            prompt += f"\n- Framing: {visual_style.framing}"
        else:
            prompt += f"\n- Show them from the waist up against a pure black background"

        prompt += f"\n- Put them in a different, natural pose from the source image"
        prompt += f"\n- Image must be in {aspect_ratio} aspect ratio"

        prompt += "\n\nThe outfit details provided are from a fashion designer's specification and MUST be followed exactly."

        return prompt

    def generate(
        self,
        subject_image: Union[Path, str],
        outfit: Optional[Union[OutfitSpec, str]] = None,
        visual_style: Optional[Union[VisualStyleSpec, str]] = None,
        output_dir: Union[Path, str] = "output/generated",
        aspect_ratio: str = "9:16",
        temperature: float = 0.8,
        outfit_reference: Optional[Union[Path, str]] = None
    ) -> ImageGenerationResult:
        """
        Generate an image with specified outfit and style

        Args:
            subject_image: Path to subject image
            outfit: OutfitSpec object or preset name
            visual_style: VisualStyleSpec object or preset name
            output_dir: Directory to save generated image
            aspect_ratio: Image aspect ratio (default "9:16")
            temperature: Generation temperature (default 0.8)
            outfit_reference: Optional reference image for the outfit

        Returns:
            ImageGenerationResult with file path and metadata
        """
        subject_image = Path(subject_image)
        output_dir = Path(output_dir)

        if not subject_image.exists():
            raise FileNotFoundError(f"Subject image not found: {subject_image}")

        # Load outfit (from preset or use directly)
        if isinstance(outfit, str):
            print(f"📦 Loading outfit preset: {outfit}")
            outfit = self.preset_manager.load("outfits", outfit, OutfitSpec)
        elif outfit is None:
            raise ValueError("outfit parameter is required (OutfitSpec or preset name)")

        # Load visual style if specified
        visual_style_spec = None
        if isinstance(visual_style, str):
            print(f"🎨 Loading visual style preset: {visual_style}")
            visual_style_spec = self.preset_manager.load("visual_styles", visual_style, VisualStyleSpec)
        elif visual_style is not None:
            visual_style_spec = visual_style

        # Construct prompts
        outfit_prompt = self._construct_outfit_prompt(outfit)
        full_prompt = self._construct_generation_prompt(
            outfit_prompt,
            visual_style_spec,
            aspect_ratio
        )

        print(f"\n🎨 Generating image...")
        print(f"   Subject: {subject_image.name}")
        print(f"   Outfit: {outfit.style_genre} ({outfit.formality})")
        if visual_style_spec:
            print(f"   Style: {visual_style_spec.photographic_style}")

        # Call generation API
        try:
            # Using Gemini 2.5 Flash for image generation
            print(f"\n🎯 Calling Gemini 2.5 Flash Image...")
            image_bytes = self.router.generate_image(
                prompt=full_prompt,
                image_path=subject_image,
                model="gemini-2.5-flash-preview",
                provider="gemini",
                temperature=temperature
            )

            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"{subject_image.stem}_outfit_{timestamp}.png"

            # Save generated image
            with open(output_path, 'wb') as f:
                f.write(image_bytes)

            print(f"✅ Generated: {output_path}")

            # Create result metadata
            result = ImageGenerationResult(
                file_path=str(output_path),
                request={
                    "subject": str(subject_image),
                    "outfit": outfit.model_dump(mode='json'),
                    "visual_style": visual_style_spec.model_dump(mode='json') if visual_style_spec else None
                },
                model_used=self.router.model,
                timestamp=datetime.now()
            )

            return result

        except Exception as e:
            raise Exception(f"Failed to generate image: {e}")


def main():
    """CLI interface for outfit generator"""
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Generate images with specified outfits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with outfit preset
  python tool.py subject.jpg --outfit casual-friday

  # Generate with outfit and style presets
  python tool.py subject.jpg --outfit formal-suit --style film-noir

  # Specify output directory
  python tool.py subject.jpg --outfit summer-dress --output output/my_generations
        """
    )

    parser.add_argument(
        'subject',
        help='Path to subject image'
    )

    parser.add_argument(
        '--outfit',
        required=True,
        help='Outfit preset name or path to OutfitSpec JSON'
    )

    parser.add_argument(
        '--style',
        help='Visual style preset name (optional)'
    )

    parser.add_argument(
        '--output',
        default='output/generated',
        help='Output directory (default: output/generated)'
    )

    parser.add_argument(
        '--aspect-ratio',
        default='9:16',
        help='Aspect ratio (default: 9:16)'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.8,
        help='Generation temperature (default: 0.8)'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    args = parser.parse_args()

    try:
        generator = OutfitGenerator(model=args.model)

        result = generator.generate(
            subject_image=args.subject,
            outfit=args.outfit,
            visual_style=args.style,
            output_dir=args.output,
            aspect_ratio=args.aspect_ratio,
            temperature=args.temperature
        )

        print(f"\n✅ Generation complete!")
        print(f"   Output: {result.file_path}")
        print(f"   Model: {result.model_used}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
