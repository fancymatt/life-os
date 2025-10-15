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
from api.services.task_tracker import get_task_tracker
from api.config import settings
from api.routes.analyzers import download_or_decode_image

router = APIRouter()
generator_service = GeneratorService()
preset_service = PresetService()


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
    Generates multiple variations in the background.
    """
    from ai_tools.modular_image_generator.tool import ModularImageGenerator

    # Validate subject image exists
    subject_path = Path(request.subject_image)
    if not subject_path.exists():
        raise HTTPException(status_code=404, detail=f"Subject image not found: {request.subject_image}")

    # Create task for tracking
    tracker = get_task_tracker()
    task = tracker.create_task("modular_generation", total=request.variations)

    # Build kwargs for generator
    kwargs = {
        "subject_image": str(subject_path),
        "output_dir": "output/generated"
    }

    # Add preset IDs for enabled categories
    if request.outfit:
        kwargs["outfit"] = request.outfit
    if request.visual_style:
        kwargs["visual_style"] = request.visual_style
    if request.art_style:
        kwargs["art_style"] = request.art_style
    if request.hair_style:
        kwargs["hair_style"] = request.hair_style
    if request.hair_color:
        kwargs["hair_color"] = request.hair_color
    if request.makeup:
        kwargs["makeup"] = request.makeup
    if request.expression:
        kwargs["expression"] = request.expression
    if request.accessories:
        kwargs["accessories"] = request.accessories

    # Define background task
    async def generate_variations():
        """Generate all requested variations with resilient error handling (async)"""
        task.set_in_progress("Starting generation...")
        generator = ModularImageGenerator()
        successful_paths = []
        failed_items = []

        for i in range(request.variations):
            try:
                task.update(
                    current=i,
                    message=f"Generating variation {i + 1}/{request.variations}..."
                )
                print(f"🎨 Generating variation {i + 1}/{request.variations}...")

                result = await generator.agenerate(**kwargs)
                successful_paths.append(str(result.file_path))
                print(f"✅ Variation {i + 1} complete: {result.file_path}")

            except Exception as e:
                # Log the error but continue with remaining variations
                error_msg = str(e)
                failed_items.append({
                    "variation": i + 1,
                    "error": error_msg
                })
                print(f"⚠️ Variation {i + 1} failed: {error_msg}")
                print(f"   Continuing with remaining variations...")

        # Determine final status
        if len(successful_paths) == 0:
            # All variations failed
            error_summary = f"All {request.variations} variations failed. Errors: " + "; ".join([f"Variation {item['variation']}: {item['error']}" for item in failed_items])
            task.set_failed(error_summary)
            print(f"❌ All variations failed")
        elif len(failed_items) == 0:
            # All variations succeeded
            task.set_completed(
                result={"file_paths": successful_paths},
                message=f"Generated {len(successful_paths)} variation(s) successfully"
            )
            print(f"🎉 All {request.variations} variation(s) generated successfully!")
        else:
            # Partial success
            task.set_completed(
                result={
                    "file_paths": successful_paths,
                    "failed": failed_items,
                    "summary": f"{len(successful_paths)}/{request.variations} succeeded, {len(failed_items)} failed"
                },
                message=f"Generated {len(successful_paths)}/{request.variations} variations ({len(failed_items)} failed)"
            )
            print(f"⚠️ Partial success: {len(successful_paths)} succeeded, {len(failed_items)} failed")

    # Start generation in background
    background_tasks.add_task(generate_variations)

    return {
        "message": "Modular generation started",
        "status": "generating",
        "task_id": task.task_id,
        "variations": request.variations,
        "output_dir": "output/generated"
    }


@router.get("/modular/status/{task_id}")
async def get_generation_status(task_id: str):
    """
    Get the status of a modular generation task

    Returns progress information including current/total and status
    """
    tracker = get_task_tracker()
    task = tracker.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    return task.to_dict()


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
