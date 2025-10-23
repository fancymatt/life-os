"""
Composition Routes

Endpoints for saving and loading preset combinations (compositions).
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from api.services.composition_service_db import CompositionServiceDB
from api.database import get_db
from api.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


class CompositionSaveRequest(BaseModel):
    name: str
    subject: str
    presets: List[dict]

@router.post("/save")
async def save_composition(
    request: CompositionSaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Save a preset combination as a named composition

    Args:
        request: Composition save request with name, subject, and presets
    """
    service = CompositionServiceDB(db, user_id=current_user.id if current_user else None)

    # Generate composition ID from name
    composition_id = request.name.lower().replace(' ', '-').replace('_', '-')

    composition_data = await service.save_composition(
        composition_id=composition_id,
        name=request.name,
        subject=request.subject,
        presets=request.presets
    )

    return {
        "message": "Composition saved successfully",
        "composition_id": composition_id,
        "composition": composition_data
    }


@router.get("/list")
async def list_compositions(
    limit: Optional[int] = Query(None, description="Maximum number of compositions to return"),
    offset: int = Query(0, description="Number of compositions to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all saved compositions for the current user

    Supports pagination via limit/offset parameters.
    Returns compositions sorted by updated_at (newest first).
    """
    service = CompositionServiceDB(db, user_id=current_user.id if current_user else None)

    # Get both compositions and total count
    compositions = await service.list_compositions(limit=limit, offset=offset)
    total_count = await service.count_compositions()

    return {
        "count": total_count,  # Total count, not page count
        "compositions": compositions
    }


@router.get("/{composition_id}")
async def get_composition(
    composition_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a specific composition by ID
    """
    service = CompositionServiceDB(db, user_id=current_user.id if current_user else None)
    composition = await service.get_composition(composition_id)

    if not composition:
        raise HTTPException(status_code=404, detail=f"Composition not found: {composition_id}")

    return composition


@router.delete("/{composition_id}")
async def delete_composition(
    composition_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a composition
    """
    service = CompositionServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.delete_composition(composition_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Composition not found: {composition_id}")

    return {
        "message": "Composition deleted successfully",
        "composition_id": composition_id
    }
