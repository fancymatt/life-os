#!/usr/bin/env python3
"""
Expression Analyzer

Analyzes facial expression including primary emotion, intensity, mouth/eyes/eyebrows position, gaze direction.

Usage:
    python ai_tools/expression_analyzer/tool.py <image_path> [--save-as <preset_name>]
"""

import sys
from pathlib import Path
from typing import Optional, Union, List
import asyncio

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import ExpressionSpec, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.preset import PresetManager
from ai_tools.shared.cache import CacheManager
from api.config import settings
from dotenv import load_dotenv
from api.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()


class ExpressionAnalyzer:
    """
    Analyzes facial expressions and emotional state.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None
    ):
        """
        Initialize expression_analyzer

        Args:
            model: Model to use (default from config)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Cache TTL in seconds (default: 7 days)
        """
        # Get model from config if not specified
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("expression_analyzer")

        self.router = LLMRouter(model=model)
        self.use_cache = use_cache
        self.cache_manager = CacheManager(default_ttl=cache_ttl) if cache_ttl else CacheManager()
        self.preset_manager = PresetManager()

    def _load_template(self) -> str:
        """
        Load template with override support.

        Checks for custom template first, then falls back to base template.
        """
        # Check for custom template override
        custom_template_path = settings.base_dir / "data" / "tool_configs" / "expression_analyzer_template.md"
        if custom_template_path.exists():
            return custom_template_path.read_text()

        # Fall back to base template
        base_template_path = Path(__file__).parent / "template.md"
        return base_template_path.read_text()

    async def aanalyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_as_preset: Optional[Union[str, bool]] = None,
        preset_notes: Optional[str] = None
    ) -> ExpressionSpec:
        """
        Analyze facial expression (async version)

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name
            preset_notes: Optional notes for the preset

        Returns:
            ExpressionSpec with analysis results
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Check cache first (unless skipped)
        if self.use_cache and not skip_cache:
            cached = self.cache_manager.get_for_file(
                "expressions",
                image_path,
                ExpressionSpec
            )
            if cached:
                logger.info(f"Using cached analysis for {image_path.name}")

                # Save as preset if requested
                if save_as_preset:
                    preset_name = cached.suggested_name if save_as_preset is True else save_as_preset
                    preset_path, preset_id = self.preset_manager.save(
                        tool_type="expressions",
                        data=cached,
                        display_name=preset_name,
                        notes=preset_notes
                    )
                    logger.info(f"Saved as preset: {preset_name}")
                    logger.info(f"   Location: {preset_path}")

                return cached

        # Load template (supports custom overrides)
        prompt_template = self._load_template()

        # Perform analysis
        logger.info(f"🔍 Analyzing facial expression in {image_path.name}...")

        try:
            result = await self.router.acall_structured(
                prompt=prompt_template,
                response_model=ExpressionSpec,
                images=[image_path],
                temperature=0.3
            )

            # Add metadata
            result._metadata = SpecMetadata(
                tool="expression_analyzer",
                tool_version="1.0.0",
                source_image=str(image_path),
                source_hash=self.cache_manager.compute_file_hash(image_path),
                model_used=self.router.model
            )

            # Cache the result
            if self.use_cache:
                self.cache_manager.set_for_file(
                    "expressions",
                    image_path,
                    result
                )
                logger.info(f"💾 Cached analysis")

            # Save as preset if requested
            if save_as_preset:
                preset_name = result.suggested_name if save_as_preset is True else save_as_preset
                preset_path, preset_id = self.preset_manager.save(
                    tool_type="expressions",
                    data=result,
                    display_name=preset_name,
                    notes=preset_notes

                )

                # Update metadata with preset info

                if result._metadata:

                    result._metadata.preset_id = preset_id

                    result._metadata.display_name = preset_name
                logger.info(f"Saved as preset: {preset_name}")
                logger.info(f"   ID: {preset_id}")
                logger.info(f"   Location: {preset_path}")

            return result

        except Exception as e:
            raise Exception(f"Failed to analyze facial expression: {e}")

    def analyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_as_preset: Optional[Union[str, bool]] = None,
        preset_notes: Optional[str] = None
    ) -> ExpressionSpec:
        """
        Analyze facial expression (synchronous wrapper)

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name
            preset_notes: Optional notes for the preset

        Returns:
            ExpressionSpec with analysis results
        """
        return asyncio.run(self.aanalyze(
            image_path=image_path,
            skip_cache=skip_cache,
            save_as_preset=save_as_preset,
            preset_notes=preset_notes
        ))

    def analyze_from_preset(self, preset_name: str) -> ExpressionSpec:
        """Load analysis from a preset"""
        return self.preset_manager.load("expressions", preset_name, ExpressionSpec)

    def save_to_preset(
        self,
        result: ExpressionSpec,
        name: str,
        notes: Optional[str] = None
    ) -> Path:
        """Save analysis as a preset"""
        return self.preset_manager.save("expressions", result, display_name=name, notes=notes)

    def list_presets(self) -> List[str]:
        """List all presets"""
        return self.preset_manager.list("expressions")

    def get_cache_stats(self):
        """Get cache statistics"""
        return self.cache_manager.stats()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze facial expression in images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze image
  python tool.py image.jpg

  # Analyze and save as preset
  python tool.py image.jpg --save-as confident-smile --notes "Confident smiling expression"

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

    analyzer = ExpressionAnalyzer(model=args.model)

    # List presets
    if args.list:
        presets = analyzer.list_presets()
        logger.info(f"\n📋 Expression Analyzer Presets ({len(presets)}):")
        for preset in presets:
            logger.info(f"  - {preset}")
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
        logger.info("\n" + "="*70)
        logger.info("Expression Analysis")
        logger.info("="*70)
        logger.info(f"\nPrimary Emotion: {result.primary_emotion}")
        logger.info(f"Intensity: {result.intensity}")
        logger.info(f"Mouth: {result.mouth}")
        logger.info(f"Eyes: {result.eyes}")
        logger.info(f"Eyebrows: {result.eyebrows}")
        logger.info(f"Gaze Direction: {result.gaze_direction}")
        logger.info(f"Overall Mood: {result.overall_mood}")
        logger.info("\n" + "="*70)

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
