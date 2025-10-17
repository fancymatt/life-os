"""
Preset Routes

Endpoints for managing presets (CRUD operations).
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path

from api.models.requests import PresetCreate, PresetUpdate
from api.models.responses import PresetListResponse, PresetInfo
from api.services import PresetService

router = APIRouter()
preset_service = PresetService()


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
                print(f"Warning: Failed to load category {category}: {e}")
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


@router.post("/{category}/{preset_id}/generate-test")
async def generate_test_image(category: str, preset_id: str, background_tasks: BackgroundTasks):
    """
    Generate a test image using jenny.png with this preset applied

    Uses the jenny.png image from the project root as the subject
    and applies the specified preset to generate a test image.
    """
    try:
        # Import here to avoid circular dependencies
        from ai_tools.modular_image_generator.tool import ModularImageGenerator

        # Check if jenny.png exists
        jenny_path = Path("jenny.png")
        if not jenny_path.exists():
            raise HTTPException(status_code=404, detail="jenny.png not found in project root")

        # Load the preset data
        preset_data = preset_service.get_preset(category, preset_id)

        # Remove metadata if present
        if '_metadata' in preset_data:
            del preset_data['_metadata']

        # Map category to the appropriate parameter
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
            raise HTTPException(status_code=400, detail=f"Category '{category}' does not support test generation")

        # Queue generation as background task
        async def generate_image():
            try:
                generator = ModularImageGenerator()

                # Build kwargs with only this preset
                kwargs = {
                    "subject_image": str(jenny_path),
                    "output_dir": f"output/test_generations/{category}",
                    category_param_map[category]: preset_id  # Pass preset_id to load from preset manager
                }

                result = await generator.agenerate(**kwargs)
                print(f"✅ Test image generated: {result.file_path}")

            except Exception as e:
                print(f"⚠️ Test generation failed: {e}")

        background_tasks.add_task(generate_image)

        return {
            "message": "Test image generation started",
            "status": "generating",
            "category": category,
            "preset_id": preset_id
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
