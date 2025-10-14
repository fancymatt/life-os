#!/usr/bin/env python3
"""
Quick validation of outfit-analyzer setup (no API calls)

Checks:
- Module imports work
- Directory structure exists
- Template loads correctly
- Analyzer initializes
- Config integration works
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def validate():
    print("=" * 70)
    print("Outfit Analyzer Validation")
    print("=" * 70)

    # Test 1: Import modules
    print("\n✓ Test 1: Module imports")
    try:
        from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
        from ai_capabilities.specs import OutfitSpec, ClothingItem
        from ai_tools.shared.router import LLMRouter, RouterConfig
        from ai_tools.shared.cache import CacheManager
        from ai_tools.shared.preset import PresetManager
        print("  ✅ All modules imported successfully")
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

    # Test 2: Directory structure
    print("\n✓ Test 2: Directory structure")
    base = Path(__file__).parent.parent
    required_dirs = [
        base / "ai_tools" / "outfit_analyzer",
        base / "presets",
        base / "cache",
        base / "configs"
    ]
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"  ✅ {dir_path.relative_to(base)}")
        else:
            print(f"  ❌ Missing: {dir_path.relative_to(base)}")
            return False

    # Test 3: Template file
    print("\n✓ Test 3: Template file")
    template_path = base / "ai_tools" / "outfit_analyzer" / "template.md"
    if template_path.exists():
        content = template_path.read_text()
        print(f"  ✅ Template loaded ({len(content)} chars)")
        if "clothing_items" in content and "style_genre" in content:
            print(f"  ✅ Template structure valid")
        else:
            print(f"  ❌ Template missing required fields")
            return False
    else:
        print(f"  ❌ Template not found")
        return False

    # Test 4: Analyzer initialization
    print("\n✓ Test 4: Analyzer initialization")
    try:
        analyzer = OutfitAnalyzer()
        print(f"  ✅ OutfitAnalyzer initialized")
        print(f"     Model: {analyzer.router.model}")
        print(f"     Cache enabled: {analyzer.use_cache}")
        print(f"     Template path: {analyzer.template_path.name}")
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        return False

    # Test 5: Config integration
    print("\n✓ Test 5: Config integration")
    try:
        config = RouterConfig()
        model = config.get_model_for_tool("outfit_analyzer")
        print(f"  ✅ Config loaded")
        print(f"     Default model: {model}")
    except Exception as e:
        print(f"  ⚠️  Config issue (non-fatal): {e}")

    # Test 6: Pydantic models
    print("\n✓ Test 6: Pydantic models")
    try:
        item = ClothingItem(
            item="test jacket",
            fabric="wool",
            color="navy",
            details="test details"
        )
        outfit = OutfitSpec(
            clothing_items=[item],
            style_genre="test",
            formality="casual",
            aesthetic="test"
        )
        print(f"  ✅ ClothingItem created")
        print(f"  ✅ OutfitSpec created with {len(outfit.clothing_items)} item(s)")
    except Exception as e:
        print(f"  ❌ Model creation failed: {e}")
        return False

    # Test 7: Cache and preset directories
    print("\n✓ Test 7: Storage setup")
    cache_dir = base / "cache" / "outfits"
    preset_dir = base / "presets" / "outfits"

    cache_dir.mkdir(parents=True, exist_ok=True)
    preset_dir.mkdir(parents=True, exist_ok=True)

    print(f"  ✅ Cache directory: {cache_dir.relative_to(base)}")
    print(f"  ✅ Preset directory: {preset_dir.relative_to(base)}")

    print("\n" + "=" * 70)
    print("✅ All validation checks passed!")
    print("=" * 70)
    print("\nOutfit-analyzer is ready to use.")
    print("\nNext steps:")
    print("  1. Test with real image: python examples/test_outfit_analyzer.py image.jpg")
    print("  2. CLI usage: python ai_tools/outfit_analyzer/tool.py image.jpg")
    print("  3. See README: ai_tools/outfit_analyzer/README.md")

    return True

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
