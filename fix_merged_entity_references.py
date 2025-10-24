#!/usr/bin/env python3
"""
Fix Image Entity Relationships After Merge

Updates image entity relationships that are pointing to archived entities
that were merged into other entities. This fixes the issue where entity chips
show IDs instead of names.
"""

import asyncio
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models.db import ImageEntityRelationship, Character, ClothingItem, BoardGame
from api.logging_config import get_logger

logger = get_logger(__name__)


async def fix_merged_references():
    """Find and fix image relationships pointing to merged entities"""

    logger.info("=" * 60)
    logger.info("FIX MERGED ENTITY REFERENCES")
    logger.info("=" * 60)

    async with get_session() as db:
        total_fixed = 0

        # Check each entity type
        entity_types = [
            ("character", Character),
            ("clothing_item", ClothingItem),
            ("board_game", BoardGame)
        ]

        for entity_type_name, EntityModel in entity_types:
            logger.info(f"Checking {entity_type_name} references...")

            # Find all image relationships for this entity type
            stmt = select(ImageEntityRelationship).where(
                ImageEntityRelationship.entity_type == entity_type_name
            )
            result = await db.execute(stmt)
            relationships = result.scalars().all()

            logger.info(f"Found {len(relationships)} {entity_type_name} image relationships")

            fixed_count = 0
            for rel in relationships:
                # Check if the entity is archived
                entity_stmt = select(EntityModel).where(
                    EntityModel.archived == True
                )

                # Add the correct ID field filter based on entity type
                if entity_type_name == "character":
                    entity_stmt = entity_stmt.where(EntityModel.character_id == rel.entity_id)
                elif entity_type_name == "clothing_item":
                    entity_stmt = entity_stmt.where(EntityModel.item_id == rel.entity_id)
                elif entity_type_name == "board_game":
                    entity_stmt = entity_stmt.where(EntityModel.game_id == rel.entity_id)

                entity_result = await db.execute(entity_stmt)
                archived_entity = entity_result.scalar_one_or_none()

                if archived_entity:
                    # Check if it has merged_into metadata
                    merged_into = None
                    if hasattr(archived_entity, 'meta') and archived_entity.meta:
                        merged_into = archived_entity.meta.get('merged_into')

                    if merged_into:
                        logger.info(f"Updating relationship: {rel.entity_id} → {merged_into}")

                        # Update the relationship
                        update_stmt = (
                            update(ImageEntityRelationship)
                            .where(ImageEntityRelationship.id == rel.id)
                            .values(entity_id=merged_into)
                        )
                        await db.execute(update_stmt)
                        fixed_count += 1
                        total_fixed += 1

            if fixed_count > 0:
                logger.info(f"Fixed {fixed_count} {entity_type_name} references")
            else:
                logger.info(f"No broken {entity_type_name} references found")

        # Commit all changes
        await db.commit()

        logger.info("=" * 60)
        logger.info(f"COMPLETE - Fixed {total_fixed} total references")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(fix_merged_references())
