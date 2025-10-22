#!/usr/bin/env python3
"""
JSON to PostgreSQL Import Script

Migrates existing JSON file data to PostgreSQL database.
Imports users, characters, clothing items, and board games.

Usage:
    python scripts/import_json_to_postgres.py [--dry-run] [--entity=characters]
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import argparse

# Add parent directory to path to import from api
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from api.database import get_session, Base, get_engine
from api.models.db import User, Character, ClothingItem, BoardGame
from api.logging_config import get_logger

logger = get_logger(__name__)


class DataImporter:
    """Handles importing JSON data to PostgreSQL"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'users': {'imported': 0, 'skipped': 0, 'errors': 0},
            'characters': {'imported': 0, 'skipped': 0, 'errors': 0},
            'clothing_items': {'imported': 0, 'skipped': 0, 'errors': 0},
            'board_games': {'imported': 0, 'skipped': 0, 'errors': 0}
        }

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string, handling multiple formats"""
        if not dt_str:
            return None

        # Try common formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # 2025-10-22T18:04:31.012095
            "%Y-%m-%d %H:%M:%S.%f",  # 2025-10-22 18:04:31.012095
            "%Y-%m-%dT%H:%M:%S",     # 2025-10-22T18:04:31
            "%Y-%m-%d %H:%M:%S",     # 2025-10-22 18:04:31
        ]

        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse datetime: {dt_str}")
        return datetime.utcnow()

    async def import_users(self, data_dir: Path):
        """Import users from users.json"""
        users_file = data_dir / "users.json"

        if not users_file.exists():
            logger.warning(f"Users file not found: {users_file}")
            return

        logger.info(f"Importing users from {users_file}")

        with open(users_file, 'r') as f:
            users_data = json.load(f)

        async with get_session() as session:
            for username, user_data in users_data.items():
                try:
                    # Check if user already exists
                    result = await session.execute(
                        select(User).where(User.username == username)
                    )
                    existing_user = result.scalar_one_or_none()

                    if existing_user:
                        logger.info(f"User '{username}' already exists, skipping")
                        self.stats['users']['skipped'] += 1
                        continue

                    if self.dry_run:
                        logger.info(f"[DRY RUN] Would import user: {username}")
                        self.stats['users']['imported'] += 1
                        continue

                    # Create new user
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        full_name=user_data.get('full_name'),
                        hashed_password=user_data['hashed_password'],
                        disabled=user_data.get('disabled', False),
                        created_at=self._parse_datetime(user_data.get('created_at')),
                        last_login=self._parse_datetime(user_data.get('last_login'))
                    )

                    session.add(user)
                    await session.commit()

                    logger.info(f"✅ Imported user: {username}")
                    self.stats['users']['imported'] += 1

                except Exception as e:
                    logger.error(f"Error importing user '{username}': {e}")
                    self.stats['users']['errors'] += 1
                    if not self.dry_run:
                        await session.rollback()

    async def import_characters(self, data_dir: Path):
        """Import characters from data/characters/*.json"""
        characters_dir = data_dir / "characters"

        if not characters_dir.exists():
            logger.warning(f"Characters directory not found: {characters_dir}")
            return

        logger.info(f"Importing characters from {characters_dir}")

        # Get default user ID (for entities without user_id)
        async with get_session() as session:
            result = await session.execute(select(User).limit(1))
            default_user = result.scalar_one_or_none()
            default_user_id = default_user.id if default_user else None

        character_files = list(characters_dir.glob("*.json"))
        logger.info(f"Found {len(character_files)} character files")

        async with get_session() as session:
            for char_file in character_files:
                # Skip reference images
                if char_file.stem.endswith('_ref'):
                    continue

                try:
                    with open(char_file, 'r') as f:
                        char_data = json.load(f)

                    character_id = char_data.get('character_id', char_file.stem)

                    # Check if character already exists
                    result = await session.execute(
                        select(Character).where(Character.character_id == character_id)
                    )
                    existing_char = result.scalar_one_or_none()

                    if existing_char:
                        logger.info(f"Character '{character_id}' already exists, skipping")
                        self.stats['characters']['skipped'] += 1
                        continue

                    if self.dry_run:
                        logger.info(f"[DRY RUN] Would import character: {char_data.get('name', character_id)}")
                        self.stats['characters']['imported'] += 1
                        continue

                    # Create new character
                    character = Character(
                        character_id=character_id,
                        name=char_data['name'],
                        visual_description=char_data.get('visual_description'),
                        physical_description=char_data.get('physical_description'),
                        personality=char_data.get('personality'),
                        reference_image_path=char_data.get('reference_image_path'),
                        age=char_data.get('age'),
                        skin_tone=char_data.get('skin_tone'),
                        face_description=char_data.get('face_description'),
                        hair_description=char_data.get('hair_description'),
                        body_description=char_data.get('body_description'),
                        tags=char_data.get('tags', []),
                        meta=char_data.get('metadata', {}),
                        created_at=self._parse_datetime(char_data.get('created_at')),
                        updated_at=self._parse_datetime(char_data.get('updated_at')),
                        user_id=default_user_id
                    )

                    session.add(character)
                    await session.commit()

                    logger.info(f"✅ Imported character: {char_data['name']} ({character_id})")
                    self.stats['characters']['imported'] += 1

                except Exception as e:
                    logger.error(f"Error importing character from {char_file}: {e}")
                    self.stats['characters']['errors'] += 1
                    if not self.dry_run:
                        await session.rollback()

    async def import_clothing_items(self, data_dir: Path):
        """Import clothing items from data/clothing_items/*.json"""
        items_dir = data_dir / "clothing_items"

        if not items_dir.exists():
            logger.warning(f"Clothing items directory not found: {items_dir}")
            return

        logger.info(f"Importing clothing items from {items_dir}")

        # Get default user ID
        async with get_session() as session:
            result = await session.execute(select(User).limit(1))
            default_user = result.scalar_one_or_none()
            default_user_id = default_user.id if default_user else None

        item_files = list(items_dir.glob("*.json"))
        logger.info(f"Found {len(item_files)} clothing item files")

        async with get_session() as session:
            for item_file in item_files:
                try:
                    with open(item_file, 'r') as f:
                        item_data = json.load(f)

                    item_id = item_data.get('item_id', item_file.stem)

                    # Check if item already exists
                    result = await session.execute(
                        select(ClothingItem).where(ClothingItem.item_id == item_id)
                    )
                    existing_item = result.scalar_one_or_none()

                    if existing_item:
                        self.stats['clothing_items']['skipped'] += 1
                        continue

                    if self.dry_run:
                        logger.info(f"[DRY RUN] Would import item: {item_data.get('item', item_id)}")
                        self.stats['clothing_items']['imported'] += 1
                        continue

                    # Create new clothing item
                    clothing_item = ClothingItem(
                        item_id=item_id,
                        category=item_data['category'],
                        item=item_data['item'],
                        fabric=item_data.get('fabric'),
                        color=item_data.get('color'),
                        details=item_data.get('details'),
                        source_image=item_data.get('source_image'),
                        preview_image_path=item_data.get('preview_image_path'),
                        created_at=self._parse_datetime(item_data.get('created_at')),
                        updated_at=self._parse_datetime(item_data.get('updated_at')),
                        user_id=default_user_id
                    )

                    session.add(clothing_item)
                    await session.commit()

                    logger.info(f"✅ Imported item: {item_data['item']} ({item_data['category']})")
                    self.stats['clothing_items']['imported'] += 1

                except Exception as e:
                    logger.error(f"Error importing item from {item_file}: {e}")
                    self.stats['clothing_items']['errors'] += 1
                    if not self.dry_run:
                        await session.rollback()

    async def import_board_games(self, data_dir: Path):
        """Import board games from data/board_games/*.json"""
        games_dir = data_dir / "board_games"

        if not games_dir.exists():
            logger.warning(f"Board games directory not found: {games_dir}")
            return

        logger.info(f"Importing board games from {games_dir}")

        # Get default user ID
        async with get_session() as session:
            result = await session.execute(select(User).limit(1))
            default_user = result.scalar_one_or_none()
            default_user_id = default_user.id if default_user else None

        game_files = list(games_dir.glob("*.json"))
        logger.info(f"Found {len(game_files)} board game files")

        async with get_session() as session:
            for game_file in game_files:
                try:
                    with open(game_file, 'r') as f:
                        game_data = json.load(f)

                    game_id = game_data.get('game_id', game_file.stem)

                    # Check if game already exists
                    result = await session.execute(
                        select(BoardGame).where(BoardGame.game_id == game_id)
                    )
                    existing_game = result.scalar_one_or_none()

                    if existing_game:
                        self.stats['board_games']['skipped'] += 1
                        continue

                    if self.dry_run:
                        logger.info(f"[DRY RUN] Would import game: {game_data.get('name', game_id)}")
                        self.stats['board_games']['imported'] += 1
                        continue

                    # Create new board game
                    board_game = BoardGame(
                        game_id=game_id,
                        name=game_data['name'],
                        bgg_id=game_data.get('bgg_id'),
                        designer=game_data.get('designer'),
                        publisher=game_data.get('publisher'),
                        year=game_data.get('year'),
                        description=game_data.get('description'),
                        player_count_min=game_data.get('player_count_min'),
                        player_count_max=game_data.get('player_count_max'),
                        playtime_min=game_data.get('playtime_min'),
                        playtime_max=game_data.get('playtime_max'),
                        complexity=game_data.get('complexity'),
                        meta=game_data.get('metadata', {}),
                        created_at=self._parse_datetime(game_data.get('created_at')),
                        updated_at=self._parse_datetime(game_data.get('updated_at')),
                        user_id=default_user_id
                    )

                    session.add(board_game)
                    await session.commit()

                    logger.info(f"✅ Imported game: {game_data['name']}")
                    self.stats['board_games']['imported'] += 1

                except Exception as e:
                    logger.error(f"Error importing game from {game_file}: {e}")
                    self.stats['board_games']['errors'] += 1
                    if not self.dry_run:
                        await session.rollback()

    def print_summary(self):
        """Print import statistics"""
        print("\n" + "="*60)
        print("📊 IMPORT SUMMARY")
        print("="*60)

        for entity_type, stats in self.stats.items():
            total = stats['imported'] + stats['skipped'] + stats['errors']
            if total > 0:
                print(f"\n{entity_type.upper()}: {total} total")
                print(f"  ✅ Imported: {stats['imported']}")
                print(f"  ⏭️  Skipped:  {stats['skipped']}")
                if stats['errors'] > 0:
                    print(f"  ❌ Errors:   {stats['errors']}")

        print("\n" + "="*60)


async def main():
    """Main import function"""
    parser = argparse.ArgumentParser(
        description="Import JSON data to PostgreSQL database"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Perform a dry run without actually importing data"
    )
    parser.add_argument(
        '--entity',
        choices=['users', 'characters', 'clothing_items', 'board_games', 'all'],
        default='all',
        help="Which entity type to import (default: all)"
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path('/app/data'),
        help="Path to data directory (default: /app/data)"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No data will be imported\n")

    importer = DataImporter(dry_run=args.dry_run)

    print(f"📁 Data directory: {args.data_dir}")
    print(f"🎯 Importing: {args.entity}\n")

    try:
        # Import entities based on selection
        if args.entity in ('users', 'all'):
            await importer.import_users(args.data_dir)

        if args.entity in ('characters', 'all'):
            await importer.import_characters(args.data_dir)

        if args.entity in ('clothing_items', 'all'):
            await importer.import_clothing_items(args.data_dir)

        if args.entity in ('board_games', 'all'):
            await importer.import_board_games(args.data_dir)

        # Print summary
        importer.print_summary()

        if args.dry_run:
            print("\n✅ Dry run complete. Run without --dry-run to import data.\n")
        else:
            print("\n✅ Import complete!\n")

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        print(f"\n❌ Import failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
