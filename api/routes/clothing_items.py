"""
Clothing Items Routes

Endpoints for managing clothing item entities.
Clothing items are extracted from outfit images and can be composed into outfits.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel

from api.services.clothing_items_service import ClothingItemsService
from api.models.auth import User
from api.dependencies.auth import get_current_active_user

router = APIRouter()


# Request/Response Models
class ClothingItemCreate(BaseModel):
    """Request to create a clothing item"""
    category: str
    item: str
    fabric: str
    color: str
    details: str
    source_image: Optional[str] = None


class ClothingItemUpdate(BaseModel):
    """Request to update a clothing item"""
    category: Optional[str] = None
    item: Optional[str] = None
    fabric: Optional[str] = None
    color: Optional[str] = None
    details: Optional[str] = None
    source_image: Optional[str] = None


class ClothingItemInfo(BaseModel):
    """Clothing item response"""
    item_id: str
    category: str
    item: str
    fabric: str
    color: str
    details: str
    source_image: Optional[str] = None
    created_at: str


class ClothingItemListResponse(BaseModel):
    """Response for listing clothing items"""
    count: int
    items: List[ClothingItemInfo]
    category_filter: Optional[str] = None


class CategoriesSummaryResponse(BaseModel):
    """Summary of items per category"""
    categories: dict  # {category: count}
    total_items: int


# Routes
@router.get("/", response_model=ClothingItemListResponse)
async def list_clothing_items(
    category: Optional[str] = Query(None, description="Filter by category (e.g., 'tops', 'bottoms')"),
    limit: Optional[int] = Query(None, description="Maximum number of items to return"),
    offset: int = Query(0, description="Number of items to skip"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all clothing items

    Optionally filter by category and paginate results.
    Returns items sorted by created_at (newest first).
    """
    service = ClothingItemsService()
    items = service.list_clothing_items(category=category, limit=limit, offset=offset)

    item_infos = [
        ClothingItemInfo(
            item_id=item['item_id'],
            category=item['category'],
            item=item['item'],
            fabric=item['fabric'],
            color=item['color'],
            details=item['details'],
            source_image=item.get('source_image'),
            created_at=item.get('created_at', '')
        )
        for item in items
    ]

    return ClothingItemListResponse(
        count=len(item_infos),
        items=item_infos,
        category_filter=category
    )


@router.get("/categories", response_model=CategoriesSummaryResponse)
async def get_categories_summary(
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get summary of items per category

    Returns a dict mapping each category to the number of items in that category.
    Useful for showing category counts in the UI.
    """
    service = ClothingItemsService()
    summary = service.get_categories_summary()

    return CategoriesSummaryResponse(
        categories=summary,
        total_items=sum(summary.values())
    )


@router.get("/{item_id}", response_model=ClothingItemInfo)
async def get_clothing_item(
    item_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a clothing item by ID

    Returns full clothing item data including all details.
    """
    service = ClothingItemsService()
    item = service.get_clothing_item(item_id)

    if not item:
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")

    return ClothingItemInfo(
        item_id=item['item_id'],
        category=item['category'],
        item=item['item'],
        fabric=item['fabric'],
        color=item['color'],
        details=item['details'],
        source_image=item.get('source_image'),
        created_at=item.get('created_at', '')
    )


@router.post("/", response_model=ClothingItemInfo)
async def create_clothing_item(
    request: ClothingItemCreate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new clothing item

    Manually create a clothing item. Typically, items are created automatically
    by the outfit analyzer, but this endpoint allows manual creation.
    """
    service = ClothingItemsService()

    item = service.create_clothing_item(
        category=request.category,
        item=request.item,
        fabric=request.fabric,
        color=request.color,
        details=request.details,
        source_image=request.source_image
    )

    return ClothingItemInfo(
        item_id=item['item_id'],
        category=item['category'],
        item=item['item'],
        fabric=item['fabric'],
        color=item['color'],
        details=item['details'],
        source_image=item.get('source_image'),
        created_at=item.get('created_at', '')
    )


@router.put("/{item_id}", response_model=ClothingItemInfo)
async def update_clothing_item(
    item_id: str,
    request: ClothingItemUpdate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update a clothing item

    Updates clothing item fields. Only provided fields will be updated.
    """
    service = ClothingItemsService()

    item = service.update_clothing_item(
        item_id=item_id,
        category=request.category,
        item=request.item,
        fabric=request.fabric,
        color=request.color,
        details=request.details,
        source_image=request.source_image
    )

    if not item:
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")

    return ClothingItemInfo(
        item_id=item['item_id'],
        category=item['category'],
        item=item['item'],
        fabric=item['fabric'],
        color=item['color'],
        details=item['details'],
        source_image=item.get('source_image'),
        created_at=item.get('created_at', '')
    )


@router.delete("/{item_id}")
async def delete_clothing_item(
    item_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a clothing item

    Removes the clothing item permanently.
    Note: This will NOT remove the item from any outfits that reference it.
    """
    service = ClothingItemsService()
    success = service.delete_clothing_item(item_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")

    return {"message": f"Clothing item {item_id} deleted successfully"}
