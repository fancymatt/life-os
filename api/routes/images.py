"""
Image Routes

Endpoints for querying generated images and their entity relationships.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from api.database import get_db
from api.services.image_service import ImageService
from api.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
async def list_images(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all images with their entity relationships

    Args:
        limit: Maximum number of images to return (default: 100)
        offset: Number of images to skip for pagination (default: 0)

    Returns:
        Dict with images list and metadata
    """
    try:
        image_service = ImageService(db)
        images = await image_service.list_all_images(limit=limit, offset=offset)
        total = await image_service.count_all_images()

        logger.info(f"Retrieved {len(images)} images", extra={'extra_fields': {
            'count': len(images),
            'total': total,
            'limit': limit,
            'offset': offset
        }})

        return {
            "images": images,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Failed to list images: {e}", extra={'extra_fields': {
            'error': str(e)
        }})
        raise HTTPException(status_code=500, detail=f"Failed to list images: {str(e)}")


@router.get("/by-entity/{entity_type}/{entity_id}")
async def get_images_by_entity(
    entity_type: str,
    entity_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all images that used a specific entity (for entity galleries)

    This is the main endpoint for displaying image galleries within entity detail pages.

    Args:
        entity_type: Type of entity (e.g., "character", "clothing_item", "preset")
        entity_id: ID of the entity
        limit: Maximum number of images to return (default: 50)
        offset: Number of images to skip for pagination (default: 0)

    Returns:
        Dict with images list and count

    Example:
        GET /api/images/by-entity/clothing_item/jacket-123?limit=20&offset=0
        Returns all images that used the jacket with ID "jacket-123"
    """
    try:
        image_service = ImageService(db)
        images = await image_service.get_images_by_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset
        )

        # Get total count for pagination
        total = await image_service.count_images_by_entity(
            entity_type=entity_type,
            entity_id=entity_id
        )

        logger.info(f"Retrieved {len(images)} images for {entity_type}:{entity_id}", extra={'extra_fields': {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'count': len(images),
            'total': total
        }})

        return {
            "images": images,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Failed to get images for {entity_type}:{entity_id}: {e}", extra={'extra_fields': {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'error': str(e)
        }})
        raise HTTPException(status_code=500, detail=f"Failed to get images: {str(e)}")


@router.get("/{image_id}")
async def get_image(
    image_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get an image with all its entity relationships

    Args:
        image_id: UUID of the image

    Returns:
        Dict with image data and relationships
    """
    try:
        image_service = ImageService(db)
        image_data = await image_service.get_image_with_relationships(image_id)

        if not image_data:
            raise HTTPException(status_code=404, detail=f"Image not found: {image_id}")

        return image_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get image {image_id}: {e}", extra={'extra_fields': {
            'image_id': image_id,
            'error': str(e)
        }})
        raise HTTPException(status_code=500, detail=f"Failed to get image: {str(e)}")


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete an image and all its relationships

    Args:
        image_id: UUID of the image

    Returns:
        Success message
    """
    try:
        image_service = ImageService(db)
        success = await image_service.delete_image(image_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Image not found: {image_id}")

        return {"message": f"Image {image_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete image {image_id}: {e}", extra={'extra_fields': {
            'image_id': image_id,
            'error': str(e)
        }})
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
