#!/usr/bin/env python3
"""
Run Database Migration

Creates the images and image_entity_relationships tables.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import init_db, get_logger

logger = get_logger(__name__)


async def main():
    """Run database migration"""
    try:
        logger.info("Running database migration...")
        await init_db()
        logger.info("✅ Migration completed successfully")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
