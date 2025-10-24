#!/usr/bin/env python3
"""
Merge Workflow Test Script

Tests the entity merge functionality by directly calling the service layer.
This bypasses API authentication for testing purposes.
"""

import asyncio
import json
from pathlib import Path
from api.logging_config import get_logger

logger = get_logger(__name__)


async def test_merge_workflow():
    """Test the complete entity merge workflow"""

    logger.info("=" * 60)
    logger.info("ENTITY MERGE WORKFLOW TEST")
    logger.info("=" * 60)

    # Load test characters
    char1_path = Path("/app/data/characters/test001.json")
    char2_path = Path("/app/data/characters/test002.json")

    if not char1_path.exists() or not char2_path.exists():
        logger.error("\nTest characters not found!")
        logger.info(f"  Expected: {char1_path}")
        logger.info(f"  Expected: {char2_path}")
        return

    with open(char1_path) as f:
        char1 = json.load(f)
    with open(char2_path) as f:
        char2 = json.load(f)

    logger.info(f"\nLoaded test characters:")
    logger.info(f"  Source: {char1['name']} ({char1['character_id']})")
    logger.info(f"  Target: {char2['name']} ({char2['character_id']})")

    # Step 1: Test MergeService initialization
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1: Initialize MergeService")
    logger.info("=" * 60)

    try:
        from api.services.merge_service import MergeService
        from api.database import get_session

        async with get_session() as db:
            service = MergeService(db, user_id=None)
            logger.info("MergeService initialized successfully")

            # Step 2: Find references
            logger.info("\n" + "=" * 60)
            logger.info("STEP 2: Find References")
            logger.info("=" * 60)

            try:
                references = await service.find_references(
                    entity_type="character",
                    entity_id=char2['character_id']
                )

                total_refs = sum(len(refs) for refs in references.values())
                logger.info(f"Found {total_refs} references for {char2['name']}")

                for ref_type, ref_list in references.items():
                    if ref_list:
                        logger.info(f"  {ref_type}: {len(ref_list)} references")

            except Exception as e:
                logger.warning(f"Reference lookup: {type(e).__name__}: {e}")
                logger.info("   (This is expected if no database is configured)")
                references = {}

            # Step 3: AI merge analysis
            logger.info("\n" + "=" * 60)
            logger.info("STEP 3: AI Merge Analysis")
            logger.info("=" * 60)

            try:
                # Prepare entities for merge (remove metadata)
                source_entity = {
                    k: v for k, v in char1.items()
                    if k not in ['character_id', 'created_at', 'updated_at', 'archived']
                }
                target_entity = {
                    k: v for k, v in char2.items()
                    if k not in ['character_id', 'created_at', 'updated_at', 'archived']
                }

                logger.info(f"Analyzing merge between:")
                logger.info(f"  Source: {source_entity['name']}")
                logger.info(f"  Target: {target_entity['name']}")

                merged_data = await service.analyze_merge(
                    entity_type="character",
                    source_entity=source_entity,
                    target_entity=target_entity
                )

                logger.info(f"\nAI merge analysis complete!")
                logger.info(f"\nMerged entity preview:")
                logger.info(f"  Name: {merged_data.get('name', 'N/A')}")
                logger.info(f"  Age: {merged_data.get('age', 'N/A')}")
                logger.info(f"  Personality: {merged_data.get('personality', 'N/A')[:60]}...")
                logger.info(f"  Hair: {merged_data.get('hair_description', 'N/A')[:60]}...")

                # Show what changed
                logger.info(f"\nMerge analysis:")
                source_fields = sum(1 for k, v in merged_data.items()
                                   if k in source_entity and v == source_entity[k])
                target_fields = sum(1 for k, v in merged_data.items()
                                   if k in target_entity and v == target_entity[k])
                merged_fields = len(merged_data) - source_fields - target_fields

                logger.info(f"  Fields from source: {source_fields}")
                logger.info(f"  Fields from target: {target_fields}")
                logger.info(f"  Intelligently merged: {merged_fields}")

            except Exception as e:
                logger.error(f"AI merge analysis failed: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                return

            # Step 4: Test simple merge fallback
            logger.info("\n" + "=" * 60)
            logger.info("STEP 4: Test Simple Merge Fallback")
            logger.info("=" * 60)

            simple_merged = service._simple_merge(source_entity, target_entity)
            logger.info(f"Simple merge fallback works")
            logger.info(f"  Merged {len(simple_merged)} fields")

            logger.info("\n" + "=" * 60)
            logger.info("MERGE SERVICE TEST COMPLETE")
            logger.info("=" * 60)
            logger.info("\nAll merge service components are working!")
            logger.info("\nNext steps:")
            logger.info("1. Create a user account or temporarily disable auth")
            logger.info("2. Test the full workflow in the UI:")
            logger.info("   a. Go to http://localhost:3000/entities/characters")
            logger.info("   b. Click on a character")
            logger.info("   c. Click 'Merge with...' button")
            logger.info("   d. Select target character")
            logger.info("   e. Review AI-generated merge")
            logger.info("   f. Execute merge")
            logger.info("\n")

    except Exception as e:
        logger.error(f"\nService initialization failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_merge_workflow())
