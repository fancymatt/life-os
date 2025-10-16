"""
Outfit Visualizer Tool

Creates standalone visualizations of outfits from their specifications.
Unlike outfit_generator which applies outfits to people, this creates
clean reference images showing the outfit itself on a mannequin or as a flat lay.

Features:
- Pure text-to-image generation from outfit specs
- Square format on white background
- Automatic generation when presets are saved
- Reference images for verification
"""

from pathlib import Path
from typing import Optional, Union
from datetime import datetime
import sys
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import OutfitSpec, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.preset import PresetManager


class OutfitVisualizer:
    """
    Generates standalone visualizations of outfit specifications

    Creates clean, reference-quality images showing outfits on
    mannequins or as styled flat lays on white backgrounds.
    """

    def __init__(self, model: Optional[str] = None):
        """
        Initialize the outfit visualizer

        Args:
            model: Model to use for generation (default: gemini-2.5-flash-image)
        """
        # Use Gemini 2.5 Flash for image generation
        self.model = model or "gemini-2.5-flash-image"
        self.router = LLMRouter(model=self.model)
        self.preset_manager = PresetManager()

        # Load prompt template
        self.template_path = Path(__file__).parent / "template.md"
        with open(self.template_path, 'r') as f:
            self.prompt_template = f.read()

    def _construct_outfit_description(self, outfit: OutfitSpec) -> str:
        """
        Construct detailed description from outfit spec

        Args:
            outfit: The outfit specification

        Returns:
            Formatted description text
        """
        parts = []

        # Overall context
        parts.append(f"OUTFIT STYLE: {outfit.style_genre}")
        parts.append(f"FORMALITY: {outfit.formality}")
        parts.append(f"AESTHETIC: {outfit.aesthetic}")

        if outfit.season:
            parts.append(f"SEASON: {outfit.season}")
        if outfit.occasion:
            parts.append(f"OCCASION: {outfit.occasion}")

        parts.append("\nCLOTHING ITEMS:")

        # Each clothing item with full details
        for i, item in enumerate(outfit.clothing_items, 1):
            item_desc = f"\n{i}. {item.item.upper()}"
            item_desc += f"\n   - Fabric: {item.fabric}"
            item_desc += f"\n   - Color: {item.color}"
            item_desc += f"\n   - Details: {item.details}"
            parts.append(item_desc)

        return "\n".join(parts)

    def _construct_generation_prompt(self, outfit: OutfitSpec) -> str:
        """
        Construct the complete generation prompt

        Args:
            outfit: Outfit specification

        Returns:
            Complete prompt for image generation
        """
        outfit_description = self._construct_outfit_description(outfit)

        prompt = f"""{self.prompt_template}

{outfit_description}

Create a professional, clean visualization that accurately represents all these details. The outfit should be displayed on a simple mannequin (no face, minimal features) in a natural, well-composed arrangement against a pure white background.

**CRITICAL COLOR ACCURACY:**
All colors must exactly match the specifications above. If a garment is described as white, it must be white in the image. Pay careful attention to getting every color and detail correct.

Style the presentation to match the {outfit.aesthetic} aesthetic while maintaining clarity and professionalism."""

        return prompt

    def visualize(
        self,
        outfit: Union[OutfitSpec, str],
        output_dir: Union[Path, str] = "output/visualizations",
        preset_id: Optional[str] = None,
        quality: str = "standard"
    ) -> Path:
        """
        Generate a visualization of an outfit

        Args:
            outfit: OutfitSpec object or preset name/ID
            output_dir: Directory to save visualization
            preset_id: Optional preset ID for filename
            quality: Image quality ("standard" or "hd")

        Returns:
            Path to generated visualization
        """
        output_dir = Path(output_dir)

        # Load outfit if given as preset name/ID
        if isinstance(outfit, str):
            print(f"📦 Loading outfit preset: {outfit}")
            outfit = self.preset_manager.load("outfits", outfit, OutfitSpec)

        # Construct generation prompt
        prompt = self._construct_generation_prompt(outfit)

        print(f"\n🎨 Generating outfit visualization...")
        print(f"   Style: {outfit.style_genre} ({outfit.formality})")
        print(f"   Aesthetic: {outfit.aesthetic}")
        print(f"   Items: {len(outfit.clothing_items)}")

        try:
            # Generate image using Gemini 2.5 Flash
            image_bytes = self.router.generate_image(
                prompt=prompt,
                model=self.model,
                provider="gemini",
                size="1024x1024",  # Square format
                quality=quality
            )

            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate output filename
            if preset_id:
                filename = f"{preset_id}_preview.png"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"outfit_viz_{timestamp}.png"

            output_path = output_dir / filename

            # Save generated image
            with open(output_path, 'wb') as f:
                f.write(image_bytes)

            print(f"✅ Visualization saved: {output_path}")

            return output_path

        except Exception as e:
            raise Exception(f"Failed to generate visualization: {e}")

    def visualize_from_preset_file(
        self,
        preset_path: Union[Path, str],
        output_dir: Union[Path, str] = None
    ) -> Path:
        """
        Generate visualization from a preset file

        Args:
            preset_path: Path to preset JSON file
            output_dir: Optional output directory (defaults to same as preset)

        Returns:
            Path to generated visualization
        """
        preset_path = Path(preset_path)

        # Load outfit from file
        with open(preset_path, 'r') as f:
            data = json.load(f)

        outfit = OutfitSpec(**data)

        # Extract preset ID from metadata or filename
        preset_id = None
        if outfit._metadata and outfit._metadata.preset_id:
            preset_id = outfit._metadata.preset_id
        else:
            preset_id = preset_path.stem

        # Default output to same directory as preset
        if output_dir is None:
            output_dir = preset_path.parent

        return self.visualize(
            outfit=outfit,
            output_dir=output_dir,
            preset_id=preset_id
        )


def main():
    """CLI interface for outfit visualizer"""
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Generate standalone outfit visualizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visualize from preset ID
  python tool.py --preset casual-friday

  # Visualize from preset file
  python tool.py --file presets/outfits/abc123.json

  # Specify output directory
  python tool.py --preset formal-suit --output output/my_viz

  # Use HD quality
  python tool.py --preset summer-dress --quality hd
        """
    )

    parser.add_argument(
        '--preset',
        help='Preset name or ID to visualize'
    )

    parser.add_argument(
        '--file',
        help='Path to preset JSON file'
    )

    parser.add_argument(
        '--output',
        default='output/visualizations',
        help='Output directory (default: output/visualizations)'
    )

    parser.add_argument(
        '--quality',
        choices=['standard', 'hd'],
        default='standard',
        help='Image quality (default: standard)'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default: gemini-2.5-flash-image)'
    )

    args = parser.parse_args()

    if not args.preset and not args.file:
        parser.error("Either --preset or --file must be specified")

    try:
        visualizer = OutfitVisualizer(model=args.model)

        if args.file:
            output_path = visualizer.visualize_from_preset_file(
                preset_path=args.file,
                output_dir=args.output
            )
        else:
            output_path = visualizer.visualize(
                outfit=args.preset,
                output_dir=args.output,
                quality=args.quality
            )

        print(f"\n✅ Visualization complete!")
        print(f"   Output: {output_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
