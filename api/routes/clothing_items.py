"""
Clothing Items Routes

Endpoints for managing clothing item entities.
Clothing items are extracted from outfit images and can be composed into outfits.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.clothing_items_service_db import ClothingItemServiceDB
from api.database import get_db
from api.models.auth import User
from api.dependencies.auth import get_current_active_user

router = APIRouter()


# Request/Response Models
class ClothingItemCreate(BaseModel):
    """Request to create a clothing item"""
    category: str
    item: str
    fabric: str
    color: str
    details: str
    source_image: Optional[str] = None


class ClothingItemUpdate(BaseModel):
    """Request to update a clothing item"""
    category: Optional[str] = None
    item: Optional[str] = None
    fabric: Optional[str] = None
    color: Optional[str] = None
    details: Optional[str] = None
    source_image: Optional[str] = None


class ClothingItemInfo(BaseModel):
    """Clothing item response"""
    item_id: str
    category: str
    item: str
    fabric: str
    color: str
    details: str
    source_image: Optional[str] = None
    preview_image_path: Optional[str] = None
    created_at: str


class ClothingItemListResponse(BaseModel):
    """Response for listing clothing items"""
    count: int
    items: List[ClothingItemInfo]
    category_filter: Optional[str] = None


class CategoriesSummaryResponse(BaseModel):
    """Summary of items per category"""
    categories: dict  # {category: count}
    total_items: int


# Routes
@router.get("/", response_model=ClothingItemListResponse)
async def list_clothing_items(
    category: Optional[str] = Query(None, description="Filter by category (e.g., 'tops', 'bottoms')"),
    limit: Optional[int] = Query(None, description="Maximum number of items to return"),
    offset: int = Query(0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all clothing items

    Optionally filter by category and paginate results.
    Returns items sorted by created_at (newest first).
    """
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)
    items = await service.list_clothing_items(category=category, limit=limit, offset=offset)

    item_infos = [
        ClothingItemInfo(
            item_id=item['item_id'],
            category=item['category'],
            item=item['item'],
            fabric=item['fabric'],
            color=item['color'],
            details=item['details'],
            source_image=item.get('source_image'),
            preview_image_path=item.get('preview_image_path'),
            created_at=item.get('created_at', '')
        )
        for item in items
    ]

    return ClothingItemListResponse(
        count=len(item_infos),
        items=item_infos,
        category_filter=category
    )


@router.get("/categories", response_model=CategoriesSummaryResponse)
async def get_categories_summary(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get summary of items per category

    Returns a dict mapping each category to the number of items in that category.
    Useful for showing category counts in the UI.
    """
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)
    summary = await service.get_categories_summary()

    return CategoriesSummaryResponse(
        categories=summary,
        total_items=sum(summary.values())
    )


@router.get("/{item_id}", response_model=ClothingItemInfo)
async def get_clothing_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a clothing item by ID

    Returns full clothing item data including all details.
    """
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)
    item = await service.get_clothing_item(item_id)

    if not item:
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")

    return ClothingItemInfo(
        item_id=item['item_id'],
        category=item['category'],
        item=item['item'],
        fabric=item['fabric'],
        color=item['color'],
        details=item['details'],
        source_image=item.get('source_image'),
        preview_image_path=item.get('preview_image_path'),
        created_at=item.get('created_at', '')
    )


@router.post("/", response_model=ClothingItemInfo)
async def create_clothing_item(
    request: ClothingItemCreate,
    background_tasks: BackgroundTasks,
    generate_preview: bool = Query(True, description="Generate preview image automatically"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new clothing item

    Manually create a clothing item. Typically, items are created automatically
    by the outfit analyzer, but this endpoint allows manual creation.

    By default, a preview image is generated automatically in the background.
    Set generate_preview=false to skip preview generation (faster for bulk operations).
    """
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)

    item = await service.create_clothing_item(
        category=request.category,
        item=request.item,
        fabric=request.fabric,
        color=request.color,
        details=request.details,
        source_image=request.source_image,
        generate_preview=generate_preview,
        background_tasks=background_tasks if generate_preview else None
    )

    return ClothingItemInfo(
        item_id=item['item_id'],
        category=item['category'],
        item=item['item'],
        fabric=item['fabric'],
        color=item['color'],
        details=item['details'],
        source_image=item.get('source_image'),
        preview_image_path=item.get('preview_image_path'),
        created_at=item.get('created_at', '')
    )


@router.put("/{item_id}", response_model=ClothingItemInfo)
async def update_clothing_item(
    item_id: str,
    request: ClothingItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update a clothing item

    Updates clothing item fields. Only provided fields will be updated.
    """
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)

    item = await service.update_clothing_item(
        item_id=item_id,
        category=request.category,
        item=request.item,
        fabric=request.fabric,
        color=request.color,
        details=request.details,
        source_image=request.source_image
    )

    if not item:
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")

    return ClothingItemInfo(
        item_id=item['item_id'],
        category=item['category'],
        item=item['item'],
        fabric=item['fabric'],
        color=item['color'],
        details=item['details'],
        source_image=item.get('source_image'),
        preview_image_path=item.get('preview_image_path'),
        created_at=item.get('created_at', '')
    )


@router.delete("/{item_id}")
async def delete_clothing_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a clothing item

    Removes the clothing item permanently.
    Note: This will NOT remove the item from any outfits that reference it.
    """
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.delete_clothing_item(item_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")

    return {"message": f"Clothing item {item_id} deleted successfully"}


async def run_preview_generation_job(job_id: str, item_id: str):
    """Background task to generate preview and update job"""
    from api.services.job_queue import get_job_queue_manager
    from api.database import get_session

    try:
        get_job_queue_manager().start_job(job_id)
        get_job_queue_manager().update_progress(job_id, 0.1, "Loading clothing item...")

        async with get_session() as session:
            service = ClothingItemServiceDB(session, user_id=None)

            get_job_queue_manager().update_progress(job_id, 0.3, "Generating preview image...")

            # Generate preview
            item = await service.generate_preview(item_id)

            if not item:
                get_job_queue_manager().fail_job(job_id, f"Clothing item {item_id} not found")
                return

            get_job_queue_manager().update_progress(job_id, 0.9, "Finalizing...")

            # Complete job with item data
            result = {
                'item_id': item['item_id'],
                'category': item['category'],
                'item': item['item'],
                'fabric': item['fabric'],
                'color': item['color'],
                'details': item['details'],
                'source_image': item.get('source_image'),
                'preview_image_path': item.get('preview_image_path'),
                'created_at': item.get('created_at', '')
            }

            get_job_queue_manager().complete_job(job_id, result)

    except Exception as e:
        get_job_queue_manager().fail_job(job_id, str(e))


class BatchGenerateRequest(BaseModel):
    """Request to batch generate previews for specific items"""
    item_ids: List[str]


@router.post("/batch-generate-previews-by-ids")
async def batch_generate_previews_by_ids(
    request: BatchGenerateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Batch generate previews for specific clothing items by ID

    Useful after outfit analysis to generate previews for all items
    that were just created.

    Request Body:
    - item_ids: List of clothing item UUIDs to generate previews for

    Returns summary of queued jobs.
    """
    from api.services.job_queue import get_job_queue_manager
    from api.models.jobs import JobType
    from api.logging_config import get_logger

    logger = get_logger(__name__)
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)

    if not request.item_ids:
        return {
            "message": "No item IDs provided",
            "jobs_queued": 0,
            "job_ids": []
        }

    logger.info(
        f"Batch generating previews for {len(request.item_ids)} specific clothing items",
        extra={'extra_fields': {
            'item_count': len(request.item_ids),
            'item_ids': request.item_ids[:5]  # Log first 5 for debugging
        }}
    )

    # Queue preview generation jobs
    job_ids = []
    not_found = []

    for item_id in request.item_ids:
        # Verify item exists
        item = await service.get_clothing_item(item_id)
        if not item:
            not_found.append(item_id)
            continue

        # Create job
        job_id = get_job_queue_manager().create_job(
            job_type=JobType.GENERATE_IMAGE,
            title=f"Generate preview: {item['item']}",
            description=f"{item['category']} - {item['color']} {item['fabric']}"
        )

        # Queue background task
        background_tasks.add_task(
            run_preview_generation_job,
            job_id,
            item_id
        )

        job_ids.append({
            "job_id": job_id,
            "item_id": item_id,
            "item_name": item['item'],
            "category": item['category']
        })

    logger.info(
        f"Queued {len(job_ids)} preview generation jobs",
        extra={'extra_fields': {
            'job_count': len(job_ids),
            'not_found_count': len(not_found)
        }}
    )

    return {
        "message": f"Queued {len(job_ids)} preview generation jobs",
        "jobs_queued": len(job_ids),
        "job_ids": job_ids,
        "not_found": not_found if not_found else None,
        "note": "Use /jobs endpoint to monitor progress"
    }


@router.post("/batch-generate-previews")
async def batch_generate_previews(
    background_tasks: BackgroundTasks,
    category: Optional[str] = Query(None, description="Only generate previews for items in this category"),
    limit: Optional[int] = Query(None, description="Maximum number of previews to generate"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Batch generate previews for all clothing items without preview images

    Scans all clothing items and queues preview generation jobs for items
    that don't have preview images. Useful for generating previews for items
    created by the outfit analyzer.

    Query Parameters:
    - category: Optional filter to only generate previews for specific category
    - limit: Maximum number of items to process (useful for testing)

    Returns summary of queued jobs.
    """
    from api.services.job_queue import get_job_queue_manager
    from api.models.jobs import JobType
    from api.logging_config import get_logger

    logger = get_logger(__name__)
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)

    # Get all clothing items
    all_items = await service.list_clothing_items(category=category)

    # Filter to items without previews
    items_without_previews = [
        item for item in all_items
        if not item.get('preview_image_path')
    ]

    # Apply limit if specified
    if limit:
        items_without_previews = items_without_previews[:limit]

    if not items_without_previews:
        return {
            "message": "No items found without previews",
            "total_items": len(all_items),
            "items_without_previews": 0,
            "jobs_queued": 0,
            "job_ids": []
        }

    logger.info(
        f"Batch generating previews for {len(items_without_previews)} clothing items",
        extra={'extra_fields': {
            'total_items': len(all_items),
            'items_without_previews': len(items_without_previews),
            'category_filter': category
        }}
    )

    # Queue preview generation jobs
    job_ids = []
    for item in items_without_previews:
        item_id = item['item_id']

        # Create job
        job_id = get_job_queue_manager().create_job(
            job_type=JobType.GENERATE_IMAGE,
            title=f"Generate preview: {item['item']}",
            description=f"{item['category']} - {item['color']} {item['fabric']}"
        )

        # Queue background task
        background_tasks.add_task(
            run_preview_generation_job,
            job_id,
            item_id
        )

        job_ids.append({
            "job_id": job_id,
            "item_id": item_id,
            "item_name": item['item'],
            "category": item['category']
        })

    logger.info(
        f"Queued {len(job_ids)} preview generation jobs",
        extra={'extra_fields': {
            'job_count': len(job_ids),
            'first_job_id': job_ids[0]['job_id'] if job_ids else None
        }}
    )

    return {
        "message": f"Queued {len(job_ids)} preview generation jobs",
        "total_items": len(all_items),
        "items_without_previews": len(items_without_previews),
        "jobs_queued": len(job_ids),
        "job_ids": job_ids,
        "note": "Use /jobs endpoint to monitor progress"
    }


@router.post("/{item_id}/generate-preview")
async def generate_clothing_item_preview(
    item_id: str,
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(True, description="Run generation in background and return job_id"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Generate or regenerate a preview image for a clothing item

    Creates a visualization of the clothing item using AI image generation.
    The preview shows the item based on the configured visualization settings.

    Query Parameters:
    - async_mode: If true (default), returns job_id immediately and processes in background
    """
    from api.services.job_queue import get_job_queue_manager
    from api.models.jobs import JobType

    # Async mode: Create job and return immediately
    if async_mode:
        # Create job
        job_id = get_job_queue_manager().create_job(
            job_type=JobType.GENERATE_IMAGE,
            title="Generating clothing item preview",
            description=f"Item ID: {item_id}"
        )

        # Queue background task
        background_tasks.add_task(
            run_preview_generation_job,
            job_id,
            item_id
        )

        # Return job info
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Preview generation queued. Use /jobs/{job_id} to check status."
        }

    # Synchronous mode: Run generation and return result
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)

    try:
        item = await service.generate_preview(item_id)

        if not item:
            raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")

        return ClothingItemInfo(
            item_id=item['item_id'],
            category=item['category'],
            item=item['item'],
            fabric=item['fabric'],
            color=item['color'],
            details=item['details'],
            source_image=item.get('source_image'),
            preview_image_path=item.get('preview_image_path'),
            created_at=item.get('created_at', '')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")


class TestImageRequest(BaseModel):
    """Request to generate test image with character wearing item"""
    character_id: str
    visual_style: str


async def run_test_image_generation_job(job_id: str, item_id: str, character_id: str, visual_style_id: str):
    """Background task to generate test image of character wearing clothing item"""
    from api.services.job_queue import get_job_queue_manager
    from api.database import get_session
    from api.services.character_service import CharacterService
    from ai_tools.modular_image_generator.tool import ModularImageGenerator
    from api.config import settings
    from pathlib import Path

    try:
        job_manager = get_job_queue_manager()
        job_manager.start_job(job_id)
        job_manager.update_progress(job_id, 0.1, "Loading clothing item and character...")

        async with get_session() as session:
            # Load clothing item
            service = ClothingItemServiceDB(session, user_id=None)
            item = await service.get_clothing_item(item_id)

            if not item:
                job_manager.fail_job(job_id, f"Clothing item {item_id} not found")
                return

            # Load character by name (case-insensitive)
            character_service = CharacterService()
            character = character_service.get_character_by_name(character_id)

            if not character:
                job_manager.fail_job(job_id, f"Character '{character_id}' not found")
                return

            # Get character reference image
            reference_image_path = character.get('reference_image_path')
            if not reference_image_path:
                job_manager.fail_job(job_id, f"Character {character_id} has no reference image")
                return

            subject_path = Path(reference_image_path)
            if not subject_path.exists():
                job_manager.fail_job(job_id, f"Character reference image not found: {reference_image_path}")
                return

            job_manager.update_progress(job_id, 0.3, "Generating test image...")

            # Generate image with modular generator
            generator = ModularImageGenerator()

            # Create a temporary outfit spec with morphsuit + clothing item
            from ai_capabilities.specs import OutfitSpec, ClothingItem

            # Build outfit description with morphsuit + specific item
            morphsuit_outfit = OutfitSpec(
                suggested_name=f"Test: {item['item']}",
                style_genre="Contemporary",
                formality="Casual",
                aesthetic=f"Black morphsuit showcasing {item['item']}",
                clothing_items=[
                    ClothingItem(
                        item="black morphsuit",
                        fabric="stretch jersey",
                        color="solid black",
                        details="Full body coverage from neck to ankles, completely black and featureless, serves as neutral base"
                    ),
                    ClothingItem(
                        item=item['item'],
                        fabric=item['fabric'],
                        color=item['color'],
                        details=item['details']
                    )
                ],
                color_palette=["black", item['color']],
                suggested_description=f"Black morphsuit base with {item['item']} ({item['color']} {item['fabric']}) as the focal point"
            )

            # Generate using character reference + outfit + visual style
            result = await generator.agenerate(
                subject_image=str(subject_path),
                outfit=morphsuit_outfit,
                visual_style=visual_style_id,  # Pass UUID, not name
                output_dir="output/generated"
            )

            job_manager.update_progress(job_id, 0.9, "Finalizing...")

            # Complete job with result
            job_manager.complete_job(job_id, {
                'file_path': str(result.file_path),
                'item_id': item_id,
                'character_id': character_id,
                'visual_style_id': visual_style_id
            })

    except Exception as e:
        from api.services.job_queue import get_job_queue_manager
        get_job_queue_manager().fail_job(job_id, str(e))


@router.post("/{item_id}/generate-test-image")
async def generate_test_image(
    item_id: str,
    request: TestImageRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Generate a test image of a character wearing this clothing item

    Creates a test visualization showing the specified character wearing the clothing item.
    The character is rendered in a black morphsuit with only the specified clothing item
    shown in its actual appearance.

    Request Body:
    - character_id: ID of character to use (e.g., 'jenny')
    - visual_style: Visual style preset to use (e.g., 'White Studio')

    Returns job ID for tracking generation progress.
    """
    from api.services.job_queue import get_job_queue_manager
    from api.models.jobs import JobType

    # Verify clothing item exists
    service = ClothingItemServiceDB(db, user_id=current_user.id if current_user else None)
    item = await service.get_clothing_item(item_id)

    if not item:
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")

    # Create job
    job_id = get_job_queue_manager().create_job(
        job_type=JobType.GENERATE_IMAGE,
        title=f"Test image: {item['item']}",
        description=f"{request.character_id} wearing {item['item']} ({request.visual_style})"
    )

    # Queue background task
    background_tasks.add_task(
        run_test_image_generation_job,
        job_id,
        item_id,
        request.character_id,
        request.visual_style  # This should be a UUID (e.g., 'b1ed9953-a91d-4257-98de-bf8b2f256293')
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Test image generation queued. Use /jobs/{job_id} to check status."
    }
