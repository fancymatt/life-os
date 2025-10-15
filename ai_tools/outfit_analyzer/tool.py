"""
Outfit Analyzer Tool

Analyzes images to extract detailed outfit information including:
- Clothing items with fabric, color, and construction details
- Style genre and formality level
- Overall aesthetic

Supports cache and preset workflows.
"""

from pathlib import Path
from typing import Optional, Union, List
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import OutfitSpec, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.cache import CacheManager
from ai_tools.shared.preset import PresetManager
from ai_tools.outfit_visualizer.tool import OutfitVisualizer


class OutfitAnalyzer:
    """
    Analyzes outfit images to extract structured outfit data

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
        cache_ttl: Optional[int] = None,
        auto_visualize: bool = True
    ):
        """
        Initialize the outfit analyzer

        Args:
            model: Model to use (default from config)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Cache TTL in seconds (default: 7 days)
            auto_visualize: Auto-generate preview images when saving presets (default: True)
        """
        # Get model from config if not specified
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("outfit_analyzer")

        self.router = LLMRouter(model=model)
        self.use_cache = use_cache
        self.cache_manager = CacheManager(default_ttl=cache_ttl) if cache_ttl else CacheManager()
        self.preset_manager = PresetManager()
        self.auto_visualize = auto_visualize
        self.visualizer = OutfitVisualizer() if auto_visualize else None

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
    ) -> OutfitSpec:
        """
        Analyze an outfit image

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name
            preset_notes: Optional notes for the preset

        Returns:
            OutfitSpec with analyzed outfit data
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Check cache first (unless skipped)
        if self.use_cache and not skip_cache:
            cached = self.cache_manager.get_for_file(
                "outfits",
                image_path,
                OutfitSpec
            )
            if cached:
                print(f"✅ Using cached analysis for {image_path.name}")
                # Save as preset if requested (even for cached results)
                if save_as_preset:
                    # If save_as_preset is True (boolean), use the AI-generated suggested_name
                    preset_name = cached.suggested_name if save_as_preset is True else save_as_preset

                    preset_path, preset_id = self.preset_manager.save(
                        "outfits",
                        cached,
                        display_name=preset_name,
                        notes=preset_notes
                    )
                    # Ensure metadata exists and update with preset info
                    if not cached._metadata:
                        cached._metadata = SpecMetadata(
                            tool="outfit-analyzer",
                            tool_version="1.0.0",
                            source_image=str(image_path),
                            source_hash=self.cache_manager.compute_file_hash(image_path),
                            model_used="cached"
                        )
                    cached._metadata.preset_id = preset_id
                    cached._metadata.display_name = preset_name
                    print(f"⭐ Saved as preset: {preset_name}")
                    print(f"   ID: {preset_id}")
                    print(f"   Location: {preset_path}")

                    # Generate preview visualization if enabled
                    if self.auto_visualize and self.visualizer:
                        try:
                            print(f"\n🎨 Generating preview visualization...")
                            viz_path = self.visualizer.visualize(
                                outfit=cached,
                                output_dir=preset_path.parent,
                                preset_id=preset_id
                            )
                            print(f"   Preview: {viz_path}")
                        except Exception as e:
                            print(f"⚠️  Preview generation failed: {e}")

                return cached

        # Perform analysis
        print(f"🔍 Analyzing outfit in {image_path.name}...")

        try:
            outfit = self.router.call_structured(
                prompt=self.prompt_template,
                response_model=OutfitSpec,
                images=[image_path],
                temperature=0.3
            )

            # Add metadata
            outfit._metadata = SpecMetadata(
                tool="outfit-analyzer",
                tool_version="1.0.0",
                source_image=str(image_path),
                source_hash=self.cache_manager.compute_file_hash(image_path),
                model_used=self.router.model
            )

            # Cache the result
            if self.use_cache:
                self.cache_manager.set_for_file(
                    "outfits",
                    image_path,
                    outfit
                )
                print(f"💾 Cached analysis")

            # Save as preset if requested
            if save_as_preset:
                # If save_as_preset is True (boolean), use the AI-generated suggested_name
                preset_name = outfit.suggested_name if save_as_preset is True else save_as_preset

                preset_path, preset_id = self.preset_manager.save(
                    "outfits",
                    outfit,
                    display_name=preset_name,
                    notes=preset_notes
                )
                # Update metadata with preset info
                if outfit._metadata:
                    outfit._metadata.preset_id = preset_id
                    outfit._metadata.display_name = preset_name
                print(f"⭐ Saved as preset: {preset_name}")
                print(f"   ID: {preset_id}")
                print(f"   Location: {preset_path}")

                # Generate preview visualization if enabled
                if self.auto_visualize and self.visualizer:
                    try:
                        print(f"\n🎨 Generating preview visualization...")
                        viz_path = self.visualizer.visualize(
                            outfit=outfit,
                            output_dir=preset_path.parent,
                            preset_id=preset_id
                        )
                        print(f"   Preview: {viz_path}")
                    except Exception as e:
                        print(f"⚠️  Preview generation failed: {e}")

            return outfit

        except Exception as e:
            raise Exception(f"Failed to analyze outfit: {e}")

    def analyze_from_preset(self, preset_id: str) -> OutfitSpec:
        """
        Load an outfit analysis from a preset

        Args:
            preset_id: UUID of the preset

        Returns:
            OutfitSpec from preset
        """
        return self.preset_manager.load("outfits", preset_id, OutfitSpec)

    def save_to_preset(
        self,
        outfit: OutfitSpec,
        display_name: str,
        notes: Optional[str] = None
    ) -> tuple[Path, str]:
        """
        Save an outfit analysis as a preset

        Args:
            outfit: OutfitSpec to save
            display_name: Display name for the preset
            notes: Optional notes

        Returns:
            Tuple of (Path to saved preset, preset_id)
        """
        return self.preset_manager.save("outfits", outfit, display_name=display_name, notes=notes)

    def list_presets(self) -> List[str]:
        """List all outfit presets"""
        return self.preset_manager.list("outfits")

    def get_cache_stats(self):
        """Get cache statistics"""
        return self.cache_manager.stats()


def main():
    """CLI interface for outfit analyzer"""
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Analyze outfit in an image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze an image
  python tool.py image.jpg

  # Analyze and save as preset
  python tool.py image.jpg --save-as fancy-suit --notes "Professional suit"

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
        help='List all outfit presets'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    args = parser.parse_args()

    analyzer = OutfitAnalyzer(model=args.model)

    # List presets
    if args.list:
        presets = analyzer.list_presets()
        print(f"\n📋 Outfit Presets ({len(presets)}):")
        for preset in presets:
            display_name = preset.get("display_name") or preset["preset_id"][:8]
            print(f"  - {display_name} (ID: {preset['preset_id'][:8]}...)")
        return

    # Analyze image
    if not args.image:
        parser.error("Image path required (or use --list)")

    try:
        outfit = analyzer.analyze(
            args.image,
            skip_cache=args.no_cache,
            save_as_preset=args.save_as,
            preset_notes=args.notes
        )

        # Print results
        print("\n" + "="*70)
        print("Outfit Analysis")
        print("="*70)
        print(f"\nStyle Genre: {outfit.style_genre}")
        print(f"Formality: {outfit.formality}")
        print(f"Aesthetic: {outfit.aesthetic}")

        print(f"\nClothing Items ({len(outfit.clothing_items)}):")
        for i, item in enumerate(outfit.clothing_items, 1):
            print(f"\n  {i}. {item.item}")
            print(f"     Fabric: {item.fabric}")
            print(f"     Color: {item.color}")
            print(f"     Details: {item.details[:100]}{'...' if len(item.details) > 100 else ''}")

        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
