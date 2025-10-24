"""
Image Optimization Service

Creates cached, optimized versions of preview images for faster loading.

Sizes:
- small: 100x100px (for small thumbnails)
- medium: 400x400px (for grid cards - displays at 200px)
- large: 800x800px (for detail/preview panels)
- full: Original resolution (no optimization)
"""

from PIL import Image
from pathlib import Path
from typing import Dict, Optional, Tuple
from api.logging_config import get_logger

logger = get_logger(__name__)


class ImageOptimizer:
    """
    Creates cached, optimized versions of preview images

    This service automatically generates multiple sizes of each preview image
    to reduce bandwidth usage and improve page load times.

    Expected bandwidth savings: 80-90% for entity list views
    """

    SIZES = {
        'small': (100, 100),
        'medium': (400, 400),
        'large': (800, 800),
        'full': None  # Original size
    }

    def optimize_preview(
        self,
        source_path: str,
        entity_type: str,
        entity_id: str
    ) -> Dict[str, str]:
        """
        Generate optimized versions of preview image

        Args:
            source_path: Path to original preview image (filesystem path, not web path)
            entity_type: Entity type (e.g., 'clothing_item', 'character')
            entity_id: Entity UUID

        Returns:
            Dict with web-accessible paths to all sizes:
            {
                'small': '/entity_previews/{type}/{id}_preview_small.png',
                'medium': '/entity_previews/{type}/{id}_preview_medium.png',
                'full': '/entity_previews/{type}/{id}_preview.png'
            }

        Raises:
            FileNotFoundError: If source image doesn't exist
            Exception: If image processing fails
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")

        logger.info(f"Optimizing preview for {entity_type}/{entity_id}")

        try:
            # Load original image
            img = Image.open(source)
            logger.debug(f"Loaded image: {img.size[0]}x{img.size[1]}, format={img.format}")

            # Convert to RGB if necessary (handles RGBA, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Output directory
            output_dir = Path(f"entity_previews/{entity_type}")
            output_dir.mkdir(parents=True, exist_ok=True)

            result = {}

            # Generate each size
            for size_name, dimensions in self.SIZES.items():
                if dimensions is None:
                    # Full size - just reference original
                    result['full'] = f"/entity_previews/{entity_type}/{entity_id}_preview.png"
                    logger.debug(f"Full size: using original at {result['full']}")
                    continue

                # Create a copy for resizing
                resized = img.copy()

                # Resize with high-quality downsampling (LANCZOS is best for downsizing)
                resized.thumbnail(dimensions, Image.Resampling.LANCZOS)

                # Save optimized version with compression
                output_path = output_dir / f"{entity_id}_preview_{size_name}.png"
                resized.save(output_path, 'PNG', optimize=True, quality=85)

                result[size_name] = f"/entity_previews/{entity_type}/{entity_id}_preview_{size_name}.png"

                # Log file size for verification
                file_size_kb = output_path.stat().st_size / 1024
                logger.debug(f"{size_name} size: {resized.size[0]}x{resized.size[1]}, {file_size_kb:.1f}KB at {output_path}")

            logger.info(f"✅ Optimized preview for {entity_type}/{entity_id}: {len(result)} versions created")
            return result

        except Exception as e:
            logger.error(f"Failed to optimize preview for {entity_type}/{entity_id}: {e}", exc_info=True)
            raise

    def cleanup_old_versions(self, entity_type: str, entity_id: str) -> None:
        """
        Delete old optimized versions when preview is regenerated

        This ensures we don't accumulate stale cached images.

        Args:
            entity_type: Entity type (e.g., 'clothing_item')
            entity_id: Entity UUID
        """
        output_dir = Path(f"entity_previews/{entity_type}")

        if not output_dir.exists():
            return

        deleted_count = 0

        for size_name in ['small', 'medium', 'large']:
            old_file = output_dir / f"{entity_id}_preview_{size_name}.png"
            if old_file.exists():
                try:
                    old_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old cached image: {old_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete old cached image {old_file}: {e}")

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old cached images for {entity_type}/{entity_id}")

    def get_image_info(self, image_path: str) -> Dict[str, any]:
        """
        Get information about an image file

        Useful for debugging and verification.

        Args:
            image_path: Path to image file

        Returns:
            Dict with image info: {
                'width': int,
                'height': int,
                'format': str,
                'mode': str,
                'size_kb': float
            }
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        img = Image.open(path)
        file_size_kb = path.stat().st_size / 1024

        return {
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'mode': img.mode,
            'size_kb': round(file_size_kb, 2)
        }
