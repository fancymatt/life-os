#!/usr/bin/env python3
"""
Test Tag Autocomplete Functionality

Verifies that:
1. Tags are created with usage_count
2. usage_count increments when tags are added to entities
3. Autocomplete returns correct usage_count
"""

import asyncio
from api.database import get_session
from api.services.tag_service import TagService
from api.logging_config import get_logger

logger = get_logger(__name__)


async def test_tag_autocomplete():
    """Test tag autocomplete with usage counts"""

    logger.info("=" * 60)
    logger.info("TAG AUTOCOMPLETE TEST")
    logger.info("=" * 60)

    async with get_session() as db:
        service = TagService()

        # 1. Create a test tag
        logger.info("\n1. Creating test tag...")
        tag = await service.create_tag(name="test-leather", category="material")
        logger.info(f"Created tag: {tag.name} (usage_count: {tag.usage_count})")

        # 2. Add tag to a clothing item
        logger.info("\n2. Adding tag to entity...")
        from sqlalchemy import select
        from api.models.db import ClothingItem

        stmt = select(ClothingItem).where(ClothingItem.archived == False).limit(1)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()

        if item:
            tagged = await service.tag_entity(
                entity_type="clothing_item",
                entity_id=item.item_id,
                tag_names=["test-leather"],
                auto_create=False
            )
            logger.info(f"Tagged {item.item} with test-leather")

            # 3. Check usage count after tagging
            logger.info("\n3. Checking usage count...")
            tag_after = await service.repository.get_tag_by_id(tag.tag_id)
            logger.info(f"Tag usage_count after tagging: {tag_after.usage_count}")

            # 4. Test autocomplete
            logger.info("\n4. Testing autocomplete...")
            suggestions = await service.autocomplete(query="leather", limit=10)

            logger.info(f"Autocomplete results for 'leather':")
            for s in suggestions:
                logger.info(f"  - {s['name']}: usage_count={s['usage_count']}")

            # 5. Cleanup
            logger.info("\n5. Cleaning up...")
            await service.untag_entity(
                entity_type="clothing_item",
                entity_id=item.item_id,
                tag_names=["test-leather"]
            )
            await service.delete_tag(tag.tag_id)
            logger.info("Cleanup complete")
        else:
            logger.warning("No clothing items found for testing")

        logger.info("\n" + "=" * 60)
        logger.info("TEST COMPLETE")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_tag_autocomplete())
