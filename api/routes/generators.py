"""
Generator Routes

Endpoints for running image generators.
"""

import time
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import List

from api.models.requests import GenerateRequest
from api.models.responses import GenerateResponse, ToolInfo
from api.services import GeneratorService, PresetService
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
