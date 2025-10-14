"""
Visual Style Analyzer Tool

Analyzes images to extract visual/photographic style including:
- Composition and framing
- Lighting setup and quality
- Color palette and grading
- Camera angles and settings
- Post-processing effects
- Era and artistic aesthetic

Supports cache and preset workflows.
"""

from pathlib import Path
from typing import Optional, Union, List
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import VisualStyleSpec, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.cache import CacheManager
from ai_tools.shared.preset import PresetManager


class VisualStyleAnalyzer:
    """
    Analyzes image visual/photographic style to extract structured style data

    Features:
    - Automatic caching (7-day TTL)
    - Preset promotion
    - File hash validation
    - Metadata tracking
    """

    def __init__(
        self,
        model: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None
    ):
        """
        Initialize the visual style analyzer

        Args:
            model: Model to use (default from config)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Cache TTL in seconds (default: 7 days)
        """
        # Get model from config if not specified
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("visual_style_analyzer")

        self.router = LLMRouter(model=model)
        self.use_cache = use_cache
        self.cache_manager = CacheManager(default_ttl=cache_ttl) if cache_ttl else CacheManager()
        self.preset_manager = PresetManager()

        # Load prompt template
        self.template_path = Path(__file__).parent / "template.md"
        with open(self.template_path, 'r') as f:
            self.prompt_template = f.read()

    def analyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_as_preset: Optional[str] = None,
        preset_notes: Optional[str] = None
    ) -> VisualStyleSpec:
        """
        Analyze an image's visual style

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name
            preset_notes: Optional notes for the preset

        Returns:
            VisualStyleSpec with analyzed style data
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Check cache first (unless skipped)
        if self.use_cache and not skip_cache:
            cached = self.cache_manager.get_for_file(
                "visual_styles",
                image_path,
                VisualStyleSpec
            )
            if cached:
                print(f"✅ Using cached analysis for {image_path.name}")
                return cached

        # Perform analysis
        print(f"🔍 Analyzing visual style in {image_path.name}...")

        try:
            style = self.router.call_structured(
                prompt=self.prompt_template,
                response_model=VisualStyleSpec,
                images=[image_path],
                temperature=0.3
            )

            # Add metadata
            style._metadata = SpecMetadata(
                tool="visual-style-analyzer",
                tool_version="1.0.0",
                source_image=str(image_path),
                source_hash=self.cache_manager.compute_file_hash(image_path),
                model_used=self.router.model
            )

            # Cache the result
            if self.use_cache:
                self.cache_manager.set_for_file(
                    "visual_styles",
                    image_path,
                    style
                )
                print(f"💾 Cached analysis")

            # Save as preset if requested
            if save_as_preset:
                preset_path = self.preset_manager.save(
                    "visual_styles",
                    save_as_preset,
                    style,
                    notes=preset_notes
                )
                print(f"⭐ Saved as preset: {save_as_preset}")
                print(f"   Location: {preset_path}")

            return style

        except Exception as e:
            raise Exception(f"Failed to analyze visual style: {e}")

    def analyze_from_preset(self, preset_name: str) -> VisualStyleSpec:
        """
        Load a visual style analysis from a preset

        Args:
            preset_name: Name of the preset

        Returns:
            VisualStyleSpec from preset
        """
        return self.preset_manager.load("visual_styles", preset_name, VisualStyleSpec)

    def save_to_preset(
        self,
        style: VisualStyleSpec,
        name: str,
        notes: Optional[str] = None
    ) -> Path:
        """
        Save a visual style analysis as a preset

        Args:
            style: VisualStyleSpec to save
            name: Preset name
            notes: Optional notes

        Returns:
            Path to saved preset
        """
        return self.preset_manager.save("visual_styles", name, style, notes=notes)

    def list_presets(self) -> List[str]:
        """List all visual style presets"""
        return self.preset_manager.list("visual_styles")

    def get_cache_stats(self):
        """Get cache statistics"""
        return self.cache_manager.stats()


def main():
    """CLI interface for visual style analyzer"""
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Analyze visual/photographic style in an image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze an image
  python tool.py image.jpg

  # Analyze and save as preset
  python tool.py image.jpg --save-as film-noir --notes "High contrast noir style"

  # Skip cache
  python tool.py image.jpg --no-cache

  # List presets
  python tool.py --list
        """
    )

    parser.add_argument(
        'image',
        nargs='?',
        help='Path to image file'
    )

    parser.add_argument(
        '--save-as',
        help='Save result as preset with this name'
    )

    parser.add_argument(
        '--notes',
        help='Notes for the preset'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Skip cache lookup'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all visual style presets'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    args = parser.parse_args()

    analyzer = VisualStyleAnalyzer(model=args.model)

    # List presets
    if args.list:
        presets = analyzer.list_presets()
        print(f"\n📋 Visual Style Presets ({len(presets)}):")
        for preset in presets:
            print(f"  - {preset}")
        return

    # Analyze image
    if not args.image:
        parser.error("Image path required (or use --list)")

    try:
        style = analyzer.analyze(
            args.image,
            skip_cache=args.no_cache,
            save_as_preset=args.save_as,
            preset_notes=args.notes
        )

        # Print results
        print("\n" + "="*70)
        print("Visual Style Analysis")
        print("="*70)
        print(f"\nPhotographic Style: {style.photographic_style}")
        print(f"Artistic Style: {style.artistic_style}")
        print(f"Era Aesthetic: {style.era_aesthetic}")
        print(f"Mood: {style.mood}")

        print(f"\nComposition:")
        print(f"  Framing: {style.framing}")
        print(f"  Camera Angle: {style.camera_angle}")
        print(f"  Composition: {style.composition[:100]}...")

        print(f"\nLighting & Color:")
        print(f"  Lighting: {style.lighting[:100]}...")
        print(f"  Color Grading: {style.color_grading}")
        print(f"  Color Palette: {', '.join(style.color_palette[:5])}")

        print(f"\nTechnical:")
        print(f"  Film Grain: {style.film_grain}")
        print(f"  DOF: {style.depth_of_field}")
        print(f"  Post-Processing: {style.post_processing[:100]}...")

        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
