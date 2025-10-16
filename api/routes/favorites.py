"""
Favorites Routes

Endpoints for managing user favorite presets.
"""

from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel

from api.services.favorites_service import favorites_service
from api.dependencies.auth import get_current_active_user

router = APIRouter()


class FavoriteRequest(BaseModel):
    """Request to add/remove a favorite"""
    preset_id: str
    category: str


class FavoriteResponse(BaseModel):
    """Response for favorite operations"""
    success: bool
    message: str
    favorites: List[str]


@router.get("/", response_model=List[str])
async def get_favorites(current_user = Depends(get_current_active_user)):
    """Get all favorites for current user"""
    return favorites_service.get_user_favorites(current_user.username)


@router.get("/{category}", response_model=List[str])
async def get_category_favorites(
    category: str,
    current_user = Depends(get_current_active_user)
):
    """Get favorites for a specific category"""
    return favorites_service.get_favorites_by_category(
        current_user.username,
        category
    )


@router.post("/add", response_model=FavoriteResponse)
async def add_favorite(
    request: FavoriteRequest,
    current_user = Depends(get_current_active_user)
):
    """Add a preset to favorites"""
    added = favorites_service.add_favorite(
        current_user.username,
        request.preset_id,
        request.category
    )

    return FavoriteResponse(
        success=added,
        message="Added to favorites" if added else "Already in favorites",
        favorites=favorites_service.get_user_favorites(current_user.username)
    )


@router.post("/remove", response_model=FavoriteResponse)
async def remove_favorite(
    request: FavoriteRequest,
    current_user = Depends(get_current_active_user)
):
    """Remove a preset from favorites"""
    removed = favorites_service.remove_favorite(
        current_user.username,
        request.preset_id,
        request.category
    )

    return FavoriteResponse(
        success=removed,
        message="Removed from favorites" if removed else "Not in favorites",
        favorites=favorites_service.get_user_favorites(current_user.username)
    )


@router.get("/check/{category}/{preset_id}")
async def check_favorite(
    category: str,
    preset_id: str,
    current_user = Depends(get_current_active_user)
):
    """Check if a preset is favorited"""
    is_fav = favorites_service.is_favorite(
        current_user.username,
        preset_id,
        category
    )

    return {"is_favorite": is_fav}
