"""
Clothing Items Service

Business logic for managing clothing item entities.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import uuid

from api.config import settings
from ai_capabilities.specs import ClothingItemEntity, ClothingCategory


class ClothingItemsService:
    """Service for managing clothing item entities"""

    def __init__(self):
        self.clothing_items_dir = settings.base_dir / "data" / "clothing_items"
        self.clothing_items_dir.mkdir(parents=True, exist_ok=True)

    def list_clothing_items(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all clothing items, optionally filtered by category

        Args:
            category: Optional category filter (e.g., "tops", "bottoms")
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            List of clothing item dicts
        """
        items = []

        # Read all clothing item files
        for item_path in self.clothing_items_dir.glob("*.json"):
            try:
                with open(item_path, 'r') as f:
                    item_data = json.load(f)

                    # Apply category filter if provided
                    if category and item_data.get('category') != category:
                        continue

                    items.append(item_data)
            except Exception as e:
                print(f"⚠️  Failed to load clothing item {item_path.name}: {e}")
                continue

        # Sort by created_at (newest first)
        items.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Apply pagination
        if offset:
            items = items[offset:]
        if limit:
            items = items[:limit]

        return items

    def get_clothing_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single clothing item by ID

        Args:
            item_id: UUID of the clothing item

        Returns:
            Clothing item dict or None if not found
        """
        item_path = self.clothing_items_dir / f"{item_id}.json"

        if not item_path.exists():
            return None

        try:
            with open(item_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load clothing item {item_id}: {e}")
            return None

    def create_clothing_item(
        self,
        category: str,
        item: str,
        fabric: str,
        color: str,
        details: str,
        source_image: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new clothing item

        Args:
            category: Body zone category
            item: Garment type
            fabric: Material and texture
            color: Color description
            details: Construction details
            source_image: Optional source image path

        Returns:
            Created clothing item dict
        """
        # Generate UUID
        item_id = str(uuid.uuid4())

        # Create entity
        item_entity = ClothingItemEntity(
            item_id=item_id,
            category=ClothingCategory(category),
            item=item,
            fabric=fabric,
            color=color,
            details=details,
            source_image=source_image,
            created_at=datetime.now()
        )

        # Save to file
        item_path = self.clothing_items_dir / f"{item_id}.json"
        with open(item_path, 'w') as f:
            json.dump(item_entity.dict(), f, indent=2, default=str)

        print(f"✅ Created clothing item: {item} ({category})")

        return item_entity.dict()

    def update_clothing_item(
        self,
        item_id: str,
        category: Optional[str] = None,
        item: Optional[str] = None,
        fabric: Optional[str] = None,
        color: Optional[str] = None,
        details: Optional[str] = None,
        source_image: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a clothing item

        Args:
            item_id: UUID of the clothing item
            category: Optional new category
            item: Optional new item type
            fabric: Optional new fabric
            color: Optional new color
            details: Optional new details
            source_image: Optional new source image

        Returns:
            Updated clothing item dict or None if not found
        """
        # Load existing item
        existing_item = self.get_clothing_item(item_id)
        if not existing_item:
            return None

        # Update fields
        if category is not None:
            existing_item['category'] = category
        if item is not None:
            existing_item['item'] = item
        if fabric is not None:
            existing_item['fabric'] = fabric
        if color is not None:
            existing_item['color'] = color
        if details is not None:
            existing_item['details'] = details
        if source_image is not None:
            existing_item['source_image'] = source_image

        # Save updated item
        item_path = self.clothing_items_dir / f"{item_id}.json"
        with open(item_path, 'w') as f:
            json.dump(existing_item, f, indent=2, default=str)

        print(f"✅ Updated clothing item: {item_id}")

        return existing_item

    def delete_clothing_item(self, item_id: str) -> bool:
        """
        Delete a clothing item

        Args:
            item_id: UUID of the clothing item

        Returns:
            True if deleted, False if not found
        """
        item_path = self.clothing_items_dir / f"{item_id}.json"

        if not item_path.exists():
            return False

        item_path.unlink()
        print(f"✅ Deleted clothing item: {item_id}")

        return True

    def get_categories_summary(self) -> Dict[str, int]:
        """
        Get count of items per category

        Returns:
            Dict mapping category name to count
        """
        items = self.list_clothing_items()

        summary = {}
        for item in items:
            category = item.get('category', 'unknown')
            summary[category] = summary.get(category, 0) + 1

        return summary
