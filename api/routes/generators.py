"""
Generator Routes

Endpoints for running image generators.
"""

import time
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List

from api.models.requests import GenerateRequest, ModularGenerateRequest
from api.models.responses import GenerateResponse, ToolInfo
from api.services import GeneratorService, PresetService
from api.services.job_queue import get_job_queue_manager
from api.models.jobs import JobType
from api.config import settings
from api.routes.analyzers import download_or_decode_image
from api.logging_config import get_logger

router = APIRouter()
generator_service = GeneratorService()
preset_service = PresetService()
logger = get_logger(__name__)


@router.get("/", response_model=List[ToolInfo])
async def list_generators():
    """List all available generators"""
    generators = generator_service.list_generators()
    return [ToolInfo(**g) for g in generators]


@router.post("/modular")
async def generate_modular(request: ModularGenerateRequest, background_tasks: BackgroundTasks):
    """
    Modular generation endpoint for frontend workflow

    Accepts a subject image path and preset IDs for any combination of categories.
    Also supports character IDs in the format "character:{character_id}".
    Generates multiple variations in the background.
    """
    from ai_tools.modular_image_generator.tool import ModularImageGenerator
    from api.services.character_service import CharacterService

    # Resolve subject image path
    # Check if it's a character reference
    if request.subject_image.startswith("character:"):
        character_id = request.subject_image.split(":", 1)[1]
        character_service = CharacterService()
        character_data = character_service.get_character(character_id)

        if not character_data:
            raise HTTPException(status_code=404, detail=f"Character not found: {character_id}")

        reference_image_path = character_data.get('reference_image_path')
        if not reference_image_path:
            raise HTTPException(status_code=404, detail=f"Character {character_id} has no reference image")

        subject_path = Path(reference_image_path)
        if not subject_path.exists():
            raise HTTPException(status_code=404, detail=f"Character reference image not found: {reference_image_path}")
    else:
        # Regular subject image path
        subject_path = Path(request.subject_image)

        # If it's just a filename (no path), look in subjects directory first, then uploads
        if not subject_path.is_absolute() and str(subject_path).count('/') == 0:
            # Try subjects directory
            subjects_path = settings.subjects_dir / request.subject_image
            if subjects_path.exists():
                subject_path = subjects_path
            else:
                # Try uploads directory
                uploads_path = settings.upload_dir / request.subject_image
                if uploads_path.exists():
                    subject_path = uploads_path
                else:
                    raise HTTPException(status_code=404, detail=f"Subject image not found: {request.subject_image}")
        elif not subject_path.exists():
            raise HTTPException(status_code=404, detail=f"Subject image not found: {request.subject_image}")

    # Create job for tracking
    job_manager = get_job_queue_manager()
    job_id = job_manager.create_job(
        job_type=JobType.BATCH_GENERATE,
        title=f"Generate {request.variations} variation(s)",
        description=f"Modular generation from {request.subject_image}",
        total_steps=request.variations,
        cancelable=True
    )

    # Build kwargs for generator
    kwargs = {
        "subject_image": str(subject_path),
        "output_dir": "output/generated"
    }

    # Add preset IDs and clothing item IDs for enabled categories
    # Clothing item categories
    clothing_categories = [
        'headwear', 'eyewear', 'earrings', 'neckwear', 'tops', 'overtops',
        'outerwear', 'one_piece', 'bottoms', 'belts', 'hosiery', 'footwear',
        'bags', 'wristwear', 'handwear'
    ]

    # Style preset categories
    style_categories = [
        'visual_style', 'art_style', 'hair_style', 'hair_color',
        'makeup', 'expression', 'accessories'
    ]

    # Add all categories dynamically
    for category in clothing_categories + style_categories:
        value = getattr(request, category, None)
        if value is not None:
            kwargs[category] = value
            logger.info(f"Added {category}: {value}", extra={'extra_fields': {
                'category': category,
                'value': str(value)
            }})

    logger.info(f"Final kwargs keys: {list(kwargs.keys())}", extra={'extra_fields': {
        'kwargs_keys': list(kwargs.keys())
    }})

    # Define background task
    async def generate_variations():
        """Generate all requested variations with resilient error handling (async)"""
        job_manager = get_job_queue_manager()

        try:
            job_manager.start_job(job_id)
            job_manager.update_progress(job_id, 0.0, "Starting generation...")

            generator = ModularImageGenerator()
            successful_paths = []
            failed_items = []

            for i in range(request.variations):
                try:
                    # Update progress
                    progress = i / request.variations
                    job_manager.update_progress(
                        job_id,
                        progress,
                        message=f"Generating variation {i + 1}/{request.variations}...",
                        current_step=i
                    )
                    logger.info(f"Generating variation {i + 1}/{request.variations}", extra={'extra_fields': {
                        'job_id': job_id,
                        'variation': i + 1,
                        'total_variations': request.variations
                    }})

                    result = await generator.agenerate(**kwargs)
                    successful_paths.append(str(result.file_path))
                    logger.info(f"Variation {i + 1} complete", extra={'extra_fields': {
                        'job_id': job_id,
                        'variation': i + 1,
                        'file_path': str(result.file_path)
                    }})

                except Exception as e:
                    # Log the error but continue with remaining variations
                    error_msg = str(e)
                    failed_items.append({
                        "variation": i + 1,
                        "error": error_msg
                    })
                    logger.warning(f"Variation {i + 1} failed, continuing with remaining", extra={'extra_fields': {
                        'job_id': job_id,
                        'variation': i + 1,
                        'error': error_msg
                    }})

            # Determine final status
            if len(successful_paths) == 0:
                # All variations failed
                error_summary = f"All {request.variations} variations failed. Errors: " + "; ".join([f"Variation {item['variation']}: {item['error']}" for item in failed_items])
                job_manager.fail_job(job_id, error_summary)
                logger.error(f"All variations failed", extra={'extra_fields': {
                    'job_id': job_id,
                    'total_variations': request.variations,
                    'failed_count': len(failed_items)
                }})
            elif len(failed_items) == 0:
                # All variations succeeded
                job_manager.complete_job(
                    job_id,
                    result={"file_paths": successful_paths}
                )
                logger.info(f"All variations generated successfully", extra={'extra_fields': {
                    'job_id': job_id,
                    'variations_count': request.variations
                }})
            else:
                # Partial success
                job_manager.complete_job(
                    job_id,
                    result={
                        "file_paths": successful_paths,
                        "failed": failed_items,
                        "summary": f"{len(successful_paths)}/{request.variations} succeeded, {len(failed_items)} failed"
                    }
                )
                logger.warning(f"Partial success", extra={'extra_fields': {
                    'job_id': job_id,
                    'succeeded': len(successful_paths),
                    'failed': len(failed_items),
                    'total': request.variations
                }})

        except Exception as e:
            # Unexpected error in the generation loop itself
            job_manager.fail_job(job_id, f"Generation failed: {str(e)}")
            logger.error(f"Generation failed with unexpected error", exc_info=e, extra={'extra_fields': {
                'job_id': job_id,
                'error': str(e)
            }})

    # Start generation in background
    background_tasks.add_task(generate_variations)

    return {
        "message": "Modular generation started",
        "status": "queued",
        "job_id": job_id,
        "variations": request.variations,
        "output_dir": "output/generated"
    }


@router.get("/modular/status/{job_id}")
async def get_generation_status(job_id: str):
    """
    Get the status of a modular generation job

    [DEPRECATED] Use /api/jobs/{job_id} instead.
    This endpoint is kept for backward compatibility.
    """
    job_manager = get_job_queue_manager()
    try:
        job = job_manager.get_job(job_id)
        # Return in old format for compatibility
        return {
            "status": job.status,
            "progress": job.progress * 100,  # Convert to percentage
            "message": job.progress_message or "",
            "result": job.result,
            "error": job.error
        }
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")


@router.post("/{generator_name}", response_model=GenerateResponse)
async def generate_image(generator_name: str, request: GenerateRequest):
    """
    Generate an image with a specific generator

    Available generators:
    - modular: Generate with any combination of specs
    - outfit: Generate with outfit and style
    - style-transfer: Transfer visual style only
    - art-style: Generate with artistic style
    - combined: Multi-spec transformation
    """
    if not generator_service.validate_generator(generator_name):
        raise HTTPException(status_code=404, detail=f"Generator not found: {generator_name}")

    start_time = time.time()

    try:
        # Download or decode subject image
        subject_path = await download_or_decode_image(request.subject_image)

        # Build specs dict
        specs = {}

        # Handle preset names or direct specs for each field
        for field in ['outfit', 'visual_style', 'art_style', 'hair_style',
                      'hair_color', 'makeup', 'expression', 'accessories']:
            value = getattr(request, field)
            if value:
                if isinstance(value, str):
                    # It's a preset name - keep as string, service will load it
                    specs[field] = value
                elif isinstance(value, dict):
                    # It's a direct spec dict
                    specs[field] = value

        # Add temperature
        specs['temperature'] = request.temperature

        # Run generator
        result = generator_service.generate(
            generator_name,
            subject_path,
            settings.output_dir,
            **specs
        )

        generation_time = time.time() - start_time

        # Get cost info
        generator_info = generator_service.get_generator_info(generator_name)

        # Convert result paths to URLs
        if isinstance(result, dict) and 'file_path' in result:
            # Make URL relative to output directory
            file_path = Path(result['file_path'])
            relative_path = file_path.relative_to(settings.base_dir)
            result['image_url'] = f"/{relative_path}"

        return GenerateResponse(
            status="completed",
            result={
                "image_url": result.get('image_url') if isinstance(result, dict) else None,
                "generation_time": generation_time,
                "cost": generator_info["estimated_cost"]
            }
        )

    except Exception as e:
        return GenerateResponse(
            status="failed",
            error=str(e)
        )
    finally:
        # Cleanup temp file
        if 'subject_path' in locals() and subject_path.exists():
            subject_path.unlink()
