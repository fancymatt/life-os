"""
Preset Routes

Endpoints for managing presets (CRUD operations).
"""

from fastapi import APIRouter, HTTPException
from typing import List

from api.models.requests import PresetCreate, PresetUpdate
from api.models.responses import PresetListResponse, PresetInfo
from api.services import PresetService

router = APIRouter()
preset_service = PresetService()


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


@router.get("/{category}/{name}", response_model=dict)
async def get_preset(category: str, name: str):
    """
    Get a specific preset

    Returns the full preset data for the specified preset.
    """
    try:
        return preset_service.get_preset(category, name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{category}", response_model=dict)
async def create_preset(category: str, request: PresetCreate):
    """
    Create a new preset

    Creates a new preset in the specified category.
    """
    try:
        preset_path = preset_service.create_preset(
            category,
            request.name,
            request.data,
            request.notes
        )
        return {
            "message": "Preset created successfully",
            "path": str(preset_path),
            "category": category,
            "name": request.name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{category}/{name}", response_model=dict)
async def update_preset(category: str, name: str, request: PresetUpdate):
    """
    Update an existing preset

    Updates the data for an existing preset.
    """
    try:
        preset_path = preset_service.update_preset(
            category,
            name,
            request.data,
            request.notes
        )
        return {
            "message": "Preset updated successfully",
            "path": str(preset_path),
            "category": category,
            "name": name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{category}/{name}", response_model=dict)
async def delete_preset(category: str, name: str):
    """
    Delete a preset

    Permanently deletes the specified preset.
    """
    try:
        preset_service.delete_preset(category, name)
        return {
            "message": "Preset deleted successfully",
            "category": category,
            "name": name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{category}/{name}/duplicate", response_model=dict)
async def duplicate_preset(category: str, name: str, new_name: str):
    """
    Duplicate a preset

    Creates a copy of an existing preset with a new name.
    """
    try:
        preset_path = preset_service.duplicate_preset(category, name, new_name)
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
