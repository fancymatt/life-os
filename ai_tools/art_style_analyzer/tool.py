#!/usr/bin/env python3
"""
Art Style Analyzer

Analyzes artistic style of images including medium, technique, composition,
and art historical context.

Usage:
    python ai_tools/art_style_analyzer/tool.py <image_path> [--save-as <preset_name>]
"""

import sys
import json
from pathlib import Path
from typing import Optional, Union, List

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import ArtStyleSpec, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.preset import PresetManager
from ai_tools.shared.cache import CacheManager
from dotenv import load_dotenv

load_dotenv()


class ArtStyleAnalyzer:
    """
    Analyzes artistic style of images.

    Extracts:
    - Artistic medium (oil, watercolor, digital, etc.)
    - Technique (brushwork, application method)
    - Color palette
    - Composition style
    - Art historical movement
    - Mood and atmosphere
    - Level of detail
    """

    def __init__(
        self,
        model: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None
    ):
        """
        Initialize art style analyzer

        Args:
            model: Model to use (default from config)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Cache TTL in seconds (default: 7 days)
        """
        # Get model from config if not specified
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("art_style_analyzer")

        self.router = LLMRouter(model=model)
        self.use_cache = use_cache
        self.cache_manager = CacheManager(default_ttl=cache_ttl) if cache_ttl else CacheManager()
        self.preset_manager = PresetManager()

        # Load prompt template
        template_path = Path(__file__).parent / "template.md"
        with open(template_path) as f:
            self.prompt_template = f.read()

    def analyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_as_preset: Optional[str] = None,
        preset_notes: Optional[str] = None
    ) -> ArtStyleSpec:
        """
        Analyze artistic style of an image

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name
            preset_notes: Optional notes for the preset

        Returns:
            ArtStyleSpec with analysis results
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Check cache first (unless skipped)
        if self.use_cache and not skip_cache:
            cached = self.cache_manager.get_for_file(
                "art_styles",
                image_path,
                ArtStyleSpec
            )
            if cached:
                print(f"✅ Using cached analysis for {image_path.name}")

                # Save as preset if requested
                if save_as_preset:
                    preset_path = self.preset_manager.save(
                        "art_styles",
                        save_as_preset,
                        cached,
                        notes=preset_notes
                    )
                    print(f"⭐ Saved as preset: {save_as_preset}")
                    print(f"   Location: {preset_path}")

                return cached

        # Perform analysis
        print(f"🎨 Analyzing art style in {image_path.name}...")

        try:
            art_style = self.router.call_structured(
                prompt=self.prompt_template,
                response_model=ArtStyleSpec,
                images=[image_path],
                temperature=0.3
            )

            # Add metadata
            art_style._metadata = SpecMetadata(
                tool="art_style_analyzer",
                tool_version="1.0.0",
                source_image=str(image_path),
                source_hash=self.cache_manager.compute_file_hash(image_path),
                model_used=self.router.model
            )

            # Cache the result
            if self.use_cache:
                self.cache_manager.set_for_file(
                    "art_styles",
                    image_path,
                    art_style
                )
                print(f"💾 Cached analysis")

            # Save as preset if requested
            if save_as_preset:
                preset_path = self.preset_manager.save(
                    "art_styles",
                    save_as_preset,
                    art_style,
                    notes=preset_notes
                )
                print(f"⭐ Saved as preset: {save_as_preset}")
                print(f"   Location: {preset_path}")

            return art_style

        except Exception as e:
            raise Exception(f"Failed to analyze art style: {e}")

    def analyze_from_preset(self, preset_name: str) -> ArtStyleSpec:
        """
        Load an art style analysis from a preset

        Args:
            preset_name: Name of the preset

        Returns:
            ArtStyleSpec from preset
        """
        return self.preset_manager.load("art_styles", preset_name, ArtStyleSpec)

    def save_to_preset(
        self,
        art_style: ArtStyleSpec,
        name: str,
        notes: Optional[str] = None
    ) -> Path:
        """
        Save an art style analysis as a preset

        Args:
            art_style: ArtStyleSpec to save
            name: Preset name
            notes: Optional notes

        Returns:
            Path to saved preset
        """
        return self.preset_manager.save("art_styles", art_style, display_name=name, notes=notes)

    def list_presets(self) -> List[str]:
        """List all art style presets"""
        return self.preset_manager.list("art_styles")

    def get_cache_stats(self):
        """Get cache statistics"""
        return self.cache_manager.stats()


def main():
    """CLI interface for art style analyzer"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze artistic style of images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze image
  python tool.py image.jpg

  # Analyze and save as preset
  python tool.py image.jpg --save-as impressionist --notes "Classic impressionist style"

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
        help='List all art style presets'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    args = parser.parse_args()

    analyzer = ArtStyleAnalyzer(model=args.model)

    # List presets
    if args.list:
        presets = analyzer.list_presets()
        print(f"\n📋 Art Style Presets ({len(presets)}):")
        for preset in presets:
            print(f"  - {preset}")
        return

    # Analyze image
    if not args.image:
        parser.error("Image path required (or use --list)")

    try:
        art_style = analyzer.analyze(
            args.image,
            skip_cache=args.no_cache,
            save_as_preset=args.save_as,
            preset_notes=args.notes
        )

        # Print results
        print("\n" + "="*70)
        print("Art Style Analysis")
        print("="*70)
        print(f"\nMedium: {art_style.medium}")
        print(f"Technique: {art_style.technique}")
        print(f"Artistic Movement: {art_style.artistic_movement}")
        print(f"Mood: {art_style.mood}")

        print(f"\nColor Palette ({len(art_style.color_palette)}):")
        print(f"  {', '.join(art_style.color_palette)}")

        if art_style.brush_style:
            print(f"\nBrush Style: {art_style.brush_style}")

        print(f"\nTexture: {art_style.texture}")
        print(f"Composition Style: {art_style.composition_style}")
        print(f"Level of Detail: {art_style.level_of_detail}")

        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
