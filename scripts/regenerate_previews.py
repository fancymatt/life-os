#!/usr/bin/env python3
"""
Regenerate preview images for all existing presets
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.preset_service import PresetService

def main():
    """Regenerate previews for all presets"""
    service = PresetService()

    print("🎨 Regenerating preview images for all presets...")
    print()

    total_generated = 0
    total_failed = 0

    for category in service.CATEGORIES:
        print(f"📁 Processing category: {category}")

        try:
            presets = service.list_presets(category)

            if not presets:
                print(f"   ⚠️  No presets found in {category}")
                continue

            print(f"   Found {len(presets)} preset(s)")

            for preset in presets:
                preset_id = preset.get("preset_id")
                display_name = preset.get("display_name", preset_id)

                try:
                    # Load preset data
                    preset_data = service.get_preset(category, preset_id)

                    # Remove metadata before generating preview
                    if "_metadata" in preset_data:
                        del preset_data["_metadata"]

                    # Generate preview
                    print(f"   🖼️  Generating preview for: {display_name}")
                    service._generate_preview(category, preset_id, preset_data)
                    total_generated += 1

                except Exception as e:
                    print(f"   ❌ Failed to generate preview for {display_name}: {e}")
                    total_failed += 1

        except Exception as e:
            print(f"   ❌ Error processing category {category}: {e}")

        print()

    print("=" * 60)
    print(f"✅ Successfully generated: {total_generated} preview(s)")
    if total_failed > 0:
        print(f"❌ Failed: {total_failed} preview(s)")
    print("=" * 60)

if __name__ == "__main__":
    main()
