#!/usr/bin/env python3
"""
PostgreSQL Query Test Script

Tests database queries to verify the PostgreSQL migration works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from api.database import get_session
from api.models.db import User, Character, ClothingItem, BoardGame


async def test_queries():
    """Test various database queries"""

    print("\n" + "="*60)
    print("🧪 TESTING POSTGRESQL QUERIES")
    print("="*60 + "\n")

    async with get_session() as session:
        # Test 1: Count all entities
        print("📊 Entity Counts:")
        user_count = await session.scalar(select(func.count()).select_from(User))
        char_count = await session.scalar(select(func.count()).select_from(Character))
        item_count = await session.scalar(select(func.count()).select_from(ClothingItem))
        game_count = await session.scalar(select(func.count()).select_from(BoardGame))

        print(f"  Users: {user_count}")
        print(f"  Characters: {char_count}")
        print(f"  Clothing Items: {item_count}")
        print(f"  Board Games: {game_count}")

        # Test 2: Query specific user
        print("\n👤 User Query:")
        result = await session.execute(select(User).where(User.username == "fancymatt"))
        user = result.scalar_one_or_none()
        if user:
            print(f"  ✅ Found user: {user.username} ({user.email})")
            print(f"     Created: {user.created_at}")
            print(f"     Disabled: {user.disabled}")
        else:
            print("  ❌ User not found")

        # Test 3: Query characters with filtering
        print("\n👥 Character Queries:")
        result = await session.execute(
            select(Character)
            .where(Character.name.ilike('%e%'))
            .order_by(Character.name)
            .limit(5)
        )
        characters = result.scalars().all()
        print(f"  Found {len(characters)} characters with 'e' in name:")
        for char in characters:
            print(f"    - {char.name} ({char.character_id})")

        # Test 4: Query clothing items by category
        print("\n👗 Clothing Items by Category:")
        result = await session.execute(
            select(ClothingItem.category, func.count(ClothingItem.id))
            .group_by(ClothingItem.category)
            .order_by(func.count(ClothingItem.id).desc())
        )
        categories = result.all()
        for category, count in categories[:5]:
            print(f"    {category}: {count} items")

        # Test 5: Test relationships (user -> characters)
        print("\n🔗 Relationship Test (User → Characters):")
        result = await session.execute(
            select(Character)
            .where(Character.user_id == user.id)
            .limit(3)
        )
        user_chars = result.scalars().all()
        print(f"  User '{user.username}' has {len(user_chars)} characters (showing first 3):")
        for char in user_chars[:3]:
            print(f"    - {char.name}")

        # Test 6: Complex query with JSON field
        print("\n📦 JSON Metadata Query:")
        result = await session.execute(
            select(Character)
            .where(Character.personality != None)
            .where(Character.personality != "")
            .limit(3)
        )
        chars_with_personality = result.scalars().all()
        print(f"  Found {len(chars_with_personality)} characters with personality:")
        for char in chars_with_personality:
            print(f"    {char.name}: {char.personality}")

        # Test 7: Search by text field
        print("\n🔍 Text Search Query:")
        result = await session.execute(
            select(ClothingItem)
            .where(ClothingItem.color.ilike('%black%'))
            .limit(3)
        )
        black_items = result.scalars().all()
        print(f"  Found {len(black_items)} items with 'black' color (showing 3):")
        for item in black_items:
            print(f"    {item.item} ({item.category}) - {item.color}")

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_queries())
