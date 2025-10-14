#!/usr/bin/env python3
"""
Comprehensive Analyzer

Runs all individual analyzers and combines results into a comprehensive analysis.

Usage:
    python ai_tools/comprehensive_analyzer/tool.py <image_path> [--save-all]
"""

import sys
from pathlib import Path
from typing import Optional, Union

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import ComprehensiveSpec, SpecMetadata
from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
from ai_tools.visual_style_analyzer.tool import VisualStyleAnalyzer
from ai_tools.art_style_analyzer.tool import ArtStyleAnalyzer
from ai_tools.hair_style_analyzer.tool import HairStyleAnalyzer
from ai_tools.hair_color_analyzer.tool import HairColorAnalyzer
from ai_tools.makeup_analyzer.tool import MakeupAnalyzer
from ai_tools.expression_analyzer.tool import ExpressionAnalyzer
from ai_tools.accessories_analyzer.tool import AccessoriesAnalyzer
from ai_tools.shared.preset import PresetManager
from ai_tools.shared.cache import CacheManager
from dotenv import load_dotenv

load_dotenv()


class ComprehensiveAnalyzer:
    """
    Comprehensive analyzer that runs all individual analyzers.

    Combines:
    - Outfit analysis
    - Visual style analysis
    - Art style analysis
    - Hair style analysis
    - Hair color analysis
    - Makeup analysis
    - Expression analysis
    - Accessories analysis
    """

    def __init__(
        self,
        model: Optional[str] = None,
        use_cache: bool = True
    ):
        """
        Initialize comprehensive analyzer

        Args:
            model: Model to use for all analyzers (default from config)
            use_cache: Whether to use caching (default: True)
        """
        self.outfit_analyzer = OutfitAnalyzer(model=model, use_cache=use_cache)
        self.visual_style_analyzer = VisualStyleAnalyzer(model=model, use_cache=use_cache)
        self.art_style_analyzer = ArtStyleAnalyzer(model=model, use_cache=use_cache)
        self.hair_style_analyzer = HairStyleAnalyzer(model=model, use_cache=use_cache)
        self.hair_color_analyzer = HairColorAnalyzer(model=model, use_cache=use_cache)
        self.makeup_analyzer = MakeupAnalyzer(model=model, use_cache=use_cache)
        self.expression_analyzer = ExpressionAnalyzer(model=model, use_cache=use_cache)
        self.accessories_analyzer = AccessoriesAnalyzer(model=model, use_cache=use_cache)

        self.preset_manager = PresetManager()
        self.cache_manager = CacheManager()

    def analyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_all_presets: bool = False,
        preset_prefix: Optional[str] = None
    ) -> ComprehensiveSpec:
        """
        Run comprehensive analysis

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup for all analyzers
            save_all_presets: Save all individual analyses as presets
            preset_prefix: Prefix for preset names if saving

        Returns:
            ComprehensiveSpec with all analyses
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        print(f"\n{'='*70}")
        print(f"COMPREHENSIVE ANALYSIS: {image_path.name}")
        print(f"{'='*70}\n")

        # Determine preset names
        if save_all_presets and not preset_prefix:
            preset_prefix = image_path.stem

        # Run all analyzers
        print("[1/8] Analyzing outfit...")
        outfit = self.outfit_analyzer.analyze(
            image_path,
            skip_cache=skip_cache,
            save_as_preset=f"{preset_prefix}-outfit" if save_all_presets else None
        )

        print("\n[2/8] Analyzing visual style...")
        visual_style = self.visual_style_analyzer.analyze(
            image_path,
            skip_cache=skip_cache,
            save_as_preset=f"{preset_prefix}-style" if save_all_presets else None
        )

        print("\n[3/8] Analyzing art style...")
        art_style = self.art_style_analyzer.analyze(
            image_path,
            skip_cache=skip_cache,
            save_as_preset=f"{preset_prefix}-art" if save_all_presets else None
        )

        print("\n[4/8] Analyzing hair style...")
        hair_style = self.hair_style_analyzer.analyze(
            image_path,
            skip_cache=skip_cache,
            save_as_preset=f"{preset_prefix}-hairstyle" if save_all_presets else None
        )

        print("\n[5/8] Analyzing hair color...")
        hair_color = self.hair_color_analyzer.analyze(
            image_path,
            skip_cache=skip_cache,
            save_as_preset=f"{preset_prefix}-haircolor" if save_all_presets else None
        )

        print("\n[6/8] Analyzing makeup...")
        makeup = self.makeup_analyzer.analyze(
            image_path,
            skip_cache=skip_cache,
            save_as_preset=f"{preset_prefix}-makeup" if save_all_presets else None
        )

        print("\n[7/8] Analyzing expression...")
        expression = self.expression_analyzer.analyze(
            image_path,
            skip_cache=skip_cache,
            save_as_preset=f"{preset_prefix}-expression" if save_all_presets else None
        )

        print("\n[8/8] Analyzing accessories...")
        accessories = self.accessories_analyzer.analyze(
            image_path,
            skip_cache=skip_cache,
            save_as_preset=f"{preset_prefix}-accessories" if save_all_presets else None
        )

        # Create comprehensive spec
        comprehensive = ComprehensiveSpec(
            outfit=outfit,
            visual_style=visual_style,
            art_style=art_style,
            hair_style=hair_style,
            hair_color=hair_color,
            makeup=makeup,
            expression=expression,
            accessories=accessories
        )

        # Add metadata
        comprehensive._metadata = SpecMetadata(
            tool="comprehensive_analyzer",
            tool_version="1.0.0",
            source_image=str(image_path),
            source_hash=self.cache_manager.compute_file_hash(image_path),
            model_used=self.outfit_analyzer.router.model
        )

        print(f"\n{'='*70}")
        print("COMPREHENSIVE ANALYSIS COMPLETE")
        print(f"{'='*70}\n")

        return comprehensive


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run comprehensive analysis on an image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze image
  python tool.py image.jpg

  # Save all analyses as presets
  python tool.py image.jpg --save-all

  # Custom preset prefix
  python tool.py image.jpg --save-all --prefix my-look

  # Skip cache
  python tool.py image.jpg --no-cache
        """
    )

    parser.add_argument(
        'image',
        help='Path to image file'
    )

    parser.add_argument(
        '--save-all',
        action='store_true',
        help='Save all analyses as presets'
    )

    parser.add_argument(
        '--prefix',
        help='Prefix for preset names (default: image filename)'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Skip cache lookup'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    args = parser.parse_args()

    try:
        analyzer = ComprehensiveAnalyzer(model=args.model)
        result = analyzer.analyze(
            args.image,
            skip_cache=args.no_cache,
            save_all_presets=args.save_all,
            preset_prefix=args.prefix
        )

        # Print summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"\n✅ Outfit: {result.outfit.style_genre} ({result.outfit.formality})")
        print(f"✅ Visual Style: {result.visual_style.photographic_style}")
        print(f"✅ Art Style: {result.art_style.artistic_movement}")
        print(f"✅ Hair Style: {result.hair_style.overall_style}")
        print(f"✅ Hair Color: {result.hair_color.base_color}")
        print(f"✅ Makeup: {result.makeup.overall_style} ({result.makeup.intensity})")
        print(f"✅ Expression: {result.expression.primary_emotion} ({result.expression.intensity})")
        print(f"✅ Accessories: {result.accessories.overall_style}")
        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
