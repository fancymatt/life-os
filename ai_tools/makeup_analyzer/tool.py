#!/usr/bin/env python3
"""
Makeup Analyzer

Analyzes makeup including complexion (foundation, blush, contour), eyes (shadow, liner, mascara), lips, and overall style.

Usage:
    python ai_tools/makeup_analyzer/tool.py <image_path> [--save-as <preset_name>]
"""

import sys
from pathlib import Path
from typing import Optional, Union, List

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import MakeupSpec, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.preset import PresetManager
from ai_tools.shared.cache import CacheManager
from dotenv import load_dotenv

load_dotenv()


class MakeupAnalyzer:
    """
    Analyzes makeup application and style.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None
    ):
        """
        Initialize makeup_analyzer

        Args:
            model: Model to use (default from config)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Cache TTL in seconds (default: 7 days)
        """
        # Get model from config if not specified
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("makeup_analyzer")

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
    ) -> MakeupSpec:
        """
        Analyze makeup

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name
            preset_notes: Optional notes for the preset

        Returns:
            MakeupSpec with analysis results
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Check cache first (unless skipped)
        if self.use_cache and not skip_cache:
            cached = self.cache_manager.get_for_file(
                "makeup",
                image_path,
                MakeupSpec
            )
            if cached:
                print(f"✅ Using cached analysis for {image_path.name}")

                # Save as preset if requested
                if save_as_preset:
                    preset_path = self.preset_manager.save(
                        "makeup",
                        save_as_preset,
                        cached,
                        notes=preset_notes
                    )
                    print(f"⭐ Saved as preset: {save_as_preset}")
                    print(f"   Location: {preset_path}")

                return cached

        # Perform analysis
        print(f"🔍 Analyzing makeup in {image_path.name}...")

        try:
            result = self.router.call_structured(
                prompt=self.prompt_template,
                response_model=MakeupSpec,
                images=[image_path],
                temperature=0.3
            )

            # Add metadata
            result._metadata = SpecMetadata(
                tool="makeup_analyzer",
                tool_version="1.0.0",
                source_image=str(image_path),
                source_hash=self.cache_manager.compute_file_hash(image_path),
                model_used=self.router.model
            )

            # Cache the result
            if self.use_cache:
                self.cache_manager.set_for_file(
                    "makeup",
                    image_path,
                    result
                )
                print(f"💾 Cached analysis")

            # Save as preset if requested
            if save_as_preset:
                preset_path = self.preset_manager.save(
                    "makeup",
                    save_as_preset,
                    result,
                    notes=preset_notes
                )
                print(f"⭐ Saved as preset: {save_as_preset}")
                print(f"   Location: {preset_path}")

            return result

        except Exception as e:
            raise Exception(f"Failed to analyze makeup: {e}")

    def analyze_from_preset(self, preset_name: str) -> MakeupSpec:
        """Load analysis from a preset"""
        return self.preset_manager.load("makeup", preset_name, MakeupSpec)

    def save_to_preset(
        self,
        result: MakeupSpec,
        name: str,
        notes: Optional[str] = None
    ) -> Path:
        """Save analysis as a preset"""
        return self.preset_manager.save("makeup", name, result, notes=notes)

    def list_presets(self) -> List[str]:
        """List all presets"""
        return self.preset_manager.list("makeup")

    def get_cache_stats(self):
        """Get cache statistics"""
        return self.cache_manager.stats()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze makeup in images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze image
  python tool.py image.jpg

  # Analyze and save as preset
  python tool.py image.jpg --save-as natural-makeup --notes "Natural everyday makeup"

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
        help='List all presets'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    args = parser.parse_args()

    analyzer = MakeupAnalyzer(model=args.model)

    # List presets
    if args.list:
        presets = analyzer.list_presets()
        print(f"\n📋 Makeup Analyzer Presets ({len(presets)}):")
        for preset in presets:
            print(f"  - {preset}")
        return

    # Analyze image
    if not args.image:
        parser.error("Image path required (or use --list)")

    try:
        result = analyzer.analyze(
            args.image,
            skip_cache=args.no_cache,
            save_as_preset=args.save_as,
            preset_notes=args.notes
        )

        # Print results
        print("\n" + "="*70)
        print("Makeup Analysis")
        print("="*70)
        print(f"\nComplexion: {result.complexion}")
        print(f"Eyes: {result.eyes}")
        print(f"Lips: {result.lips}")
        print(f"Overall Style: {result.overall_style}")
        print(f"Intensity: {result.intensity}")
        print(f"\nColor Palette ({len(result.color_palette)}):")
        print(f"  {', '.join(result.color_palette)}")
        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
