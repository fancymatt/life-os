#!/usr/bin/env python3
"""
Accessories Analyzer

Analyzes accessories including jewelry, bags, belts, scarves, hats, watches, and overall styling approach.

Usage:
    python ai_tools/accessories_analyzer/tool.py <image_path> [--save-as <preset_name>]
"""

import sys
from pathlib import Path
from typing import Optional, Union, List
import asyncio

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import AccessoriesSpec, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.preset import PresetManager
from ai_tools.shared.cache import CacheManager
from api.config import settings
from dotenv import load_dotenv
from api.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()


class AccessoriesAnalyzer:
    """
    Analyzes accessories and styling details.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None
    ):
        """
        Initialize accessories_analyzer

        Args:
            model: Model to use (default from config)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Cache TTL in seconds (default: 7 days)
        """
        # Get model from config if not specified
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("accessories_analyzer")

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
        custom_template_path = settings.base_dir / "data" / "tool_configs" / "accessories_analyzer_template.md"
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
    ) -> AccessoriesSpec:
        """
        Analyze accessories

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name, or True to use suggested_name
            preset_notes: Optional notes for the preset

        Returns:
            AccessoriesSpec with analysis results
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Check cache first (unless skipped)
        if self.use_cache and not skip_cache:
            cached = self.cache_manager.get_for_file(
                "accessories",
                image_path,
                AccessoriesSpec
            )
            if cached:
                logger.info(f"Using cached analysis for {image_path.name}")

                # Save as preset if requested
                if save_as_preset:
                    # Use suggested_name if save_as_preset is True (boolean)
                    preset_name = cached.suggested_name if save_as_preset is True else save_as_preset
                    preset_path, preset_id = self.preset_manager.save(
                        tool_type="accessories",
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
        logger.info(f"🔍 Analyzing accessories in {image_path.name}...")

        try:
            result = await self.router.acall_structured(
                prompt=prompt_template,
                response_model=AccessoriesSpec,
                images=[image_path],
                temperature=0.3
            )

            # Add metadata
            result._metadata = SpecMetadata(
                tool="accessories_analyzer",
                tool_version="1.0.0",
                source_image=str(image_path),
                source_hash=self.cache_manager.compute_file_hash(image_path),
                model_used=self.router.model
            )

            # Cache the result
            if self.use_cache:
                self.cache_manager.set_for_file(
                    "accessories",
                    image_path,
                    result
                )
                logger.info(f"💾 Cached analysis")

            # Save as preset if requested
            if save_as_preset:
                # Use suggested_name if save_as_preset is True (boolean)
                preset_name = result.suggested_name if save_as_preset is True else save_as_preset
                preset_path, preset_id = self.preset_manager.save(
                    tool_type="accessories",
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
            raise Exception(f"Failed to analyze accessories: {e}")

    def analyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_as_preset: Optional[Union[str, bool]] = None,
        preset_notes: Optional[str] = None
    ) -> AccessoriesSpec:
        """
        Analyze accessories (synchronous wrapper)

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name, or True to use suggested_name
            preset_notes: Optional notes for the preset

        Returns:
            AccessoriesSpec with analysis results
        """
        return asyncio.run(self.aanalyze(
            image_path=image_path,
            skip_cache=skip_cache,
            save_as_preset=save_as_preset,
            preset_notes=preset_notes
        ))

    def analyze_from_preset(self, preset_name: str) -> AccessoriesSpec:
        """Load analysis from a preset"""
        return self.preset_manager.load("accessories", preset_name, AccessoriesSpec)

    def save_to_preset(
        self,
        result: AccessoriesSpec,
        name: str,
        notes: Optional[str] = None
    ) -> Path:
        """Save analysis as a preset"""
        return self.preset_manager.save("accessories", result, display_name=name, notes=notes)

    def list_presets(self) -> List[str]:
        """List all presets"""
        return self.preset_manager.list("accessories")

    def get_cache_stats(self):
        """Get cache statistics"""
        return self.cache_manager.stats()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze accessories in images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze image
  python tool.py image.jpg

  # Analyze and save as preset
  python tool.py image.jpg --save-as minimal-jewelry --notes "Minimal jewelry style"

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

    analyzer = AccessoriesAnalyzer(model=args.model)

    # List presets
    if args.list:
        presets = analyzer.list_presets()
        logger.info(f"\n📋 Accessories Analyzer Presets ({len(presets)}):")
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
        logger.info("Accessories Analysis")
        logger.info("="*70)
        if result.jewelry:
            logger.info(f"\nJewelry ({len(result.jewelry)}):")
            for item in result.jewelry:
                logger.info(f"  - {item}")
        if result.bags:
            logger.info(f"\nBags: {result.bags}")
        if result.belts:
            logger.info(f"Belts: {result.belts}")
        if result.scarves:
            logger.info(f"Scarves: {result.scarves}")
        if result.hats:
            logger.info(f"Hats: {result.hats}")
        if result.watches:
            logger.info(f"Watches: {result.watches}")
        if result.other:
            logger.info(f"\nOther ({len(result.other)}):")
            for item in result.other:
                logger.info(f"  - {item}")
        logger.info(f"\nOverall Style: {result.overall_style}")
        logger.info("\n" + "="*70)

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
