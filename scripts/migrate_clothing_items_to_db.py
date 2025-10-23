#!/usr/bin/env python3
"""
Migrate clothing items from JSON files to PostgreSQL database

This script reads all clothing item JSON files from data/clothing_items/
and imports them into the PostgreSQL database.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import get_session
from api.services.clothing_items_service_db import ClothingItemServiceDB


async def migrate_clothing_items():
    """Migrate all JSON clothing items to database"""

    # Path to JSON files (absolute path in container)
    json_dir = Path("/app/data/clothing_items")

    if not json_dir.exists():
        print(f"❌ Directory not found: {json_dir}")
        return

    # Find all JSON files (exclude preview images)
    json_files = list(json_dir.glob("*.json"))

    if not json_files:
        print("❌ No JSON files found")
        return

    print(f"\n📦 Found {len(json_files)} JSON files")
    print(f"📂 Source: {json_dir}")
    print()

    # Create database session
    async with get_session() as session:
        service = ClothingItemServiceDB(session, user_id=None)

        migrated = 0
        skipped = 0
        errors = []

        for json_file in json_files:
            try:
                # Load JSON
                with open(json_file, 'r') as f:
                    data = json.load(f)

                # Check if already exists by item_id
                item_id = data.get('item_id')
                if item_id:
                    existing = await service.get_clothing_item(item_id)
                    if existing:
                        print(f"⏩ Skipped (already exists): {data.get('item', 'unknown')} ({item_id[:8]}...)")
                        skipped += 1
                        continue

                # Extract fields
                category = data.get('category', 'tops')
                item = data.get('item', 'Unknown item')
                fabric = data.get('fabric', 'Unknown fabric')
                color = data.get('color', 'Unknown color')
                details = data.get('details', '')
                source_image = data.get('source_image')

                # Create in database
                created = await service.create_clothing_item(
                    category=category,
                    item=item,
                    fabric=fabric,
                    color=color,
                    details=details,
                    source_image=source_image,
                    generate_preview=False  # Don't generate previews during migration
                )

                print(f"✅ Migrated: {item} ({category}) - ID: {created['item_id'][:8]}...")
                migrated += 1

            except Exception as e:
                error_msg = f"Error processing {json_file.name}: {e}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)

        # Commit all changes
        await session.commit()

        print()
        print("="*70)
        print("Migration Summary")
        print("="*70)
        print(f"✅ Migrated: {migrated}")
        print(f"⏩ Skipped (duplicates): {skipped}")
        print(f"❌ Errors: {len(errors)}")
        print(f"📊 Total: {len(json_files)}")
        print()

        if errors:
            print("Errors encountered:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")

        print()
        print(f"💾 All items saved to PostgreSQL database")
        print()


if __name__ == "__main__":
    asyncio.run(migrate_clothing_items())
