"""
Outfit Service (PostgreSQL)

Business logic for managing outfit composition entities using PostgreSQL.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from api.repositories.outfit_repository import OutfitRepository
from api.models.db import Outfit


class OutfitServiceDB:
    """Service for managing outfit compositions (PostgreSQL-backed)"""

    def __init__(self, session: AsyncSession, user_id: Optional[int] = None):
        self.session = session
        self.user_id = user_id
        self.repository = OutfitRepository(session)

    def _outfit_to_dict(self, outfit: Outfit) -> Dict[str, Any]:
        """Convert Outfit model to dict"""
        return {
            "outfit_id": outfit.outfit_id,
            "name": outfit.name,
            "description": outfit.description,
            "style_genre": outfit.style_genre,
            "formality": outfit.formality,
            "clothing_item_ids": outfit.clothing_item_ids,
            "source_image": outfit.source_image,
            "preview_image_path": outfit.preview_image_path,
            "metadata": outfit.meta,
            "created_at": outfit.created_at.isoformat() if outfit.created_at else None,
            "updated_at": outfit.updated_at.isoformat() if outfit.updated_at else None,
        }

    async def list_outfits(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """List all outfits"""
        outfits = await self.repository.list_all(
            user_id=self.user_id,
            include_archived=include_archived
        )

        # Apply pagination
        if offset:
            outfits = outfits[offset:]
        if limit:
            outfits = outfits[:limit]

        return [self._outfit_to_dict(outfit) for outfit in outfits]

    async def get_outfit(self, outfit_id: str) -> Optional[Dict[str, Any]]:
        """Get outfit by ID"""
        outfit = await self.repository.get_by_id(outfit_id)
        if not outfit:
            return None
        if self.user_id and outfit.user_id != self.user_id:
            return None
        return self._outfit_to_dict(outfit)

    async def create_outfit(self, name: str, clothing_item_ids: List[str],
                           description: Optional[str] = None,
                           style_genre: Optional[str] = None,
                           formality: Optional[str] = None) -> Dict[str, Any]:
        """Create new outfit"""
        outfit_id = str(uuid.uuid4())[:8]

        outfit = Outfit(
            outfit_id=outfit_id,
            name=name,
            description=description,
            style_genre=style_genre,
            formality=formality,
            clothing_item_ids=clothing_item_ids,
            meta={},
            user_id=self.user_id
        )

        outfit = await self.repository.create(outfit)
        await self.session.commit()

        return self._outfit_to_dict(outfit)

    async def update_outfit(self, outfit_id: str, name: Optional[str] = None,
                           clothing_item_ids: Optional[List[str]] = None,
                           description: Optional[str] = None,
                           style_genre: Optional[str] = None,
                           formality: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update outfit"""
        outfit = await self.repository.get_by_id(outfit_id)
        if not outfit:
            return None
        if self.user_id and outfit.user_id != self.user_id:
            return None

        if name is not None:
            outfit.name = name
        if clothing_item_ids is not None:
            outfit.clothing_item_ids = clothing_item_ids
        if description is not None:
            outfit.description = description
        if style_genre is not None:
            outfit.style_genre = style_genre
        if formality is not None:
            outfit.formality = formality

        outfit = await self.repository.update(outfit)
        await self.session.commit()

        return self._outfit_to_dict(outfit)

    async def delete_outfit(self, outfit_id: str) -> bool:
        """Delete outfit"""
        outfit = await self.repository.get_by_id(outfit_id)
        if not outfit:
            return False
        if self.user_id and outfit.user_id != self.user_id:
            return False

        await self.repository.delete(outfit)
        await self.session.commit()
        return True

    async def archive_outfit(self, outfit_id: str) -> bool:
        """Archive outfit (soft delete)"""
        outfit = await self.repository.get_by_id(outfit_id)
        if not outfit:
            return False
        if self.user_id and outfit.user_id != self.user_id:
            return False

        success = await self.repository.archive(outfit_id)
        if success:
            await self.session.commit()
        return success

    async def unarchive_outfit(self, outfit_id: str) -> bool:
        """Unarchive outfit"""
        outfit = await self.repository.get_by_id(outfit_id)
        if not outfit:
            return False
        if self.user_id and outfit.user_id != self.user_id:
            return False

        success = await self.repository.unarchive(outfit_id)
        if success:
            await self.session.commit()
        return success

    async def add_item_to_outfit(self, outfit_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Add item to outfit"""
        outfit = await self.repository.get_by_id(outfit_id)
        if not outfit:
            return None
        if self.user_id and outfit.user_id != self.user_id:
            return None

        if item_id not in outfit.clothing_item_ids:
            outfit.clothing_item_ids.append(item_id)
            outfit = await self.repository.update(outfit)
            await self.session.commit()

        return self._outfit_to_dict(outfit)

    async def remove_item_from_outfit(self, outfit_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Remove item from outfit"""
        outfit = await self.repository.get_by_id(outfit_id)
        if not outfit:
            return None
        if self.user_id and outfit.user_id != self.user_id:
            return None

        if item_id in outfit.clothing_item_ids:
            outfit.clothing_item_ids.remove(item_id)
            outfit = await self.repository.update(outfit)
            await self.session.commit()

        return self._outfit_to_dict(outfit)
