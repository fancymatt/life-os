"""
Composition Routes

Endpoints for saving and loading preset combinations (compositions).
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
import aiofiles

from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from api.config import settings
from api.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_compositions_dir(user: Optional[User] = None) -> Path:
    """Get the compositions directory for a user"""
    if user:
        user_dir = settings.base_dir / "data" / "compositions" / user.username
    else:
        # Default to anonymous user
        user_dir = settings.base_dir / "data" / "compositions" / "anonymous"

    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


class CompositionSaveRequest(BaseModel):
    name: str
    subject: str
    presets: List[dict]

@router.post("/save")
async def save_composition(
    request: CompositionSaveRequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Save a preset combination as a named composition

    Args:
        request: Composition save request with name, subject, and presets
    """
    name = request.name
    subject = request.subject
    presets = request.presets
    compositions_dir = get_compositions_dir(current_user)

    # Generate composition ID from name
    composition_id = name.lower().replace(' ', '-').replace('_', '-')

    # Check if composition already exists
    composition_file = compositions_dir / f"{composition_id}.json"

    composition_data = {
        "composition_id": composition_id,
        "name": name,
        "subject": subject,
        "presets": presets,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    # Update timestamp if it already exists
    if composition_file.exists():
        composition_data["updated_at"] = datetime.now().isoformat()
        # Keep original created_at
        async with aiofiles.open(composition_file, 'r') as f:
            content = await f.read()
            old_data = json.loads(content)
            composition_data["created_at"] = old_data.get("created_at", composition_data["created_at"])

    # Save composition
    async with aiofiles.open(composition_file, 'w') as f:
        await f.write(json.dumps(composition_data, indent=2))

    return {
        "message": "Composition saved successfully",
        "composition_id": composition_id,
        "composition": composition_data
    }


@router.get("/list")
async def list_compositions(
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all saved compositions for the current user
    """
    compositions_dir = get_compositions_dir(current_user)

    compositions = []
    for composition_file in compositions_dir.glob("*.json"):
        try:
            async with aiofiles.open(composition_file, 'r') as f:
                content = await f.read()
                composition_data = json.loads(content)
                compositions.append(composition_data)
        except Exception as e:
            logger.warning(f"Error loading composition", extra={'extra_fields': {
                'composition_file': str(composition_file),
                'error': str(e)
            }})

    # Sort by updated_at (most recent first)
    compositions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    return compositions


@router.get("/{composition_id}")
async def get_composition(
    composition_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a specific composition by ID
    """
    compositions_dir = get_compositions_dir(current_user)
    composition_file = compositions_dir / f"{composition_id}.json"

    if not composition_file.exists():
        raise HTTPException(status_code=404, detail=f"Composition not found: {composition_id}")

    async with aiofiles.open(composition_file, 'r') as f:
        content = await f.read()
        composition_data = json.loads(content)

    return composition_data


@router.delete("/{composition_id}")
async def delete_composition(
    composition_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a composition
    """
    compositions_dir = get_compositions_dir(current_user)
    composition_file = compositions_dir / f"{composition_id}.json"

    if not composition_file.exists():
        raise HTTPException(status_code=404, detail=f"Composition not found: {composition_id}")

    composition_file.unlink()

    return {
        "message": "Composition deleted successfully",
        "composition_id": composition_id
    }
