"""
Outfits Routes

Endpoints for managing outfit composition entities.
Outfits are compositions of clothing item IDs that can be mixed and matched.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel

from api.services.outfits_service import OutfitsService
from api.models.auth import User
from api.dependencies.auth import get_current_active_user

router = APIRouter()


# Request/Response Models
class OutfitCreate(BaseModel):
    """Request to create an outfit"""
    name: str
    clothing_item_ids: List[str]
    notes: Optional[str] = None


class OutfitUpdate(BaseModel):
    """Request to update an outfit"""
    name: Optional[str] = None
    clothing_item_ids: Optional[List[str]] = None
    notes: Optional[str] = None


class OutfitInfo(BaseModel):
    """Outfit response"""
    outfit_id: str
    name: str
    clothing_item_ids: List[str]
    notes: Optional[str] = None
    created_at: str
    updated_at: str


class OutfitListResponse(BaseModel):
    """Response for listing outfits"""
    count: int
    outfits: List[OutfitInfo]


class AddItemRequest(BaseModel):
    """Request to add an item to an outfit"""
    item_id: str


class RemoveItemRequest(BaseModel):
    """Request to remove an item from an outfit"""
    item_id: str


# Routes
@router.get("/", response_model=OutfitListResponse)
async def list_outfits(
    limit: Optional[int] = Query(None, description="Maximum number of outfits to return"),
    offset: int = Query(0, description="Number of outfits to skip"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all outfit compositions

    Returns outfits sorted by updated_at (most recently updated first).
    """
    service = OutfitsService()
    outfits = service.list_outfits(limit=limit, offset=offset)

    outfit_infos = [
        OutfitInfo(
            outfit_id=outfit['outfit_id'],
            name=outfit['name'],
            clothing_item_ids=outfit['clothing_item_ids'],
            notes=outfit.get('notes'),
            created_at=outfit.get('created_at', ''),
            updated_at=outfit.get('updated_at', '')
        )
        for outfit in outfits
    ]

    return OutfitListResponse(
        count=len(outfit_infos),
        outfits=outfit_infos
    )


@router.get("/{outfit_id}", response_model=OutfitInfo)
async def get_outfit(
    outfit_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get an outfit by ID

    Returns full outfit data including all clothing item IDs.
    """
    service = OutfitsService()
    outfit = service.get_outfit(outfit_id)

    if not outfit:
        raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")

    return OutfitInfo(
        outfit_id=outfit['outfit_id'],
        name=outfit['name'],
        clothing_item_ids=outfit['clothing_item_ids'],
        notes=outfit.get('notes'),
        created_at=outfit.get('created_at', ''),
        updated_at=outfit.get('updated_at', '')
    )


@router.post("/", response_model=OutfitInfo)
async def create_outfit(
    request: OutfitCreate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new outfit composition

    Create an outfit by specifying a name and a list of clothing item IDs.
    """
    service = OutfitsService()

    outfit = service.create_outfit(
        name=request.name,
        clothing_item_ids=request.clothing_item_ids,
        notes=request.notes
    )

    return OutfitInfo(
        outfit_id=outfit['outfit_id'],
        name=outfit['name'],
        clothing_item_ids=outfit['clothing_item_ids'],
        notes=outfit.get('notes'),
        created_at=outfit.get('created_at', ''),
        updated_at=outfit.get('updated_at', '')
    )


@router.put("/{outfit_id}", response_model=OutfitInfo)
async def update_outfit(
    outfit_id: str,
    request: OutfitUpdate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update an outfit composition

    Updates outfit fields. Only provided fields will be updated.
    """
    service = OutfitsService()

    outfit = service.update_outfit(
        outfit_id=outfit_id,
        name=request.name,
        clothing_item_ids=request.clothing_item_ids,
        notes=request.notes
    )

    if not outfit:
        raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")

    return OutfitInfo(
        outfit_id=outfit['outfit_id'],
        name=outfit['name'],
        clothing_item_ids=outfit['clothing_item_ids'],
        notes=outfit.get('notes'),
        created_at=outfit.get('created_at', ''),
        updated_at=outfit.get('updated_at', '')
    )


@router.delete("/{outfit_id}")
async def delete_outfit(
    outfit_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete an outfit composition

    Removes the outfit composition. Does NOT delete the clothing items themselves.
    """
    service = OutfitsService()
    success = service.delete_outfit(outfit_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")

    return {"message": f"Outfit {outfit_id} deleted successfully"}


@router.post("/{outfit_id}/items", response_model=OutfitInfo)
async def add_item_to_outfit(
    outfit_id: str,
    request: AddItemRequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Add a clothing item to an outfit

    Adds a clothing item ID to the outfit's item list.
    If the item is already in the outfit, this is a no-op.
    """
    service = OutfitsService()

    outfit = service.add_item_to_outfit(outfit_id, request.item_id)

    if not outfit:
        raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")

    return OutfitInfo(
        outfit_id=outfit['outfit_id'],
        name=outfit['name'],
        clothing_item_ids=outfit['clothing_item_ids'],
        notes=outfit.get('notes'),
        created_at=outfit.get('created_at', ''),
        updated_at=outfit.get('updated_at', '')
    )


@router.delete("/{outfit_id}/items/{item_id}", response_model=OutfitInfo)
async def remove_item_from_outfit(
    outfit_id: str,
    item_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Remove a clothing item from an outfit

    Removes a clothing item ID from the outfit's item list.
    If the item is not in the outfit, this is a no-op.
    """
    service = OutfitsService()

    outfit = service.remove_item_from_outfit(outfit_id, item_id)

    if not outfit:
        raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")

    return OutfitInfo(
        outfit_id=outfit['outfit_id'],
        name=outfit['name'],
        clothing_item_ids=outfit['clothing_item_ids'],
        notes=outfit.get('notes'),
        created_at=outfit.get('created_at', ''),
        updated_at=outfit.get('updated_at', '')
    )
