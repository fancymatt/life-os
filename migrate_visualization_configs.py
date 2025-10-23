#!/usr/bin/env python3
"""
Migrate Visualization Configs from JSON to Database

This script migrates visualization configuration data from JSON files
in data/visualization_configs/ to the PostgreSQL database.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from api.database import get_session
from api.services.visualization_config_service_db import VisualizationConfigServiceDB
from api.logging_config import get_logger

logger = get_logger(__name__)


async def migrate_visualization_configs():
    """Migrate visualization configs from JSON files to database"""

    # Path to JSON files
    json_dir = Path(__file__).parent / "data" / "visualization_configs"

    if not json_dir.exists():
        logger.info(f"No visualization configs directory found at {json_dir}")
        return

    # Get all JSON files
    json_files = list(json_dir.glob("*.json"))

    if not json_files:
        logger.info("No visualization config JSON files to migrate")
        return

    logger.info(f"Found {len(json_files)} visualization configs to migrate")

    migrated_count = 0
    error_count = 0

    # Import needed for creating models
    from api.models.db import VisualizationConfig
    from datetime import datetime

    for json_file in json_files:
        # Each config gets its own session/transaction to prevent rollback cascades
        async with get_session() as session:
            try:
                service = VisualizationConfigServiceDB(session, user_id=None)

                # Read JSON file
                with open(json_file, 'r') as f:
                    config_data = json.load(f)

                config_id = json_file.stem
                display_name = config_data.get('display_name', 'Unnamed Config')

                logger.info(f"Migrating config: {display_name} ({config_id})")

                # Check if config already exists in database
                existing = await service.get_config(config_id)
                if existing:
                    logger.info(f"  ⏭️  Skipping {config_id} - already exists in database")
                    continue

                # Get values with defaults for required NOT NULL fields
                composition_style = config_data.get('composition_style') or 'product'
                framing = config_data.get('framing') or 'medium'
                angle = config_data.get('angle') or 'front'
                background = config_data.get('background') or 'white'
                lighting = config_data.get('lighting') or 'soft_even'

                config = VisualizationConfig(
                    config_id=config_id,  # Use existing UUID from filename
                    entity_type=config_data.get('entity_type', 'unknown'),
                    display_name=display_name,
                    composition_style=composition_style,
                    framing=framing,
                    angle=angle,
                    background=background,
                    lighting=lighting,
                    art_style_id=config_data.get('art_style_id'),
                    reference_image_path=config_data.get('reference_image_path'),
                    additional_instructions=config_data.get('additional_instructions') or '',
                    image_size=config_data.get('image_size', '1024x1024'),
                    model=config_data.get('model', 'gemini/gemini-2.5-flash-image'),
                    is_default=config_data.get('is_default', False),
                    created_at=datetime.fromisoformat(config_data['created_at']) if 'created_at' in config_data else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(config_data['updated_at']) if 'updated_at' in config_data else datetime.utcnow(),
                    user_id=None
                )

                await service.repository.create(config)
                await session.commit()

                logger.info(f"  ✅ Migrated {display_name}")
                migrated_count += 1

            except Exception as e:
                logger.error(f"  ❌ Failed to migrate {json_file.name}: {e}")
                error_count += 1
                # Transaction will rollback automatically on exception
                continue

    logger.info(f"\n📊 Migration Summary:")
    logger.info(f"  Total configs found: {len(json_files)}")
    logger.info(f"  Successfully migrated: {migrated_count}")
    logger.info(f"  Errors: {error_count}")
    logger.info(f"  Skipped (already exists): {len(json_files) - migrated_count - error_count}")


async def verify_migration():
    """Verify that all configs were migrated successfully"""

    json_dir = Path(__file__).parent / "data" / "visualization_configs"

    if not json_dir.exists():
        return

    json_files = list(json_dir.glob("*.json"))

    logger.info(f"\n🔍 Verifying migration...")

    async with get_session() as session:
        service = VisualizationConfigServiceDB(session, user_id=None)

        all_configs = await service.list_configs()

        logger.info(f"  Database contains {len(all_configs)} visualization configs")

        # Check each JSON file exists in database
        missing = []
        for json_file in json_files:
            config_id = json_file.stem
            exists = any(c['config_id'] == config_id for c in all_configs)
            if not exists:
                missing.append(config_id)

        if missing:
            logger.warning(f"  ⚠️  {len(missing)} configs missing from database: {missing}")
        else:
            logger.info(f"  ✅ All configs successfully migrated!")

        # Show entity type breakdown
        entity_types = {}
        for config in all_configs:
            entity_type = config['entity_type']
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

        logger.info(f"\n📋 Configs by entity type:")
        for entity_type, count in sorted(entity_types.items()):
            logger.info(f"  {entity_type}: {count}")


async def main():
    """Main migration function"""
    logger.info("🚀 Starting visualization configs migration\n")

    try:
        await migrate_visualization_configs()
        await verify_migration()

        logger.info("\n✅ Migration completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
