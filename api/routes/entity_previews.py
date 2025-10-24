"""
Entity Preview Optimization Routes

On-demand generation of optimized preview sizes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from sqlalchemy import select

from api.models.jobs import JobType
from api.services.job_queue import get_job_queue_manager
from api.services.rq_worker import get_rq_service
from api.logging_config import get_logger
from api.database import get_db

router = APIRouter()
logger = get_logger(__name__)


async def get_entity_name(entity_type: str, entity_id: str) -> str:
    """
    Get human-readable entity name for job description

    Args:
        entity_type: Entity type (e.g., 'clothing_items', 'characters')
        entity_id: Entity UUID

    Returns:
        Entity name or fallback string
    """
    try:
        async for db in get_db():
            if entity_type == 'clothing_items':
                from api.models.db import ClothingItem
                stmt = select(ClothingItem).where(ClothingItem.item_id == entity_id)
                result = await db.execute(stmt)
                item = result.scalar_one_or_none()
                if item:
                    return item.item
            elif entity_type == 'characters':
                from api.models.db import Character
                stmt = select(Character).where(Character.character_id == entity_id)
                result = await db.execute(stmt)
                char = result.scalar_one_or_none()
                if char:
                    return char.name
            # Add more entity types as needed

            return f"{entity_type}/{entity_id}"
    except Exception as e:
        logger.warning(f"Failed to fetch entity name: {e}")
        return f"{entity_type}/{entity_id}"


class OptimizePreviewRequest(BaseModel):
    entity_type: str  # e.g., 'clothing_items', 'characters'
    entity_id: str    # UUID
    size: str         # 'small', 'medium', 'large', or 'full'


@router.post("/optimize")
async def optimize_preview(request: OptimizePreviewRequest):
    """
    Generate optimized preview size on-demand

    Called by EntityPreviewImage when a specific size doesn't exist.
    Creates a background job to generate just that size.
    """
    # Validate size
    if request.size not in ['small', 'medium', 'large', 'full']:
        raise HTTPException(status_code=400, detail="Size must be 'small', 'medium', 'large', or 'full'")

    # Check if source preview exists
    source_path = Path(f"entity_previews/{request.entity_type}/{request.entity_id}_preview.png")
    if not source_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Source preview not found for {request.entity_type}/{request.entity_id}"
        )

    # Full size already exists (it's the source)
    if request.size == 'full':
        return {
            "status": "exists",
            "path": f"/entity_previews/{request.entity_type}/{request.entity_id}_preview.png"
        }

    # Check if optimized version already exists
    optimized_path = Path(f"entity_previews/{request.entity_type}/{request.entity_id}_preview_{request.size}.png")
    if optimized_path.exists():
        return {
            "status": "exists",
            "path": f"/entity_previews/{request.entity_type}/{request.entity_id}_preview_{request.size}.png"
        }

    # Get entity name for better job description
    entity_name = await get_entity_name(request.entity_type, request.entity_id)

    # Format entity type for display (e.g., 'clothing_items' -> 'Clothing Item')
    entity_type_display = request.entity_type.replace('_', ' ').title().rstrip('s')

    # Create optimization job with descriptive title and description
    job_id = get_job_queue_manager().create_job(
        job_type=JobType.GENERATE_IMAGE,
        title=f"Generate Preview Image ({request.size})",
        description=f"{entity_type_display}: {entity_name}",
        metadata={
            "entity_type": request.entity_type,
            "entity_id": request.entity_id,
            "optimization_size": request.size
        }
    )

    logger.info(f"Queueing on-demand optimization: {request.entity_type}/{request.entity_id} ({request.size})")

    # Enqueue optimization job via RQ
    from api.workers.jobs import optimize_preview_size_job
    get_rq_service().enqueue(
        optimize_preview_size_job,
        job_id,
        request.entity_type,
        request.entity_id,
        request.size,
        priority='high'  # User is waiting for this
    )

    return {
        "status": "generating",
        "job_id": job_id,
        "message": f"Generating {request.size} preview for {request.entity_type}/{request.entity_id}"
    }
