#!/usr/bin/env python3
"""
Outfit Analyzer Workflow Example

Demonstrates the complete workflow:
1. Analyze an image (caches automatically)
2. Cache hit on second analysis
3. Promote result to preset
4. Load from preset
5. Edit preset manually
6. Reuse edited preset

Usage:
    python test_outfit_analyzer.py path/to/outfit-image.jpg
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
from dotenv import load_dotenv

load_dotenv()


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_outfit_analyzer.py path/to/image.jpg")
        print("\nThis script demonstrates the complete outfit-analyzer workflow:")
        print("  1. First analysis (calls API, caches result)")
        print("  2. Second analysis (cache hit)")
        print("  3. Promote to preset")
        print("  4. Load from preset")
        print("  5. Manual editing workflow")
        sys.exit(1)

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        print(f"❌ Error: Image not found: {image_path}")
        sys.exit(1)

    print("=" * 70)
    print("Outfit Analyzer Workflow Demo")
    print("=" * 70)

    # Initialize analyzer
    analyzer = OutfitAnalyzer()

    # Step 1: First analysis (will call API and cache)
    print("\n📍 STEP 1: First Analysis (API call)")
    print("-" * 70)
    outfit = analyzer.analyze(image_path)

    print(f"\n✅ Analysis complete!")
    print(f"   Style Genre: {outfit.style_genre}")
    print(f"   Formality: {outfit.formality}")
    print(f"   Items: {len(outfit.clothing_items)}")
    for item in outfit.clothing_items[:3]:  # Show first 3
        print(f"     - {item.item} ({item.color})")
    if len(outfit.clothing_items) > 3:
        print(f"     ... and {len(outfit.clothing_items) - 3} more")

    # Step 2: Second analysis (should hit cache)
    print("\n📍 STEP 2: Second Analysis (Cache Hit)")
    print("-" * 70)
    outfit2 = analyzer.analyze(image_path)
    print("   (Should see 'Using cached analysis' message above)")

    # Step 3: Promote to preset
    print("\n📍 STEP 3: Promote to Preset")
    print("-" * 70)
    preset_name = "example-outfit"
    preset_path = analyzer.save_to_preset(
        outfit,
        preset_name,
        notes="Example outfit from workflow demo"
    )
    print(f"✅ Saved as preset: {preset_name}")
    print(f"   Location: {preset_path}")

    # Step 4: Load from preset
    print("\n📍 STEP 4: Load from Preset")
    print("-" * 70)
    loaded_outfit = analyzer.analyze_from_preset(preset_name)
    print(f"✅ Loaded preset: {preset_name}")
    print(f"   Style: {loaded_outfit.style_genre}")
    print(f"   Items: {len(loaded_outfit.clothing_items)}")

    # Step 5: Manual editing workflow
    print("\n📍 STEP 5: Manual Editing Workflow")
    print("-" * 70)
    print(f"\nThe preset is now saved at:")
    print(f"  {preset_path}")
    print(f"\nYou can manually edit this JSON file to refine:")
    print(f"  - Clothing item descriptions")
    print(f"  - Fabric details")
    print(f"  - Color descriptions")
    print(f"  - Style genre and aesthetic")
    print(f"\nAfter editing, reload with:")
    print(f'  outfit = analyzer.analyze_from_preset("{preset_name}")')

    # Step 6: List all presets
    print("\n📍 STEP 6: All Outfit Presets")
    print("-" * 70)
    presets = analyzer.list_presets()
    if presets:
        print(f"Found {len(presets)} preset(s):")
        for p in presets:
            print(f"  - {p}")
    else:
        print("No presets found")

    # Cache stats
    print("\n📍 Cache Statistics")
    print("-" * 70)
    stats = analyzer.get_cache_stats()
    print(f"Total cached entries: {stats.total_entries}")
    print(f"Total size: {stats.total_size_bytes / 1024 / 1024:.2f} MB")
    print(f"Entries by type: {stats.entries_by_type}")
    if stats.oldest_entry:
        print(f"Oldest entry: {stats.oldest_entry}")
    if stats.newest_entry:
        print(f"Newest entry: {stats.newest_entry}")

    print("\n" + "=" * 70)
    print("✅ Workflow Demo Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print(f"  1. Edit the preset at: {preset_path}")
    print(f"  2. Reload it: analyzer.analyze_from_preset('{preset_name}')")
    print(f"  3. Use it in image generation workflows")


if __name__ == "__main__":
    main()
