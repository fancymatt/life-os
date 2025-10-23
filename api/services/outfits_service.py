"""
Outfits Service

Business logic for managing outfit composition entities.
Outfits are compositions of clothing item IDs.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import uuid

from api.config import settings
from ai_capabilities.specs import OutfitCompositionEntity
from api.logging_config import get_logger

logger = get_logger(__name__)


class OutfitsService:
    """Service for managing outfit composition entities"""

    def __init__(self):
        self.outfits_dir = settings.base_dir / "data" / "outfits"
        self.outfits_dir.mkdir(parents=True, exist_ok=True)

    def list_outfits(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all outfit compositions

        Args:
            limit: Maximum number of outfits to return
            offset: Number of outfits to skip

        Returns:
            List of outfit dicts
        """
        outfits = []

        # Read all outfit files
        for outfit_path in self.outfits_dir.glob("*.json"):
            try:
                with open(outfit_path, 'r') as f:
                    outfit_data = json.load(f)
                    outfits.append(outfit_data)
            except Exception as e:
                logger.warning(f"Failed to load outfit {outfit_path.name}: {e}")
                continue

        # Sort by updated_at (most recently updated first)
        outfits.sort(key=lambda x: x.get('updated_at', x.get('created_at', '')), reverse=True)

        # Apply pagination
        if offset:
            outfits = outfits[offset:]
        if limit:
            outfits = outfits[:limit]

        return outfits

    def get_outfit(self, outfit_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single outfit by ID

        Args:
            outfit_id: UUID of the outfit

        Returns:
            Outfit dict or None if not found
        """
        outfit_path = self.outfits_dir / f"{outfit_id}.json"

        if not outfit_path.exists():
            return None

        try:
            with open(outfit_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load outfit {outfit_id}: {e}")
            return None

    def create_outfit(
        self,
        name: str,
        clothing_item_ids: List[str],
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new outfit composition

        Args:
            name: User-defined outfit name
            clothing_item_ids: List of clothing item IDs that make up this outfit
            notes: Optional notes about the outfit

        Returns:
            Created outfit dict
        """
        # Generate UUID
        outfit_id = str(uuid.uuid4())

        # Create entity
        outfit_entity = OutfitCompositionEntity(
            outfit_id=outfit_id,
            name=name,
            clothing_item_ids=clothing_item_ids,
            notes=notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to file
        outfit_path = self.outfits_dir / f"{outfit_id}.json"
        with open(outfit_path, 'w') as f:
            json.dump(outfit_entity.dict(), f, indent=2, default=str)

        logger.info(f"Created outfit: {name} ({len(clothing_item_ids)} items)")

        return outfit_entity.dict()

    def update_outfit(
        self,
        outfit_id: str,
        name: Optional[str] = None,
        clothing_item_ids: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an outfit composition

        Args:
            outfit_id: UUID of the outfit
            name: Optional new name
            clothing_item_ids: Optional new list of item IDs
            notes: Optional new notes

        Returns:
            Updated outfit dict or None if not found
        """
        # Load existing outfit
        existing_outfit = self.get_outfit(outfit_id)
        if not existing_outfit:
            return None

        # Update fields
        if name is not None:
            existing_outfit['name'] = name
        if clothing_item_ids is not None:
            existing_outfit['clothing_item_ids'] = clothing_item_ids
        if notes is not None:
            existing_outfit['notes'] = notes

        # Update timestamp
        existing_outfit['updated_at'] = datetime.now().isoformat()

        # Save updated outfit
        outfit_path = self.outfits_dir / f"{outfit_id}.json"
        with open(outfit_path, 'w') as f:
            json.dump(existing_outfit, f, indent=2, default=str)

        logger.info(f"Updated outfit: {outfit_id}")

        return existing_outfit

    def delete_outfit(self, outfit_id: str) -> bool:
        """
        Delete an outfit composition

        Args:
            outfit_id: UUID of the outfit

        Returns:
            True if deleted, False if not found
        """
        outfit_path = self.outfits_dir / f"{outfit_id}.json"

        if not outfit_path.exists():
            return False

        outfit_path.unlink()
        logger.info(f"Deleted outfit: {outfit_id}")

        return True

    def add_item_to_outfit(self, outfit_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Add a clothing item to an outfit

        Args:
            outfit_id: UUID of the outfit
            item_id: UUID of the clothing item to add

        Returns:
            Updated outfit dict or None if not found
        """
        outfit = self.get_outfit(outfit_id)
        if not outfit:
            return None

        # Add item if not already in outfit
        if item_id not in outfit['clothing_item_ids']:
            outfit['clothing_item_ids'].append(item_id)
            outfit['updated_at'] = datetime.now().isoformat()

            # Save updated outfit
            outfit_path = self.outfits_dir / f"{outfit_id}.json"
            with open(outfit_path, 'w') as f:
                json.dump(outfit, f, indent=2, default=str)

            logger.info(f"Added item {item_id} to outfit {outfit_id}")

        return outfit

    def remove_item_from_outfit(self, outfit_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Remove a clothing item from an outfit

        Args:
            outfit_id: UUID of the outfit
            item_id: UUID of the clothing item to remove

        Returns:
            Updated outfit dict or None if not found
        """
        outfit = self.get_outfit(outfit_id)
        if not outfit:
            return None

        # Remove item if it exists
        if item_id in outfit['clothing_item_ids']:
            outfit['clothing_item_ids'].remove(item_id)
            outfit['updated_at'] = datetime.now().isoformat()

            # Save updated outfit
            outfit_path = self.outfits_dir / f"{outfit_id}.json"
            with open(outfit_path, 'w') as f:
                json.dump(outfit, f, indent=2, default=str)

            logger.info(f"Removed item {item_id} from outfit {outfit_id}")

        return outfit
