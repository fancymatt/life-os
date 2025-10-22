"""
Outfit Analyzer Tool

Analyzes images to extract detailed outfit information including:
- Clothing items with fabric, color, and construction details
- Style genre and formality level
- Overall aesthetic

Supports cache and preset workflows.
"""

from pathlib import Path
from typing import Optional, Union, List, Dict, Any
import sys
import asyncio
import uuid
import json
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import (
    OutfitSpec,
    SpecMetadata,
    OutfitAnalysisResult,
    ClothingItemEntity,
    ClothingCategory
)
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.cache import CacheManager
from ai_tools.shared.preset import PresetManager
from ai_tools.outfit_visualizer.tool import OutfitVisualizer
from api.config import settings


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

    def _load_template(self) -> str:
        """
        Load template with override support.

        Checks for custom template first, then falls back to base template.
        """
        # Check for custom template override
        custom_template_path = settings.base_dir / "data" / "tool_configs" / "outfit_analyzer_template.md"
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
    ) -> Dict[str, Any]:
        """
        Analyze an outfit image and save individual clothing items (async version)

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: DEPRECATED - no longer used with new architecture
            preset_notes: DEPRECATED - no longer used with new architecture

        Returns:
            Dict with keys:
                - clothing_items: List of ClothingItemEntity dicts
                - suggested_outfit_name: Suggested name for this outfit
                - item_count: Number of items created
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load template first (needed for cache key)
        prompt_template = self._load_template()

        # Compute cache key that includes image, template, AND model
        import hashlib
        image_hash = self.cache_manager.compute_file_hash(image_path)
        template_hash = hashlib.sha256(prompt_template.encode('utf-8')).hexdigest()[:16]
        model_hash = hashlib.sha256(self.router.model.encode('utf-8')).hexdigest()[:8]
        combined_key = f"{image_hash}_{template_hash}_{model_hash}"

        print(f"🔍 Cache key computation:")
        print(f"   Image hash: {image_hash}")
        print(f"   Template hash: {template_hash} (from {len(prompt_template)} chars)")
        print(f"   Model: {self.router.model} (hash: {model_hash})")
        print(f"   Combined key: {combined_key}")

        # Check cache first (unless skipped)
        # NOTE: Cache lookup disabled for new architecture - old OutfitSpec cache is incompatible
        # New runs will cache OutfitAnalysisResult, but we always analyze fresh for now
        if self.use_cache and not skip_cache:
            # Try to get cached analysis result
            try:
                cached = self.cache_manager.get(
                    "outfits",
                    combined_key,
                    OutfitAnalysisResult
                )
                if cached:
                    print(f"✅ CACHE HIT - Processing cached analysis for {image_path.name}")
                    # Process cached result into clothing items (same as fresh analysis)
                    clothing_items_dir = settings.base_dir / "data" / "clothing_items"
                    clothing_items_dir.mkdir(parents=True, exist_ok=True)

                    created_items = []
                    for item_data in cached.clothing_items:
                        item_id = str(uuid.uuid4())
                        item_entity = ClothingItemEntity(
                            item_id=item_id,
                            category=ClothingCategory(item_data["category"]),
                            item=item_data["item"],
                            fabric=item_data["fabric"],
                            color=item_data["color"],
                            details=item_data["details"],
                            source_image=str(image_path),
                            created_at=datetime.now()
                        )
                        item_path = clothing_items_dir / f"{item_id}.json"
                        item_path.write_text(json.dumps(item_entity.dict(), indent=2, default=str))
                        created_items.append(item_entity)
                        print(f"   ✅ Saved {item_entity.category.value}: {item_entity.item}")

                    print(f"\n✨ Created {len(created_items)} clothing items from cache")
                    return {
                        "clothing_items": [item.dict() for item in created_items],
                        "suggested_outfit_name": cached.suggested_outfit_name,
                        "item_count": len(created_items)
                    }
            except Exception as e:
                # Cache miss or incompatible cache format - analyze fresh
                print(f"❌ CACHE MISS - Will analyze fresh ({e})")
        else:
            if skip_cache:
                print(f"⏩ CACHE SKIPPED - Will analyze fresh")

        # Perform analysis
        print(f"🔍 Analyzing outfit in {image_path.name}...")

        # GPT-5 models only support temperature=1, use 0.3 for all others
        temperature = 1.0 if "gpt-5" in self.router.model.lower() else 0.3

        try:
            # Call LLM to analyze image and extract clothing items
            analysis = await self.router.acall_structured(
                prompt=prompt_template,
                response_model=OutfitAnalysisResult,
                images=[image_path],
                temperature=temperature
            )

            # Create clothing_items directory if it doesn't exist
            clothing_items_dir = settings.base_dir / "data" / "clothing_items"
            clothing_items_dir.mkdir(parents=True, exist_ok=True)

            # Create and save individual ClothingItemEntity objects
            created_items = []
            for item_data in analysis.clothing_items:
                # Generate unique ID
                item_id = str(uuid.uuid4())

                # Create ClothingItemEntity
                item_entity = ClothingItemEntity(
                    item_id=item_id,
                    category=ClothingCategory(item_data["category"]),
                    item=item_data["item"],
                    fabric=item_data["fabric"],
                    color=item_data["color"],
                    details=item_data["details"],
                    source_image=str(image_path),
                    created_at=datetime.now()
                )

                # Save to file
                item_path = clothing_items_dir / f"{item_id}.json"
                item_path.write_text(json.dumps(item_entity.dict(), indent=2, default=str))

                created_items.append(item_entity)
                print(f"   ✅ Saved {item_entity.category.value}: {item_entity.item}")

            # Cache the result using combined key (image + template + model)
            if self.use_cache:
                self.cache_manager.set(
                    "outfits",
                    combined_key,
                    analysis,
                    source_file=image_path
                )
                print(f"💾 Cached analysis (key: {combined_key[:16]}...)")

            print(f"\n✨ Created {len(created_items)} clothing items")

            # Return the created items with suggested name
            return {
                "clothing_items": [item.dict() for item in created_items],
                "suggested_outfit_name": analysis.suggested_outfit_name,
                "item_count": len(created_items)
            }

        except Exception as e:
            raise Exception(f"Failed to analyze outfit: {e}")

    def analyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_as_preset: Optional[str] = None,
        preset_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an outfit image and save individual clothing items (synchronous wrapper)

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: DEPRECATED - no longer used with new architecture
            preset_notes: DEPRECATED - no longer used with new architecture

        Returns:
            Dict with keys:
                - clothing_items: List of ClothingItemEntity dicts
                - suggested_outfit_name: Suggested name for this outfit
                - item_count: Number of items created
        """
        return asyncio.run(self.aanalyze(
            image_path=image_path,
            skip_cache=skip_cache,
            save_as_preset=save_as_preset,
            preset_notes=preset_notes
        ))

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
        result = analyzer.analyze(
            args.image,
            skip_cache=args.no_cache,
            save_as_preset=args.save_as,
            preset_notes=args.notes
        )

        # Print results
        print("\n" + "="*70)
        print("Outfit Analysis - Individual Clothing Items")
        print("="*70)
        if result.get("suggested_outfit_name"):
            print(f"\nSuggested Name: {result['suggested_outfit_name']}")

        print(f"\nClothing Items ({result['item_count']}):")
        for i, item in enumerate(result['clothing_items'], 1):
            print(f"\n  {i}. {item['item']} ({item['category']})")
            print(f"     Fabric: {item['fabric']}")
            print(f"     Color: {item['color']}")
            print(f"     Details: {item['details'][:100]}{'...' if len(item['details']) > 100 else ''}")
            print(f"     ID: {item['item_id']}")

        print("\n" + "="*70)
        print(f"\n💾 Saved {result['item_count']} items to data/clothing_items/")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
