"""
Favorites Routes

Endpoints for managing user favorite presets.
"""

from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.favorites_service_db import FavoritesServiceDB
from api.database import get_db
from api.models.auth import User
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


# CRITICAL: Support both with and without trailing slash to avoid FastAPI redirect issues
# GET /favorites and GET /favorites/ both work
# POST requests fail after redirect, so we need both paths
@router.get("", response_model=List[str])
@router.get("/", response_model=List[str])
async def get_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all favorites for current user"""
    service = FavoritesServiceDB(db, user_id=current_user.id)
    return await service.get_user_favorites()


@router.get("/{category}", response_model=List[str])
async def get_category_favorites(
    category: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get favorites for a specific category"""
    service = FavoritesServiceDB(db, user_id=current_user.id)
    return await service.get_favorites_by_category(category)


@router.post("/add", response_model=FavoriteResponse)
async def add_favorite(
    request: FavoriteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a preset to favorites"""
    service = FavoritesServiceDB(db, user_id=current_user.id)
    added = await service.add_favorite(
        request.preset_id,
        request.category
    )

    return FavoriteResponse(
        success=added,
        message="Added to favorites" if added else "Already in favorites",
        favorites=await service.get_user_favorites()
    )


@router.post("/remove", response_model=FavoriteResponse)
async def remove_favorite(
    request: FavoriteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a preset from favorites"""
    service = FavoritesServiceDB(db, user_id=current_user.id)
    removed = await service.remove_favorite(
        request.preset_id,
        request.category
    )

    return FavoriteResponse(
        success=removed,
        message="Removed from favorites" if removed else "Not in favorites",
        favorites=await service.get_user_favorites()
    )


@router.get("/check/{category}/{preset_id}")
async def check_favorite(
    category: str,
    preset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if a preset is favorited"""
    service = FavoritesServiceDB(db, user_id=current_user.id)
    is_fav = await service.is_favorite(preset_id, category)

    return {"is_favorite": is_fav}
