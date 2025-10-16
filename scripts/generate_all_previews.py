#!/usr/bin/env python3
"""
Generate preview images for all presets that don't have one
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.preset_service import PresetService


def main():
    """Generate all missing previews"""
    service = PresetService()

    print("🎨 Generating missing preview images...\n")

    total_generated = 0
    total_skipped = 0
    total_failed = 0

    for category in service.CATEGORIES:
        print(f"\n📂 Processing {category}...")
        presets = service.list_presets(category)

        for preset in presets:
            preset_id = preset['preset_id']
            display_name = preset.get('display_name', preset_id)

            # Check if preview already exists
            has_preview = service.preset_manager.has_preview_image(category, preset_id)

            if has_preview:
                print(f"  ⏭️  Skipping {display_name} (preview exists)")
                total_skipped += 1
                continue

            # Load preset data
            try:
                data = service.get_preset(category, preset_id)

                # Generate preview
                print(f"  🎨 Generating preview for {display_name}...")
                service._generate_preview(category, preset_id, data)
                total_generated += 1

            except Exception as e:
                print(f"  ❌ Failed to generate preview for {display_name}: {e}")
                total_failed += 1

    print(f"\n" + "="*60)
    print(f"✅ Generated: {total_generated}")
    print(f"⏭️  Skipped (already exist): {total_skipped}")
    print(f"❌ Failed: {total_failed}")
    print(f"📊 Total presets: {total_generated + total_skipped + total_failed}")
    print("="*60)


if __name__ == "__main__":
    main()
