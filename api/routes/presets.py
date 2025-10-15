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


@router.put("/{category}/{preset_id}", response_model=dict)
async def update_preset(category: str, preset_id: str, request: PresetUpdate):
    """
    Update an existing preset by ID

    Updates the data and/or display name for an existing preset.
    """
    try:
        preset_service.update_preset(
            category,
            preset_id,
            request.data,
            request.display_name,
            request.notes
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
