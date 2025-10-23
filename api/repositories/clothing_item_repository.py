"""
Clothing Item Repository

Handles database operations for ClothingItem entities.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import ClothingItem
from api.logging_config import get_logger

logger = get_logger(__name__)


class ClothingItemRepository:
    """Repository for ClothingItem database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, item_id: str) -> Optional[ClothingItem]:
        """Get clothing item by ID"""
        result = await self.session.execute(
            select(ClothingItem).where(ClothingItem.item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[ClothingItem]:
        """Get all clothing items, optionally filtered with pagination support"""
        query = select(ClothingItem).order_by(ClothingItem.created_at.desc())

        if user_id is not None:
            query = query.where(ClothingItem.user_id == user_id)

        if category:
            query = query.where(ClothingItem.category == category)

        # Exclude archived by default
        if not include_archived:
            query = query.where(ClothingItem.archived == False)

        if limit is not None:
            query = query.limit(limit)

        query = query.offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_category(self, category: str, user_id: Optional[int] = None) -> List[ClothingItem]:
        """Get all items in a specific category"""
        return await self.get_all(user_id=user_id, category=category)

    async def create(self, item: ClothingItem) -> ClothingItem:
        """Create new clothing item"""
        self.session.add(item)
        await self.session.flush()

        logger.info(f"Created clothing item in database: {item.item} ({item.category})")
        return item

    async def update(self, item: ClothingItem) -> ClothingItem:
        """Update existing clothing item"""
        await self.session.merge(item)
        await self.session.flush()

        logger.info(f"Updated clothing item in database: {item.item} ({item.item_id})")
        return item

    async def delete(self, item_id: str) -> bool:
        """Archive clothing item by ID (soft delete)"""
        return await self.archive(item_id)

    async def archive(self, item_id: str) -> bool:
        """Archive clothing item by ID (soft delete)"""
        item = await self.get_by_id(item_id)

        if not item:
            return False

        item.archived = True
        item.archived_at = datetime.utcnow()
        await self.session.flush()

        logger.info(f"Archived clothing item in database: {item_id}")
        return True

    async def unarchive(self, item_id: str) -> bool:
        """Unarchive clothing item by ID"""
        item = await self.get_by_id(item_id)

        if not item:
            return False

        item.archived = False
        item.archived_at = None
        await self.session.flush()

        logger.info(f"Unarchived clothing item in database: {item_id}")
        return True

    async def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        color: Optional[str] = None,
        user_id: Optional[int] = None,
        include_archived: bool = False
    ) -> List[ClothingItem]:
        """
        Search clothing items with optional filters

        Args:
            query: Text search in item name, fabric, or details
            category: Filter by category
            color: Filter by color
            user_id: Filter by user ID
            include_archived: If True, include archived items. Default False.
        """
        stmt = select(ClothingItem)

        if user_id is not None:
            stmt = stmt.where(ClothingItem.user_id == user_id)

        if category:
            stmt = stmt.where(ClothingItem.category == category)

        if color:
            stmt = stmt.where(ClothingItem.color.ilike(f"%{color}%"))

        # Exclude archived by default
        if not include_archived:
            stmt = stmt.where(ClothingItem.archived == False)

        if query:
            # Case-insensitive search in item, fabric, or details
            search_filter = (
                ClothingItem.item.ilike(f"%{query}%") |
                ClothingItem.fabric.ilike(f"%{query}%") |
                ClothingItem.details.ilike(f"%{query}%")
            )
            stmt = stmt.where(search_filter)

        stmt = stmt.order_by(ClothingItem.created_at.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_without_preview(self, user_id: Optional[int] = None) -> List[ClothingItem]:
        """Get all items without preview images"""
        query = select(ClothingItem).where(
            (ClothingItem.preview_image_path == None) |
            (ClothingItem.preview_image_path == "")
        )

        if user_id is not None:
            query = query.where(ClothingItem.user_id == user_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def exists(self, item_id: str) -> bool:
        """Check if clothing item exists"""
        item = await self.get_by_id(item_id)
        return item is not None

    async def count(self, user_id: Optional[int] = None, category: Optional[str] = None, include_archived: bool = False) -> int:
        """Count clothing items"""
        query = select(func.count()).select_from(ClothingItem)

        if user_id is not None:
            query = query.where(ClothingItem.user_id == user_id)

        if category:
            query = query.where(ClothingItem.category == category)

        # Exclude archived by default
        if not include_archived:
            query = query.where(ClothingItem.archived == False)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_categories(self, user_id: Optional[int] = None) -> List[tuple[str, int]]:
        """Get all categories with item counts"""
        query = select(
            ClothingItem.category,
            func.count(ClothingItem.id)
        ).group_by(ClothingItem.category)

        if user_id is not None:
            query = query.where(ClothingItem.user_id == user_id)

        query = query.order_by(func.count(ClothingItem.id).desc())

        result = await self.session.execute(query)
        return list(result.all())
