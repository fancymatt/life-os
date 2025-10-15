#!/usr/bin/env python3
"""
Fix corrupted preset display_name values

Finds presets with boolean display_name and replaces with suggested_name
"""

import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def fix_preset_file(preset_path: Path) -> bool:
    """
    Fix a single preset file if it has invalid display_name

    Returns True if fixed, False if no fix needed
    """
    try:
        with open(preset_path, 'r') as f:
            data = json.load(f)

        # Check if _metadata.display_name is not a string
        if '_metadata' in data and 'display_name' in data['_metadata']:
            display_name = data['_metadata']['display_name']

            # If display_name is boolean or None, replace with suggested_name
            if not isinstance(display_name, str):
                suggested_name = data.get('suggested_name', 'Unnamed Preset')
                data['_metadata']['display_name'] = suggested_name

                # Write back
                with open(preset_path, 'w') as f:
                    json.dump(data, f, indent=2)

                print(f"✅ Fixed: {preset_path.name} → '{suggested_name}'")
                return True

        return False

    except Exception as e:
        print(f"⚠️  Error processing {preset_path}: {e}")
        return False


def main():
    """Fix all corrupted presets"""
    project_root = Path(__file__).parent.parent
    presets_dir = project_root / "presets"

    print("🔍 Scanning for corrupted presets...\n")

    # Categories to check
    categories = [
        "outfits", "visual_styles", "art_styles", "hair_styles",
        "hair_colors", "makeup", "expressions", "accessories"
    ]

    fixed_count = 0
    total_count = 0

    for category in categories:
        category_dir = presets_dir / category
        if not category_dir.exists():
            continue

        print(f"📁 Checking {category}...")

        for preset_file in category_dir.glob("*.json"):
            total_count += 1
            if fix_preset_file(preset_file):
                fixed_count += 1

    print(f"\n{'='*60}")
    print(f"✅ Fixed {fixed_count} out of {total_count} presets")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
