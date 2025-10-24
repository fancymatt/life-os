#!/usr/bin/env python3
"""
Migrate Images to Entity Previews Directory

Copies all images from /output/generated/ to entity_previews/images/
with the correct naming format for optimization.
"""
import shutil
from pathlib import Path
import requests
from api.logging_config import get_logger

logger = get_logger(__name__)

# Directories
ENTITY_PREVIEWS_DIR = Path("/app/entity_previews/images")
API_URL = "http://localhost:8000/images/"

def migrate_images():
    """Copy all images to entity_previews directory"""

    # Create entity_previews directory
    ENTITY_PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Created directory: {ENTITY_PREVIEWS_DIR}")

    # Fetch all images from API
    logger.info("🔍 Fetching images from API...")
    response = requests.get(f"{API_URL}?limit=10000")
    response.raise_for_status()
    data = response.json()

    images = data.get("images", [])
    logger.info(f"📊 Found {len(images)} images in database")
    logger.info(f"🚀 Starting migration...\n")

    copied = 0
    skipped = 0
    errors = 0

    for image in images:
        # Source path (file_path from API starts with /)
        source_path = Path(f"/app{image['file_path']}")

        # Destination path: entity_previews/images/{image_id}_preview.png
        dest_path = ENTITY_PREVIEWS_DIR / f"{image['image_id']}_preview.png"

        # Check if source exists
        if not source_path.exists():
            logger.warning(f"Source not found: {source_path}")
            errors += 1
            continue

        # Skip if already exists
        if dest_path.exists():
            skipped += 1
            continue

        # Copy file
        try:
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied: {image['filename'][:50]}... → {dest_path.name}")
            copied += 1
        except Exception as e:
            logger.error(f"Error copying {image['filename']}: {e}")
            errors += 1

    logger.info(f"\n📊 Migration Summary:")
    logger.info(f"   Copied: {copied}")
    logger.info(f"   ⏩ Skipped (already exist): {skipped}")
    logger.error(f"   Errors: {errors}")
    logger.info(f"   📁 Total images: {len(images)}")

if __name__ == "__main__":
    migrate_images()
