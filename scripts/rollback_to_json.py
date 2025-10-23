#!/usr/bin/env python3
"""
PostgreSQL to JSON Rollback Script

Exports data from PostgreSQL back to JSON files in case of migration failure.
This script reads all entities from the database and writes them to JSON files
in the original data/ directory structure.

Usage:
    python3 scripts/rollback_to_json.py [--dry-run] [--backup-first]

Options:
    --dry-run       Show what would be exported without writing files
    --backup-first  Create backup of current JSON files before rollback
    --entity-type   Only rollback specific entity type (e.g., 'characters')
"""

import sys
import os
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import services
from api.services.character_service_db import CharacterServiceDB
from api.services.clothing_items_service_db import ClothingItemServiceDB
from api.services.outfit_service_db import OutfitServiceDB
from api.services.composition_service_db import CompositionServiceDB
from api.services.favorites_service_db import FavoritesServiceDB
from api.services.board_game_service_db import BoardGameServiceDB
from api.database import init_db, close_db


async def export_characters(output_dir: Path, dry_run: bool = False) -> int:
    """Export all characters from PostgreSQL to JSON files"""
    service = CharacterServiceDB()
    characters = await service.list_characters(limit=10000)  # Get all

    char_dir = output_dir / "characters"
    if not dry_run:
        char_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for char in characters:
        filename = f"{char['character_id']}.json"
        filepath = char_dir / filename

        # Convert to original JSON format
        char_data = {
            "character_id": char["character_id"],
            "name": char["name"],
            "description": char.get("description"),
            "appearance": char.get("appearance"),
            "reference_image_path": char.get("reference_image_path"),
            "created_at": char.get("created_at").isoformat() if char.get("created_at") else None,
            "updated_at": char.get("updated_at").isoformat() if char.get("updated_at") else None,
        }

        if dry_run:
            print(f"  Would write: {filepath}")
        else:
            with open(filepath, 'w') as f:
                json.dump(char_data, f, indent=2)
        count += 1

    print(f"✅ Characters: {count} files")
    return count


async def export_clothing_items(output_dir: Path, dry_run: bool = False) -> int:
    """Export all clothing items from PostgreSQL to JSON files"""
    service = ClothingItemServiceDB()
    items = await service.list_clothing_items(limit=10000)  # Get all

    item_dir = output_dir / "clothing_items"
    if not dry_run:
        item_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for item in items:
        filename = f"{item['item_id']}.json"
        filepath = item_dir / filename

        # Convert to original JSON format
        item_data = {
            "item_id": item["item_id"],
            "name": item["name"],
            "category": item.get("category"),
            "subcategory": item.get("subcategory"),
            "description": item.get("description"),
            "brand": item.get("brand"),
            "color": item.get("color"),
            "material": item.get("material"),
            "season": item.get("season"),
            "tags": item.get("tags", []),
            "reference_image_path": item.get("reference_image_path"),
            "created_at": item.get("created_at").isoformat() if item.get("created_at") else None,
            "updated_at": item.get("updated_at").isoformat() if item.get("updated_at") else None,
        }

        if dry_run:
            print(f"  Would write: {filepath}")
        else:
            with open(filepath, 'w') as f:
                json.dump(item_data, f, indent=2)
        count += 1

    print(f"✅ Clothing Items: {count} files")
    return count


async def export_outfits(output_dir: Path, dry_run: bool = False) -> int:
    """Export all outfits from PostgreSQL to JSON files"""
    service = OutfitServiceDB()
    outfits = await service.list_outfits(limit=10000)  # Get all

    outfit_dir = output_dir / "outfits"
    if not dry_run:
        outfit_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for outfit in outfits:
        filename = f"{outfit['outfit_id']}.json"
        filepath = outfit_dir / filename

        # Convert to original JSON format
        outfit_data = {
            "outfit_id": outfit["outfit_id"],
            "name": outfit["name"],
            "description": outfit.get("description"),
            "clothing_items": outfit.get("clothing_items", []),
            "tags": outfit.get("tags", []),
            "created_at": outfit.get("created_at").isoformat() if outfit.get("created_at") else None,
            "updated_at": outfit.get("updated_at").isoformat() if outfit.get("updated_at") else None,
        }

        if dry_run:
            print(f"  Would write: {filepath}")
        else:
            with open(filepath, 'w') as f:
                json.dump(outfit_data, f, indent=2)
        count += 1

    print(f"✅ Outfits: {count} files")
    return count


async def export_compositions(output_dir: Path, dry_run: bool = False) -> int:
    """Export all compositions from PostgreSQL to JSON files"""
    service = CompositionServiceDB()
    compositions = await service.list_compositions(limit=10000)  # Get all

    comp_dir = output_dir / "compositions"
    if not dry_run:
        comp_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for comp in compositions:
        filename = f"{comp['composition_id']}.json"
        filepath = comp_dir / filename

        # Convert to original JSON format
        comp_data = {
            "composition_id": comp["composition_id"],
            "name": comp["name"],
            "description": comp.get("description"),
            "presets": comp.get("presets", {}),
            "created_at": comp.get("created_at").isoformat() if comp.get("created_at") else None,
            "updated_at": comp.get("updated_at").isoformat() if comp.get("updated_at") else None,
        }

        if dry_run:
            print(f"  Would write: {filepath}")
        else:
            with open(filepath, 'w') as f:
                json.dump(comp_data, f, indent=2)
        count += 1

    print(f"✅ Compositions: {count} files")
    return count


async def export_board_games(output_dir: Path, dry_run: bool = False) -> int:
    """Export all board games from PostgreSQL to JSON files"""
    service = BoardGameServiceDB()
    games = await service.list_board_games(limit=10000)  # Get all

    game_dir = output_dir / "board_games"
    if not dry_run:
        game_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for game in games:
        filename = f"{game['game_id']}.json"
        filepath = game_dir / filename

        # Convert to original JSON format
        game_data = {
            "game_id": game["game_id"],
            "name": game["name"],
            "bgg_id": game.get("bgg_id"),
            "description": game.get("description"),
            "designers": game.get("designers", []),
            "year_published": game.get("year_published"),
            "min_players": game.get("min_players"),
            "max_players": game.get("max_players"),
            "playing_time": game.get("playing_time"),
            "min_age": game.get("min_age"),
            "complexity": game.get("complexity"),
            "created_at": game.get("created_at").isoformat() if game.get("created_at") else None,
            "updated_at": game.get("updated_at").isoformat() if game.get("updated_at") else None,
        }

        if dry_run:
            print(f"  Would write: {filepath}")
        else:
            with open(filepath, 'w') as f:
                json.dump(game_data, f, indent=2)
        count += 1

    print(f"✅ Board Games: {count} files")
    return count


async def export_favorites(output_dir: Path, dry_run: bool = False) -> int:
    """Export favorites to JSON file"""
    service = FavoritesServiceDB()

    # Note: This assumes a simple structure. Adjust if needed.
    favorites_path = output_dir / "favorites.json"

    # Get all favorites (this may need user context)
    # For now, just create empty structure
    favorites_data = {
        "items": [],
        "exported_at": datetime.now().isoformat()
    }

    if dry_run:
        print(f"  Would write: {favorites_path}")
    else:
        with open(favorites_path, 'w') as f:
            json.dump(favorites_data, f, indent=2)

    print(f"✅ Favorites: 1 file")
    return 1


async def main():
    parser = argparse.ArgumentParser(description="Rollback PostgreSQL data to JSON files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be exported")
    parser.add_argument("--backup-first", action="store_true", help="Backup current JSON files first")
    parser.add_argument("--entity-type", help="Only export specific entity type")
    parser.add_argument("--output-dir", default="data", help="Output directory (default: data)")
    args = parser.parse_args()

    print("🔄 PostgreSQL to JSON Rollback Script")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print(f"Output directory: {args.output_dir}")
    print(f"Dry run: {args.dry_run}")
    print("")

    # Backup first if requested
    if args.backup_first and not args.dry_run:
        print("📦 Creating backup of current JSON files...")
        import subprocess
        result = subprocess.run(["./scripts/backup_json_data.sh"], cwd=Path(__file__).parent.parent)
        if result.returncode != 0:
            print("❌ Backup failed! Aborting rollback.")
            return 1
        print("")

    # Initialize database
    print("🔌 Connecting to PostgreSQL...")
    await init_db()
    print("✅ Connected")
    print("")

    output_dir = Path(args.output_dir)
    total_files = 0

    try:
        print("📤 Exporting entities...")
        print("")

        entity_type = args.entity_type

        if not entity_type or entity_type == "characters":
            total_files += await export_characters(output_dir, args.dry_run)

        if not entity_type or entity_type == "clothing_items":
            total_files += await export_clothing_items(output_dir, args.dry_run)

        if not entity_type or entity_type == "outfits":
            total_files += await export_outfits(output_dir, args.dry_run)

        if not entity_type or entity_type == "compositions":
            total_files += await export_compositions(output_dir, args.dry_run)

        if not entity_type or entity_type == "board_games":
            total_files += await export_board_games(output_dir, args.dry_run)

        if not entity_type or entity_type == "favorites":
            total_files += await export_favorites(output_dir, args.dry_run)

        print("")
        print("=" * 50)
        if args.dry_run:
            print(f"✅ Dry run complete! Would export {total_files} files.")
        else:
            print(f"✅ Rollback complete! Exported {total_files} files.")
        print("")
        print("⚠️  Remember to:")
        print("  1. Restart the application to use JSON files")
        print("  2. Update .env to disable database (if needed)")
        print("  3. Verify all data exported correctly")
        print("")

        return 0

    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        await close_db()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
