"""
Photograph Composition Analyzer Tool

Analyzes images to describe photograph composition:
- What the subject is doing in the frame
- Where the scene is taking place
- Basic framing and camera angle
- Lighting description
- Overall mood and atmosphere

Supports cache and preset workflows.
"""

from pathlib import Path
from typing import Optional, Union, List
import sys
import asyncio

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import VisualStyleSpec, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.cache import CacheManager
from ai_tools.shared.preset import PresetManager
from api.config import settings
from api.logging_config import get_logger

logger = get_logger(__name__)


class VisualStyleAnalyzer:
    """
    Analyzes photograph composition to describe what's happening in the frame

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
        Initialize the photograph composition analyzer

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

    def _load_template(self) -> str:
        """
        Load template with override support.

        Checks for custom template first, then falls back to base template.
        """
        # Check for custom template override
        custom_template_path = settings.base_dir / "data" / "tool_configs" / "visual_style_analyzer_template.md"
        if custom_template_path.exists():
            return custom_template_path.read_text()

        # Fall back to base template
        base_template_path = Path(__file__).parent / "template.md"
        return base_template_path.read_text()

    async def aanalyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_as_preset: Optional[str] = None,
        preset_notes: Optional[str] = None
    ) -> VisualStyleSpec:
        """
        Analyze photograph composition (async version)

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name
            preset_notes: Optional notes for the preset

        Returns:
            PhotoCompositionSpec with analyzed composition data
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
                logger.info(f"Using cached analysis for {image_path.name}")
                return cached

        # Load template (supports custom overrides)
        prompt_template = self._load_template()

        # Perform analysis
        logger.info(f"🔍 Analyzing photograph composition in {image_path.name}...")

        try:
            style = await self.router.acall_structured(
                prompt=prompt_template,
                response_model=VisualStyleSpec,
                images=[image_path],
                temperature=0.7  # Higher temperature for more detailed, verbose descriptions
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
                logger.info(f"💾 Cached analysis")

            # Save as preset if requested
            if save_as_preset:
                # If save_as_preset is True (boolean), use the AI-generated suggested_name
                preset_name = style.suggested_name if save_as_preset is True else save_as_preset

                preset_path, preset_id = self.preset_manager.save(
                    "visual_styles",
                    style,
                    display_name=preset_name,
                    notes=preset_notes
                )
                # Update metadata with preset info
                if style._metadata:
                    style._metadata.preset_id = preset_id
                    style._metadata.display_name = preset_name
                logger.info(f"Saved as preset: {preset_name}")
                logger.info(f"   ID: {preset_id}")
                logger.info(f"   Location: {preset_path}")

            return style

        except Exception as e:
            raise Exception(f"Failed to analyze photograph composition: {e}")

    def analyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_as_preset: Optional[str] = None,
        preset_notes: Optional[str] = None
    ) -> VisualStyleSpec:
        """
        Analyze photograph composition (synchronous wrapper)

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name
            preset_notes: Optional notes for the preset

        Returns:
            PhotoCompositionSpec with analyzed composition data
        """
        return asyncio.run(self.aanalyze(
            image_path=image_path,
            skip_cache=skip_cache,
            save_as_preset=save_as_preset,
            preset_notes=preset_notes
        ))

    def analyze_from_preset(self, preset_name: str) -> VisualStyleSpec:
        """
        Load a photograph composition analysis from a preset

        Args:
            preset_name: Name of the preset

        Returns:
            PhotoCompositionSpec from preset
        """
        return self.preset_manager.load("visual_styles", preset_name, VisualStyleSpec)

    def save_to_preset(
        self,
        style: VisualStyleSpec,
        name: str,
        notes: Optional[str] = None
    ) -> Path:
        """
        Save a photograph composition analysis as a preset

        Args:
            style: PhotoCompositionSpec to save
            name: Preset name
            notes: Optional notes

        Returns:
            Path to saved preset
        """
        return self.preset_manager.save("visual_styles", style, display_name=name, notes=notes)

    def list_presets(self) -> List[str]:
        """List all photograph composition presets"""
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
        description="Analyze photograph composition in an image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze an image
  python tool.py image.jpg

  # Analyze and save as preset
  python tool.py image.jpg --save-as cafe-scene --notes "Subject sitting at cafe table"

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
        help='List all photograph composition presets'
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
        logger.info(f"\n📋 Photograph Composition Presets ({len(presets)}):")
        for preset in presets:
            logger.info(f"  - {preset}")
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
        logger.info("\n" + "="*70)
        logger.info("Photograph Composition Analysis")
        logger.info("="*70)
        logger.info(f"\nSubject Action: {style.subject_action}")
        logger.info(f"Setting: {style.setting}")
        logger.info(f"Framing: {style.framing}")
        logger.info(f"Camera Angle: {style.camera_angle}")
        logger.info(f"Lighting: {style.lighting}")
        logger.info(f"Mood: {style.mood}")
        logger.info("\n" + "="*70)

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
