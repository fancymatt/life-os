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
from api.logging_config import get_logger

logger = get_logger(__name__)

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
        preset_prefix: Optional[str] = None,
        selected_analyses: Optional[dict] = None
    ) -> dict:
        """
        Run comprehensive analysis

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup for all analyzers
            save_all_presets: Save all individual analyses as presets
            preset_prefix: Prefix for preset names if saving
            selected_analyses: Dict of which analyses to run (e.g., {'outfit': True, 'art_style': False})

        Returns:
            Dict with created_presets list and individual results
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Default to all analyses if not specified
        if selected_analyses is None:
            selected_analyses = {
                'outfit': True,
                'visual_style': True,
                'art_style': True,
                'hair_style': True,
                'hair_color': True,
                'makeup': True,
                'expression': True,
                'accessories': True
            }

        logger.info(f"\n{'='*70}")
        logger.info(f"COMPREHENSIVE ANALYSIS: {image_path.name}")
        logger.info(f"{'='*70}\n")

        created_presets = []
        results = {}

        # Run selected analyzers
        step = 1
        total_selected = sum(1 for v in selected_analyses.values() if v)

        if selected_analyses.get('outfit', False):
            logger.info(f"[{step}/{total_selected}] Analyzing outfit...")
            outfit = self.outfit_analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=True if save_all_presets else None
            )
            results['outfit'] = outfit
            if save_all_presets:
                created_presets.append({'type': 'Outfit', 'name': outfit.suggested_name})
            step += 1
        else:
            results['outfit'] = None

        if selected_analyses.get('visual_style', False):
            logger.info(f"[{step}/{total_selected}] Analyzing visual style...")
            result = self.visual_style_analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=True if save_all_presets else None
            )
            results['visual_style'] = result
            if save_all_presets:
                created_presets.append({'type': 'Photograph Composition', 'name': result.suggested_name})
            step += 1
        else:
            results['visual_style'] = None

        if selected_analyses.get('art_style', False):
            logger.info(f"[{step}/{total_selected}] Analyzing art style...")
            result = self.art_style_analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=True if save_all_presets else None
            )
            results['art_style'] = result
            if save_all_presets:
                created_presets.append({'type': 'Art Style', 'name': result.suggested_name})
            step += 1
        else:
            results['art_style'] = None

        if selected_analyses.get('hair_style', False):
            logger.info(f"[{step}/{total_selected}] Analyzing hair style...")
            result = self.hair_style_analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=True if save_all_presets else None
            )
            results['hair_style'] = result
            if save_all_presets:
                created_presets.append({'type': 'Hair Style', 'name': result.suggested_name})
            step += 1
        else:
            results['hair_style'] = None

        if selected_analyses.get('hair_color', False):
            logger.info(f"[{step}/{total_selected}] Analyzing hair color...")
            result = self.hair_color_analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=True if save_all_presets else None
            )
            results['hair_color'] = result
            if save_all_presets:
                created_presets.append({'type': 'Hair Color', 'name': result.suggested_name})
            step += 1
        else:
            results['hair_color'] = None

        if selected_analyses.get('makeup', False):
            logger.info(f"[{step}/{total_selected}] Analyzing makeup...")
            result = self.makeup_analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=True if save_all_presets else None
            )
            results['makeup'] = result
            if save_all_presets:
                created_presets.append({'type': 'Makeup', 'name': result.suggested_name})
            step += 1
        else:
            results['makeup'] = None

        if selected_analyses.get('expression', False):
            logger.info(f"[{step}/{total_selected}] Analyzing expression...")
            result = self.expression_analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=True if save_all_presets else None
            )
            results['expression'] = result
            if save_all_presets:
                created_presets.append({'type': 'Expression', 'name': result.suggested_name})
            step += 1
        else:
            results['expression'] = None

        if selected_analyses.get('accessories', False):
            logger.info(f"[{step}/{total_selected}] Analyzing accessories...")
            result = self.accessories_analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=True if save_all_presets else None
            )
            results['accessories'] = result
            if save_all_presets:
                created_presets.append({'type': 'Accessories', 'name': result.suggested_name})
            step += 1
        else:
            results['accessories'] = None

        logger.info(f"\n{'='*70}")
        logger.info(f"COMPREHENSIVE ANALYSIS COMPLETE - {len(created_presets)} presets created")
        logger.info(f"{'='*70}\n")

        return {
            'created_presets': created_presets,
            'results': results
        }


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
        logger.info("\n" + "="*70)
        logger.info("SUMMARY")
        logger.info("="*70)
        logger.info(f"\nOutfit: {result.outfit.style_genre} ({result.outfit.formality})")
        logger.info(f"Visual Style: {result.visual_style.framing} / {result.visual_style.camera_angle}")
        logger.info(f"Art Style: {result.art_style.artistic_movement}")
        logger.info(f"Hair Style: {result.hair_style.overall_style}")
        logger.info(f"Hair Color: {result.hair_color.base_color}")
        logger.info(f"Makeup: {result.makeup.overall_style} ({result.makeup.intensity})")
        logger.info(f"Expression: {result.expression.primary_emotion} ({result.expression.intensity})")
        logger.info(f"Accessories: {result.accessories.overall_style}")
        logger.info("\n" + "="*70)

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
