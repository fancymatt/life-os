#!/usr/bin/env python3
"""
Startup script to generate missing preview images in the background
Runs when the container starts
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.preset_service import PresetService
from api.logging_config import (
    log_background_task_start,
    log_background_task_success,
    log_background_task_error
)

def main():
    """Generate missing previews on startup"""
    service = PresetService()

    print("🎨 Checking for missing preview images...")

    total_missing = 0
    total_generated = 0
    total_failed = 0

    for category in service.CATEGORIES:
        try:
            presets = service.list_presets(category)

            if not presets:
                continue

            for preset in presets:
                preset_id = preset.get("preset_id")

                # Check if preview exists
                if not service.preset_manager.has_preview_image(category, preset_id):
                    total_missing += 1
                    display_name = preset.get("display_name", preset_id)

                    try:
                        # Load preset data
                        preset_data = service.get_preset(category, preset_id)

                        # Remove metadata before generating preview
                        if "_metadata" in preset_data:
                            del preset_data["_metadata"]

                        # Generate preview
                        print(f"   🖼️  Generating missing preview: {category}/{display_name}")
                        service._generate_preview(category, preset_id, preset_data)
                        total_generated += 1

                    except Exception as e:
                        print(f"   ⚠️  Failed to generate preview for {display_name}: {e}")
                        total_failed += 1

        except Exception as e:
            print(f"   ❌ Error processing category {category}: {e}")

    if total_missing == 0:
        print("✅ All presets have preview images")
    else:
        print(f"\n📊 Generated {total_generated} missing preview(s)")
        if total_failed > 0:
            print(f"⚠️  {total_failed} preview(s) failed to generate")

if __name__ == "__main__":
    main()
