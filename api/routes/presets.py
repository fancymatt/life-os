"""
Preset Routes

Endpoints for managing presets (CRUD operations).
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path

from api.logging_config import get_logger
from api.models.requests import PresetCreate, PresetUpdate
from api.models.responses import PresetListResponse, PresetInfo
from api.services import PresetService

router = APIRouter()
logger = get_logger(__name__)
preset_service = PresetService()


async def run_preview_generation_job(job_id: str, category: str, preset_id: str):
    """Background task to generate preview and update job"""
    from ai_tools.shared.visualizer import PresetVisualizer
    from api.services.job_queue import get_job_queue_manager
    import asyncio
    import traceback

    logger.info(f"Starting preview generation for {category}/{preset_id} (Job: {job_id})")

    try:
        job_manager = get_job_queue_manager()
        job_manager.start_job(job_id)
        job_manager.update_progress(job_id, 0.1, "Loading preset data...")
        logger.info(f"Job {job_id} updated to running")

        # Generate preview using visualizer
        visualizer = PresetVisualizer()
        preset_data = preset_service.get_preset(category, preset_id)
        logger.info(f"Loaded preset data for {category}/{preset_id}")

        # Remove metadata
        if '_metadata' in preset_data:
            del preset_data['_metadata']

        job_manager.update_progress(job_id, 0.2, "Loading visualization config...")

        # Load visualization config for this entity type
        from api.services.visualization_config_service_db import VisualizationConfigServiceDB
        from api.database import get_session

        # Convert category to entity_type (strip trailing 's')
        entity_type = category.rstrip('s') if category.endswith('s') else category

        # Get viz config from database
        async with get_session() as session:
            viz_service = VisualizationConfigServiceDB(session, user_id=None)
            viz_config = await viz_service.get_default_config(entity_type)

        logger.info(f"Loaded viz config for {entity_type}: {viz_config.get('display_name') if viz_config else 'None'}")

        job_manager.update_progress(job_id, 0.4, "Generating preview image...")
        logger.info(f"Starting visualization for {category}/{preset_id}")

        # Get correct output directory from preset manager
        preset_dir = preset_service.preset_manager._get_preset_dir(category)
        output_file = str(preset_dir / f"{preset_id}_preview.png")

        # Generate preview using create_preset_preview with viz config
        # Pass preset_data as dict (not Pydantic spec), create_preset_preview handles it
        output_path = await asyncio.to_thread(
            visualizer.create_preset_preview,
            preset_data,
            output_file,
            category,
            viz_config
        )

        job_manager.complete_job(job_id, {"output_path": str(output_path)})
        logger.info(f"✅ Preview generated successfully for {category}/{preset_id}: {output_path}")

    except Exception as e:
        logger.error(f"❌ Preview generation failed for {category}/{preset_id}: {e}")
        logger.error(traceback.format_exc())
        get_job_queue_manager().fail_job(job_id, str(e))


async def run_test_generation_job(job_id: str, category: str, preset_id: str):
    """Background task to generate test image and update job"""
    from ai_tools.modular_image_generator.tool import ModularImageGenerator
    from api.services.job_queue import get_job_queue_manager

    try:
        job_manager = get_job_queue_manager()
        job_manager.start_job(job_id)
        job_manager.update_progress(job_id, 0.1, "Preparing test generation...")

        # Map category to parameter name
        category_param_map = {
            "outfits": "outfit",
            "visual_styles": "visual_style",
            "art_styles": "art_style",
            "hair_styles": "hair_style",
            "hair_colors": "hair_color",
            "makeup": "makeup",
            "expressions": "expression",
            "accessories": "accessories"
        }

        # Check if jenny.png exists
        jenny_path = Path("jenny.png")
        if not jenny_path.exists():
            raise FileNotFoundError("jenny.png not found in project root")

        job_manager.update_progress(job_id, 0.2, "Loading generator...")

        # Generate test image
        generator = ModularImageGenerator()
        kwargs = {
            "subject_image": str(jenny_path),
            "output_dir": f"output/test_generations/{category}",
            category_param_map[category]: preset_id
        }

        job_manager.update_progress(job_id, 0.4, "Generating image...")

        result = await generator.agenerate(**kwargs)

        job_manager.complete_job(job_id, {"file_path": result.file_path})
        logger.info(f"Test image generated: {result.file_path}")

    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        get_job_queue_manager().fail_job(job_id, str(e))


@router.get("/batch")
async def get_all_presets():
    """
    Get all presets across all categories in a single request

    Returns a dictionary mapping category names to preset lists.
    This is much faster than making separate requests for each category.

    Performance: ~8x faster than individual category requests.
    """
    try:
        categories = preset_service.list_categories()
        result = {}

        for category in categories:
            try:
                presets = preset_service.list_presets(category)
                result[category] = [PresetInfo(**p).dict() for p in presets]
            except Exception as e:
                # If one category fails, continue with others
                logger.warning(f"Failed to load category {category}: {e}")
                result[category] = []

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load presets: {str(e)}")


@router.get("/", response_model=List[str])
async def list_categories():
    """
    List all preset categories

    Returns a list of all available preset categories.
    """
    return preset_service.list_categories()


@router.get("/{category}", response_model=PresetListResponse)
async def list_presets_in_category(category: str):
    """
    List all presets in a category

    Returns detailed information about all presets in the specified category.
    """
    try:
        presets = preset_service.list_presets(category)
        return PresetListResponse(
            category=category,
            count=len(presets),
            presets=[PresetInfo(**p) for p in presets]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{category}/{preset_id}", response_model=dict)
async def get_preset(category: str, preset_id: str):
    """
    Get a specific preset by ID

    Returns the full preset data for the specified preset.
    """
    try:
        return preset_service.get_preset(category, preset_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{category}/", response_model=dict)
async def create_preset(category: str, request: PresetCreate, background_tasks: BackgroundTasks):
    """
    Create a new preset

    Creates a new preset in the specified category.
    Visualization generation runs asynchronously in the background.
    """
    try:
        preset_path, preset_id = preset_service.create_preset(
            category,
            request.name,
            request.data,
            request.notes,
            background_tasks=background_tasks
        )
        return {
            "message": "Preset created successfully",
            "path": str(preset_path),
            "category": category,
            "name": request.name,
            "preset_id": preset_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{category}/{preset_id}", response_model=dict)
async def update_preset(
    category: str,
    preset_id: str,
    request: PresetUpdate,
    background_tasks: BackgroundTasks
):
    """
    Update an existing preset by ID

    Updates the data and/or display name for an existing preset.
    Visualization generation runs asynchronously in the background.
    """
    try:
        preset_service.update_preset(
            category,
            preset_id,
            request.data,
            request.display_name,
            request.notes,
            background_tasks=background_tasks
        )
        return {
            "message": "Preset updated successfully",
            "category": category,
            "preset_id": preset_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{category}/{preset_id}", response_model=dict)
async def delete_preset(category: str, preset_id: str):
    """
    Delete a preset by ID

    Permanently deletes the specified preset.
    """
    try:
        preset_service.delete_preset(category, preset_id)
        return {
            "message": "Preset deleted successfully",
            "category": category,
            "preset_id": preset_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{category}/{name}/duplicate", response_model=dict)
async def duplicate_preset(category: str, name: str, new_name: str, background_tasks: BackgroundTasks):
    """
    Duplicate a preset

    Creates a copy of an existing preset with a new name.
    Visualization generation runs asynchronously in the background.
    """
    try:
        preset_path = preset_service.duplicate_preset(
            category,
            name,
            new_name,
            background_tasks=background_tasks
        )
        return {
            "message": "Preset duplicated successfully",
            "path": str(preset_path),
            "category": category,
            "original_name": name,
            "new_name": new_name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/{category}/{preset_id}/preview")
async def get_preset_preview(category: str, preset_id: str):
    """
    Get preview image for a preset

    Returns the preview image file for presets that support visualizations (e.g., outfits).
    If no preview exists, returns 404.
    """
    try:
        # Get the preview image path from preset manager
        preview_path = preset_service.preset_manager.get_preview_image_path(category, preset_id)

        if not preview_path.exists():
            raise HTTPException(status_code=404, detail="Preview image not found")

        return FileResponse(
            path=str(preview_path),
            media_type="image/png",
            filename=f"{preset_id}_preview.png"
        )
    except HTTPException:
        # Re-raise HTTPException as-is (don't convert to 500)
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{category}/{preset_id}/generate-preview")
async def generate_preset_preview(
    category: str,
    preset_id: str,
    background_tasks: BackgroundTasks
):
    """
    Generate or regenerate a preview image for a preset

    Returns job_id for tracking generation progress.
    """
    from api.services.job_queue import get_job_queue_manager
    from api.models.jobs import JobType

    logger.info(f"🎨 Generate preview endpoint called: {category}/{preset_id}")

    # Create job immediately
    job_id = get_job_queue_manager().create_job(
        job_type=JobType.GENERATE_IMAGE,
        title=f"Generating {category} preview",
        description=f"Preset ID: {preset_id}"
    )
    logger.info(f"Created job {job_id} for preview generation")

    # Queue background task
    background_tasks.add_task(run_preview_generation_job, job_id, category, preset_id)
    logger.info(f"Queued preview generation task for {category}/{preset_id} (Job: {job_id})")

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Preview generation queued"
    }


@router.post("/{category}/{preset_id}/generate-test-image")
async def generate_test_image(
    category: str,
    preset_id: str,
    background_tasks: BackgroundTasks
):
    """
    Generate a test image using jenny with this preset applied

    Returns job_id for tracking generation progress.
    """
    from api.services.job_queue import get_job_queue_manager
    from api.models.jobs import JobType

    # Map category to parameter name
    category_param_map = {
        "outfits": "outfit",
        "visual_styles": "visual_style",
        "art_styles": "art_style",
        "hair_styles": "hair_style",
        "hair_colors": "hair_color",
        "makeup": "makeup",
        "expressions": "expression",
        "accessories": "accessories"
    }

    if category not in category_param_map:
        raise HTTPException(
            status_code=400,
            detail=f"Category '{category}' does not support test generation"
        )

    # Create job immediately
    job_id = get_job_queue_manager().create_job(
        job_type=JobType.GENERATE_IMAGE,
        title=f"Test image: {category}",
        description=f"Preset ID: {preset_id}"
    )

    # Queue background task
    background_tasks.add_task(run_test_generation_job, job_id, category, preset_id)

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Test image generation queued"
    }
