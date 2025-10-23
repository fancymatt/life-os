#!/usr/bin/env python3
"""
Add character relationships to images based on filename prefixes.

Images are named like: {character_id}_ref_modular_{timestamp}.png
This script extracts the character_id and adds the relationship to the database.
"""

import asyncio
from api.database import get_session
from api.services.image_service import ImageService
from api.services.character_service_db import CharacterServiceDB
from api.logging_config import get_logger

logger = get_logger(__name__)

async def add_character_relationships():
    # Get all characters to build a mapping
    async with get_session() as char_session:
        character_service = CharacterServiceDB(char_session, user_id=None)
        characters = await character_service.list_characters()

    character_map = {char['character_id']: char['name'] for char in characters}

    logger.info(f"Found {len(character_map)} characters:")
    for char_id, name in character_map.items():
        logger.info(f"  {char_id}: {name}")
    logger.info("")

    async with get_session() as session:
        image_service = ImageService(session)

        # Get all images
        images = await image_service.list_all_images(limit=200)

        logger.info(f"Checking {len(images)} images...")
        logger.info("")

        updated_count = 0
        skipped_count = 0

        for img in images:
            filename = img['filename']
            entities = img.get('entities', {})
            characters_in_image = entities.get('character', [])

            # Skip if already has character relationship
            if characters_in_image:
                skipped_count += 1
                continue

            # Extract character_id from filename (format: {character_id}_ref_modular_...)
            if '_ref_modular_' in filename:
                char_id = filename.split('_ref_modular_')[0]

                if char_id in character_map:
                    logger.info(f"Adding {character_map[char_id]} ({char_id}) to {filename}")

                    # Add character relationship
                    await image_service.add_entity_relationships(
                        image_id=img['image_id'],
                        entities=[{
                            "entity_type": "character",
                            "entity_id": char_id,
                            "role": "subject"
                        }]
                    )
                    updated_count += 1
                else:
                    logger.warning(f"Unknown character_id {char_id} in {filename}")
            else:
                logger.warning(f"Unexpected filename format: {filename}")

        logger.info("")
        logger.info(f"Updated {updated_count} images")
        logger.info(f"Skipped {skipped_count} images (already have character)")

if __name__ == "__main__":
    asyncio.run(add_character_relationships())
